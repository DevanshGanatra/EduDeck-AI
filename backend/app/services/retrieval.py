from uuid import UUID
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.vectorization import VectorizationService
from app.models.core import DocumentChunk
from sqlalchemy.future import select

class RetrievalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_service = VectorizationService(db)

    async def retrieve(self, query: str, project_id: UUID, top_k: int = 5) -> List[Dict[str, Any]]:
        # 1. Embed query
        response = await self.vector_service.openai_client.embeddings.create(
            input=[query], model=self.vector_service.model
        )
        query_embedding = response.data[0].embedding
        
        # 2. Query ChromaDB with project isolation
        chroma_results = self.vector_service.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"project_id": str(project_id)}
        )
        
        if not chroma_results["ids"] or not chroma_results["ids"][0]:
            return []
            
        chunk_ids = chroma_results["ids"][0]
        distances = chroma_results["distances"][0]
        
        # 3. Fetch full chunks from Postgres for provenance
        stmt = select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        result = await self.db.execute(stmt)
        chunks = {str(c.id): c for c in result.scalars().all()}
        
        # 4. Format Output
        final_results = []
        for cid, distance in zip(chunk_ids, distances):
            if cid in chunks:
                chunk = chunks[cid]
                # Chroma uses L2 distance by default. Convert to a similarity score (approximate)
                similarity = max(0.0, 1.0 - (distance / 2.0))
                
                final_results.append({
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "page_number": chunk.page_number,
                    "text": chunk.chunk_text,
                    "similarity_score": round(similarity, 4)
                })
                
        return final_results
