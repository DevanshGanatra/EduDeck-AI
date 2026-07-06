from uuid import UUID
from typing import List, Dict
from openai import AsyncOpenAI
from app.core.config import settings
from app.db.repositories.document_chunk import DocumentChunkRepository
from app.db.repositories.document import DocumentRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.core import DocumentChunk

class VectorizationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chunk_repo = DocumentChunkRepository(db)
        self.doc_repo = DocumentRepository(db)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"

    async def vectorize_document(self, document_id: UUID, project_id: UUID) -> None:
        # Get chunks
        items, _ = await self.chunk_repo.get_paginated_by_document(document_id, page=1, page_size=10000)
        if not items:
            return
            
        texts = [chunk.chunk_text for chunk in items]
        
        # Generate Embeddings in batch
        response = await self.openai_client.embeddings.create(input=texts, model=self.model)
        embeddings = [data.embedding for data in response.data]
        
        # Update PG Metadata and store pgvector embeddings directly
        for i, chunk in enumerate(items):
            chunk.embedding_provider = "openai"
            chunk.embedding_model = self.model
            chunk.vector_reference = str(chunk.id)
            chunk.vector_store = "pgvector"
            chunk.vector_dimension = len(embeddings[i])
            chunk.embedding = embeddings[i]
            
        await self.db.commit()
