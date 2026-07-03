from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.core import DocumentStatus

class DocumentBase(BaseModel):
    filename: str

class DocumentCreate(DocumentBase):
    project_id: UUID
    checksum: str

class DocumentResponse(DocumentBase):
    id: UUID
    project_id: UUID
    status: DocumentStatus
    checksum: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_duration_ms: Optional[int] = None
    total_pages: int
    total_characters: int
    total_chunks: int
    average_chunk_size: float
    
    failed_stage: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentProgressResponse(BaseModel):
    id: UUID
    status: DocumentStatus
    total_pages: int
    total_chunks: int
    failed_stage: Optional[str] = None
    error_message: Optional[str] = None
