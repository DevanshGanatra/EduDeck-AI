from uuid import UUID
from typing import List, Dict
from openai import AsyncOpenAI
from app.core.config import settings
from app.db.repositories.document_chunk import DocumentChunkRepository
from app.db.repositories.document import DocumentRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.core import DocumentChunk

import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

class VectorizationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chunk_repo = DocumentChunkRepository(db)
        self.doc_repo = DocumentRepository(db)
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = "models/gemini-embedding-2"

    async def vectorize_document(self, document_id: UUID, project_id: UUID) -> None:
        # Get chunks
        items, _ = await self.chunk_repo.get_paginated_by_document(document_id, page=1, page_size=10000)
        if not items:
            return
            
        texts = [chunk.chunk_text for chunk in items]
        
        # Generate Embeddings in batch using Gemini
        # Gemini free tier limits to 15 RPM, so we must sleep and retry on 429
        batch_size = 50
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Retry loop for rate limits
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = genai.embed_content(
                        model=self.model,
                        content=batch_texts,
                        task_type="retrieval_document"
                    )
                    embeddings.extend(response['embedding'])
                    break
                except Exception as e:
                    if '429' in str(e) or isinstance(e, ResourceExhausted):
                        if attempt < max_retries - 1:
                            print(f"Rate limited. Sleeping 30s. Attempt {attempt+1}/{max_retries}")
                            time.sleep(30)
                        else:
                            raise e
                    else:
                        raise e
            
        # Update PG Metadata and store pgvector embeddings directly
        for i, chunk in enumerate(items):
            chunk.embedding_provider = "gemini"
            chunk.embedding_model = self.model
            chunk.vector_reference = str(chunk.id)
            chunk.vector_store = "pgvector"
            chunk.vector_dimension = len(embeddings[i])
            chunk.embedding = embeddings[i]
            
        await self.db.commit()
