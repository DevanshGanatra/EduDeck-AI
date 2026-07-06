import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime

from app.services.project import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.core import Project, User
from app.core.exceptions import NotFoundException

@pytest.fixture
def mock_project_repo():
    return AsyncMock()

@pytest.fixture
def project_service(mock_project_repo):
    return ProjectService(project_repo=mock_project_repo)

@pytest.fixture
def current_user():
    return User(id=uuid4(), email="test@example.com")

@pytest.mark.asyncio
async def test_create_project(project_service, mock_project_repo, current_user):
    project_in = ProjectCreate(title="New Project", description="Desc")
    mock_project_repo.create.return_value = Project(id=uuid4(), title=project_in.title, user_id=current_user.id, status="active", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    
    project = await project_service.create_project(project_in, current_user)
    assert project.title == "New Project"
    assert project.user_id == current_user.id
    mock_project_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_get_project_success(project_service, mock_project_repo, current_user):
    project_id = uuid4()
    mock_project_repo.get_by_id.return_value = Project(id=project_id, title="Test", user_id=current_user.id, status="active", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    
    project = await project_service.get_project(project_id, current_user)
    assert project.id == project_id
    assert project.user_id == current_user.id

@pytest.mark.asyncio
async def test_get_project_not_found(project_service, mock_project_repo, current_user):
    project_id = uuid4()
    mock_project_repo.get_by_id.return_value = None
    
    with pytest.raises(NotFoundException):
        await project_service.get_project(project_id, current_user)

@pytest.mark.asyncio
async def test_update_project(project_service, mock_project_repo, current_user):
    project_id = uuid4()
    existing_project = Project(id=project_id, title="Old Title", user_id=current_user.id, status="active", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    mock_project_repo.get_by_id.return_value = existing_project
    
    # We must return an updated project with the new title
    updated_project = Project(id=project_id, title="New Title", user_id=current_user.id, status="active", created_at=existing_project.created_at, updated_at=datetime.utcnow())
    mock_project_repo.update.return_value = updated_project
    
    update_data = ProjectUpdate(title="New Title")
    project = await project_service.update_project(project_id, update_data, current_user)
    
    # Wait, the project service fetches the project again using get_project.
    # So we need to ensure get_by_id returns the updated project on the second call.
    mock_project_repo.get_by_id.side_effect = [existing_project, updated_project]
    
    assert project.title == "New Title"
    mock_project_repo.update.assert_called_once()

@pytest.mark.asyncio
async def test_delete_project(project_service, mock_project_repo, current_user):
    project_id = uuid4()
    existing_project = Project(id=project_id, title="Test", user_id=current_user.id, status="active", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    mock_project_repo.get_by_id.return_value = existing_project
    
    await project_service.delete_project(project_id, current_user)
    mock_project_repo.soft_delete.assert_called_once_with(existing_project)
