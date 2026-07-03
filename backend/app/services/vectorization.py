from uuid import UUID
from typing import List, Dict
import chromadb
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
        self.chroma_client = chromadb.PersistentClient(path="./chroma_data/")
        self.collection = self.chroma_client.get_or_create_collection(name="edudeck_chunks")
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"

    async def vectorize_document(self, document_id: UUID, project_id: UUID) -> None:
        # Delete existing in Chroma to support re-indexing
        self.collection.delete(where={"document_id": str(document_id)})
        
        # Get chunks
        items, _ = await self.chunk_repo.get_paginated_by_document(document_id, page=1, page_size=10000)
        if not items:
            return
            
        texts = [chunk.chunk_text for chunk in items]
        ids = [str(chunk.id) for chunk in items]
        metadatas = [{"document_id": str(document_id), "project_id": str(project_id)} for _ in items]
        
        # Generate Embeddings in batch
        response = await self.openai_client.embeddings.create(input=texts, model=self.model)
        embeddings = [data.embedding for data in response.data]
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        # Update PG Metadata
        for chunk in items:
            chunk.embedding_provider = "openai"
            chunk.embedding_model = self.model
            chunk.vector_reference = str(chunk.id)
            chunk.vector_store = "chromadb"
            
        await self.db.commit()
