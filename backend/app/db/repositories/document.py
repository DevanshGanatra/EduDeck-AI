from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.core import Document, DocumentChunk

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, document_id: UUID, project_id: UUID) -> Optional[Document]:
        stmt = select(Document).where(Document.id == document_id, Document.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
        
    async def get_by_id_internal(self, document_id: UUID) -> Optional[Document]:
        """Internal use only, does not check project access"""
        stmt = select(Document).where(Document.id == document_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def update(self, document: Document) -> Document:
        await self.session.commit()
        await self.session.refresh(document)
        return document

class DocumentChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bulk(self, chunks: List[DocumentChunk]) -> None:
        self.session.add_all(chunks)
        await self.session.commit()
