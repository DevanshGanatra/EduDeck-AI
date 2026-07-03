from abc import ABC, abstractmethod
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.core import DocumentChunk

class SearchStrategy(ABC):
    @abstractmethod
    async def search(self, session: AsyncSession, document_id: str, query: str, limit: int = 20) -> List[DocumentChunk]:
        """Returns chunks matching the query for a specific document."""
        pass

class ILIKESearchStrategy(SearchStrategy):
    async def search(self, session: AsyncSession, document_id: str, query: str, limit: int = 20) -> List[DocumentChunk]:
        stmt = select(DocumentChunk).where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.chunk_text.ilike(f"%{query}%")
        ).order_by(DocumentChunk.chunk_index).limit(limit)
        
        result = await session.execute(stmt)
        return list(result.scalars().all())
