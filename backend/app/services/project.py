from uuid import UUID
from typing import List, Optional, Tuple
from datetime import datetime
from app.db.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectDashboardResponse, PaginatedResponse
from app.models.core import Project, User
from app.core.exceptions import NotFoundException

class ProjectService:
    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    async def create_project(self, project_in: ProjectCreate, current_user: User) -> Project:
        project = Project(
            title=project_in.title,
            description=project_in.description,
            user_id=current_user.id,
            default_language=project_in.default_language,
            default_audience=project_in.default_audience,
            default_style=project_in.default_style,
            default_template_id=project_in.default_template_id,
            default_slide_count=project_in.default_slide_count,
            default_duration_minutes=project_in.default_duration_minutes
        )
        return await self.project_repo.create(project)

    async def get_projects(
        self, current_user: User, page: int = 1, page_size: int = 20, search_title: Optional[str] = None
    ) -> PaginatedResponse[ProjectDashboardResponse]:
        
        items, total = await self.project_repo.get_paginated_for_user(
            user_id=current_user.id, page=page, page_size=page_size, search_title=search_title
        )
        
        dashboard_items = []
        for p in items:
            # MVP Placeholders for dashboard metrics
            resp = ProjectDashboardResponse.model_validate(p)
            resp.last_activity = p.updated_at
            dashboard_items.append(resp)
            
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        return PaginatedResponse[ProjectDashboardResponse](
            items=dashboard_items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages
        )

    async def get_project(self, project_id: UUID, current_user: User) -> ProjectDashboardResponse:
        project = await self.project_repo.get_by_id(project_id=project_id, user_id=current_user.id)
        if not project:
            raise NotFoundException(message="Project not found or access denied")
            
        resp = ProjectDashboardResponse.model_validate(project)
        resp.last_activity = project.updated_at
        return resp

    async def update_project(self, project_id: UUID, project_in: ProjectUpdate, current_user: User) -> ProjectDashboardResponse:
        project = await self.project_repo.get_by_id(project_id=project_id, user_id=current_user.id)
        if not project:
            raise NotFoundException(message="Project not found or access denied")
        
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
            
        updated_project = await self.project_repo.update(project)
        return await self.get_project(updated_project.id, current_user)

    async def archive_project(self, project_id: UUID, current_user: User) -> None:
        project = await self.project_repo.get_by_id(project_id=project_id, user_id=current_user.id)
        if not project:
            raise NotFoundException(message="Project not found or access denied")
        
        project.status = "archived"
        await self.project_repo.update(project)

    async def delete_project(self, project_id: UUID, current_user: User) -> None:
        project = await self.project_repo.get_by_id(project_id=project_id, user_id=current_user.id)
        if not project:
            raise NotFoundException(message="Project not found or access denied")
            
        await self.project_repo.soft_delete(project)
