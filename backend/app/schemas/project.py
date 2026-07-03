from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from enum import Enum

T = TypeVar("T")

class ProjectStatusEnum(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    default_language: Optional[str] = None
    default_audience: Optional[str] = None
    default_style: Optional[str] = None
    default_template_id: Optional[UUID] = None
    default_slide_count: Optional[int] = None
    default_duration_minutes: Optional[int] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatusEnum] = None
    default_language: Optional[str] = None
    default_audience: Optional[str] = None
    default_style: Optional[str] = None
    default_template_id: Optional[UUID] = None
    default_slide_count: Optional[int] = None
    default_duration_minutes: Optional[int] = None

class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    status: ProjectStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectDashboardResponse(ProjectResponse):
    # Dashboard Placeholder Summary
    total_documents: int = 0
    ready_documents: int = 0
    processing_documents: int = 0
    total_presentations: int = 0
    total_generation_jobs: int = 0
    last_activity: Optional[datetime] = None
    storage_used_bytes: int = 0

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int
    page_size: int
    total: int
    total_pages: int
