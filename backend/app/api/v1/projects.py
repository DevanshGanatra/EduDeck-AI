from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectDashboardResponse, PaginatedResponse
from app.schemas.base import StandardResponse, success_response
from app.services.project import ProjectService
from app.api.deps import get_project_service, get_current_user
from app.models.core import User

router = APIRouter()

@router.post("", response_model=StandardResponse[ProjectDashboardResponse], status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    project = await project_service.create_project(project_in, current_user)
    # Quick fix: fetch dashboard response immediately
    dashboard_project = await project_service.get_project(project.id, current_user)
    return success_response(data=dashboard_project, message="Project created successfully")

@router.get("", response_model=StandardResponse[PaginatedResponse[ProjectDashboardResponse]])
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search projects by title"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    projects_paginated = await project_service.get_projects(
        current_user=current_user, page=page, page_size=page_size, search_title=search
    )
    return success_response(data=projects_paginated, message="Projects retrieved successfully")

@router.get("/{project_id}", response_model=StandardResponse[ProjectDashboardResponse])
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    project = await project_service.get_project(project_id, current_user)
    return success_response(data=project, message="Project retrieved successfully")

@router.patch("/{project_id}", response_model=StandardResponse[ProjectDashboardResponse])
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    project = await project_service.update_project(project_id, project_in, current_user)
    return success_response(data=project, message="Project updated successfully")

@router.post("/{project_id}/archive", response_model=StandardResponse[None])
async def archive_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    await project_service.archive_project(project_id, current_user)
    return success_response(data=None, message="Project archived successfully")

@router.delete("/{project_id}", response_model=StandardResponse[None])
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    await project_service.delete_project(project_id, current_user)
    return success_response(data=None, message="Project deleted successfully")
