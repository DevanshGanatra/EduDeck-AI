from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from app.schemas.document import DocumentResponse, DocumentProgressResponse
from app.schemas.base import StandardResponse, success_response
from app.models.core import User
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.document import DocumentRepository
from app.services.storage import LocalStorageService
from app.services.document_parser import DocumentParser, PyPDFExtractionStrategy
from app.services.text_chunker import TextChunker, RecursiveCharacterChunker
from app.services.chunk_persistence import ChunkPersistenceService
from app.services.task_dispatcher import FastAPITaskDispatcher
from app.services.document import DocumentService

router = APIRouter()

def get_document_service(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> DocumentService:
    # Manual DI for this complex setup
    return DocumentService(
        document_repo=DocumentRepository(db),
        storage_service=LocalStorageService(),
        document_parser=DocumentParser(strategy=PyPDFExtractionStrategy()),
        text_chunker=TextChunker(strategy=RecursiveCharacterChunker()),
        chunk_persistence=None, # Injected manually inside the background task for async safety
        task_dispatcher=FastAPITaskDispatcher(background_tasks)
    )

@router.post("/upload", response_model=StandardResponse[DocumentResponse])
async def upload_document(
    project_id: UUID = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service)
):
    doc = await doc_service.upload_and_process(
        file_stream=file.file,
        filename=file.filename,
        project_id=project_id,
        current_user=current_user
    )
    return success_response(data=doc, message="Document uploaded and processing started")

@router.get("/{document_id}/progress", response_model=StandardResponse[DocumentProgressResponse])
async def get_document_progress(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service)
):
    doc = await doc_service.get_document_status(document_id)
    return success_response(data=doc, message="Progress retrieved")

from app.db.repositories.document_chunk import DocumentChunkRepository
from app.schemas.document_chunks import DocumentChunkResponse, DocumentAnalyticsResponse, DocumentTimelineResponse
from app.schemas.project import PaginatedResponse
from sqlalchemy.future import select
from app.models.core import Document
from typing import List

@router.get("/project/{project_id}", response_model=StandardResponse[List[DocumentResponse]])
async def list_documents(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # MVP: assuming internal access check
    docs = await db.execute(select(Document).where(Document.project_id == project_id))
    return success_response(data=list(docs.scalars().all()), message="Documents retrieved")

@router.get("/{document_id}/chunks", response_model=StandardResponse[PaginatedResponse[DocumentChunkResponse]])
async def get_document_chunks(
    document_id: UUID,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = DocumentChunkRepository(db)
    items, total = await repo.get_paginated_by_document(document_id, page, page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    paginated = PaginatedResponse(
        items=[DocumentChunkResponse.model_validate(i) for i in items],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )
    return success_response(data=paginated, message="Chunks retrieved")

@router.get("/{document_id}/chunks/search", response_model=StandardResponse[List[DocumentChunkResponse]])
async def search_document_chunks(
    document_id: UUID,
    q: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = DocumentChunkRepository(db)
    chunks = await repo.search_chunks(document_id, q)
    # Highlight snippet logic (MVP placeholder: just return chunk_text or prefix)
    resp = []
    for c in chunks:
        cr = DocumentChunkResponse.model_validate(c)
        idx = c.chunk_text.lower().find(q.lower())
        if idx != -1:
            start = max(0, idx - 30)
            end = min(len(c.chunk_text), idx + len(q) + 30)
            cr.snippet = "..." + c.chunk_text[start:end] + "..."
        resp.append(cr)
        
    return success_response(data=resp, message="Search results")

@router.get("/{document_id}/analytics", response_model=StandardResponse[DocumentAnalyticsResponse])
async def get_document_analytics(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc = await DocumentRepository(db).get_by_id_internal(document_id)
    return success_response(data=DocumentAnalyticsResponse.model_validate(doc), message="Analytics retrieved")

@router.get("/{document_id}/timeline", response_model=StandardResponse[DocumentTimelineResponse])
async def get_document_timeline(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc = await DocumentRepository(db).get_by_id_internal(document_id)
    return success_response(data=DocumentTimelineResponse.model_validate(doc), message="Timeline retrieved")
