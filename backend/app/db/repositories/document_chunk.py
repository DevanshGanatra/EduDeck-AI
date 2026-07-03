from uuid import UUID
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.core import Document, DocumentChunk
from app.services.search_strategy import SearchStrategy, ILIKESearchStrategy

class DocumentChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bulk(self, chunks: List[DocumentChunk]) -> None:
        self.session.add_all(chunks)
        await self.session.commit()
        
    async def get_paginated_by_document(self, document_id: UUID, page: int = 1, page_size: int = 20) -> Tuple[List[DocumentChunk], int]:
        base_stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        count_stmt = select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == document_id)
        
        base_stmt = base_stmt.order_by(DocumentChunk.chunk_index).offset((page - 1) * page_size).limit(page_size)
        
        items_result = await self.session.execute(base_stmt)
        items = list(items_result.scalars().all())
        
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        return items, total
        
    async def search_chunks(self, document_id: UUID, query: str, strategy: SearchStrategy = None) -> List[DocumentChunk]:
        if strategy is None:
            strategy = ILIKESearchStrategy()
        return await strategy.search(self.session, document_id, query)
