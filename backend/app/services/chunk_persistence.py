from typing import List, Dict
from uuid import UUID
from app.db.repositories.document import DocumentChunkRepository
from app.models.core import DocumentChunk

class ChunkPersistenceService:
    def __init__(self, chunk_repo: DocumentChunkRepository):
        self.chunk_repo = chunk_repo

    async def persist_chunks(self, document_id: UUID, chunks_data: List[Dict[str, any]]) -> None:
        chunks_to_insert = []
        for c in chunks_data:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=c["chunk_index"],
                chunk_text=c["text"],
                page_number=c["page_number"],
                token_count=c["token_count"],
                heading=c["heading"],
                section=c["section"],
                chapter=c["chapter"]
            )
            chunks_to_insert.append(chunk)
            
        await self.chunk_repo.create_bulk(chunks_to_insert)
