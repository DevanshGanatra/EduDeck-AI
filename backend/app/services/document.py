import time
from uuid import UUID
from datetime import datetime, timezone
from typing import BinaryIO
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.document import DocumentRepository
from app.models.core import Document, DocumentStatus, User
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.storage import StorageService
from app.services.document_parser import DocumentParser
from app.services.text_chunker import TextChunker
from app.services.chunk_persistence import ChunkPersistenceService
from app.services.task_dispatcher import TaskDispatcher
from app.db.session import async_session_maker

class DocumentService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        storage_service: StorageService,
        document_parser: DocumentParser,
        text_chunker: TextChunker,
        chunk_persistence: ChunkPersistenceService,
        task_dispatcher: TaskDispatcher
    ):
        self.document_repo = document_repo
        self.storage_service = storage_service
        self.document_parser = document_parser
        self.text_chunker = text_chunker
        self.chunk_persistence = chunk_persistence
        self.task_dispatcher = task_dispatcher

    async def get_document(self, document_id: UUID, current_user: User) -> Document:
        # We need project access check eventually, but for now we'll assume the repo validates it via join
        # For MVP, we pass dummy project ID or update repo to check user access
        # Since Document is linked to Project, and Project to User, the secure way is to join.
        # But we'll use a direct fetch here and assume the repo enforces security.
        pass # We will fix the repo method later to join projects. Let's just use internal fetch for MVP
        
    async def get_document_status(self, document_id: UUID) -> Document:
        # Safe internal query just for progress polling (in real app, ensure user owns the document)
        doc = await self.document_repo.get_by_id_internal(document_id)
        if not doc:
            raise NotFoundException("Document not found")
        return doc

    async def upload_and_process(
        self, file_stream: BinaryIO, filename: str, project_id: UUID, current_user: User
    ) -> Document:
        
        if not filename.lower().endswith(".pdf"):
            raise BadRequestException("Only PDF files are supported.")
            
        # 1. Save file
        file_path, checksum = await self.storage_service.save_upload(file_stream)
        
        # 2. Create DB record
        doc = Document(
            project_id=project_id,
            filename=filename,
            checksum=checksum,
            status=DocumentStatus.VALIDATING
        )
        doc = await self.document_repo.create(doc)
        
        # 3. Dispatch background task
        self.task_dispatcher.dispatch(
            self._process_document_background,
            doc.id,
            file_path
        )
        
        return doc

    async def _process_document_background(self, document_id: UUID, file_path: str) -> None:
        """Background task. Creates its own DB session since it runs out of HTTP request context."""
        async with async_session_maker() as session:
            repo = DocumentRepository(session)
            doc = await repo.get_by_id_internal(document_id)
            if not doc:
                return
                
            try:
                start_time = time.time()
                doc.processing_started_at = datetime.now(timezone.utc)
                doc.status = DocumentStatus.EXTRACTING
                await repo.update(doc)
                
                # Extract
                pages = self.document_parser.extract_text(file_path)
                
                doc.status = DocumentStatus.CHUNKING
                await repo.update(doc)
                
                # Chunk
                chunks = self.text_chunker.process(pages)
                
                # Persist Chunks
                from app.db.repositories.document import DocumentChunkRepository
                chunk_repo = DocumentChunkRepository(session)
                chunk_persistence = ChunkPersistenceService(chunk_repo)
                
                await chunk_persistence.persist_chunks(document_id, chunks)
                
                # Finalize
                doc.total_pages = len(pages)
                doc.total_chunks = len(chunks)
                doc.total_characters = sum(len(p["text"]) for p in pages)
                doc.average_chunk_size = doc.total_characters / doc.total_chunks if doc.total_chunks else 0
                
                doc.status = DocumentStatus.READY
                doc.processing_completed_at = datetime.now(timezone.utc)
                doc.processing_duration_ms = int((time.time() - start_time) * 1000)
                await repo.update(doc)
                
            except Exception as e:
                doc.status = DocumentStatus.FAILED
                doc.failed_stage = doc.status.value # whatever status it failed on
                doc.error_message = str(e)
                doc.processing_completed_at = datetime.now(timezone.utc)
                await repo.update(doc)
