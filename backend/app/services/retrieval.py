from uuid import UUID
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.vectorization import VectorizationService
from app.models.core import DocumentChunk, Document
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
        
        # 2. Query Postgres directly using pgvector cosine_distance
        stmt = (
            select(DocumentChunk, DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"))
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.project_id == project_id)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        # 3. Format Output
        final_results = []
        for chunk, distance in rows:
            # pgvector cosine_distance returns distance, convert to similarity
            similarity = max(0.0, 1.0 - distance)
            
            final_results.append({
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "page_number": chunk.page_number,
                "text": chunk.chunk_text,
                "similarity_score": round(similarity, 4)
            })
                
        return final_results
