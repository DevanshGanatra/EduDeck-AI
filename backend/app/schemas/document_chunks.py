from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.core import DocumentStatus
from app.schemas.project import PaginatedResponse

class DocumentChunkResponse(BaseModel):
    id: UUID
    chunk_index: int
    chunk_text: str
    page_number: Optional[int]
    token_count: int
    is_very_short: int
    is_low_text_density: int
    is_ocr_candidate: int
    
    # Search snippet
    snippet: Optional[str] = None

    class Config:
        from_attributes = True

class DocumentAnalyticsResponse(BaseModel):
    id: UUID
    total_pages: int
    total_characters: int
    total_words: int
    estimated_tokens: int
    total_chunks: int
    average_chunk_size: float
    largest_chunk_size: int
    smallest_chunk_size: int
    reading_time_minutes: int
    language: str
    extraction_method: str
    
    class Config:
        from_attributes = True
        
class DocumentTimelineResponse(BaseModel):
    id: UUID
    uploaded_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    stored_at: Optional[datetime] = None
    extracted_at: Optional[datetime] = None
    chunked_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
