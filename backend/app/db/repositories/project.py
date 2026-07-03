from uuid import UUID
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.core import Project

class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, project_id: UUID, user_id: UUID) -> Optional[Project]:
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.status != "deleted")
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_paginated_for_user(
        self, user_id: UUID, page: int = 1, page_size: int = 20, search_title: Optional[str] = None
    ) -> Tuple[List[Project], int]:
        
        base_stmt = select(Project).where(Project.user_id == user_id, Project.status != "deleted")
        count_stmt = select(func.count(Project.id)).where(Project.user_id == user_id, Project.status != "deleted")
        
        if search_title:
            search_filter = Project.title.ilike(f"%{search_title}%")
            base_stmt = base_stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)
            
        base_stmt = base_stmt.order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        
        items_result = await self.session.execute(base_stmt)
        items = list(items_result.scalars().all())
        
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        return items, total

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def update(self, project: Project) -> Project:
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def soft_delete(self, project: Project) -> None:
        project.status = "deleted"
        await self.session.commit()
