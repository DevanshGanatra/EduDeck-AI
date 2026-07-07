from uuid import UUID
from typing import List, Dict
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
        items, total = await self.chunk_repo.get_paginated_by_document(document_id, page=1, page_size=10000)
        if not items:
            return

        # Pre-set total_chunks so the frontend knows the denominator immediately
        doc = await self.doc_repo.get_by_id_internal(document_id)
        if doc:
            doc.total_chunks = total
            doc.vectorized_chunks = 0
            await self.db.commit()
            
        texts = [chunk.chunk_text for chunk in items]
        
        # Generate embeddings in batches of 50
        batch_size = 50
        embeddings = []
        vectorized_so_far = 0

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Retry loop for rate limits
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = genai.embed_content(
                        model=self.model,
                        content=batch_texts,
                        task_type="retrieval_document",
                        output_dimensionality=768
                    )
                    embeddings.extend(response['embedding'])
                    break
                except Exception as e:
                    if '429' in str(e) or isinstance(e, ResourceExhausted):
                        if attempt < max_retries - 1:
                            wait = 30 * (attempt + 1)
                            print(f"Rate limited. Sleeping {wait}s. Attempt {attempt+1}/{max_retries}")
                            time.sleep(wait)
                        else:
                            raise e
                    else:
                        raise e

            # Update vectorized_chunks progress after each batch
            vectorized_so_far += len(batch_texts)
            doc = await self.doc_repo.get_by_id_internal(document_id)
            if doc:
                doc.vectorized_chunks = vectorized_so_far
                await self.db.commit()

        # Store the embeddings in PG
        for i, chunk in enumerate(items):
            chunk.embedding_provider = "gemini"
            chunk.embedding_model = self.model
            chunk.vector_reference = str(chunk.id)
            chunk.vector_store = "pgvector"
            chunk.vector_dimension = len(embeddings[i])
            chunk.embedding = embeddings[i]
            
        await self.db.commit()
