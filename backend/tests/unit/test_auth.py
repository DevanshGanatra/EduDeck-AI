import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone

from app.services.auth import AuthService
from app.schemas.user import UserCreate
from app.models.core import User
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import get_password_hash, create_access_token, decode_access_token

@pytest.fixture
def mock_user_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def auth_service(mock_user_repo):
    return AuthService(user_repo=mock_user_repo)

@pytest.mark.asyncio
async def test_successful_registration(auth_service, mock_user_repo):
    user_data = UserCreate(email="test@example.com", name="Test User", password="Password123")
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = User(id=uuid4(), email=user_data.email, name=user_data.name)
    
    user = await auth_service.register_user(user_data)
    assert user.email == "test@example.com"
    assert user.name == "Test User"

@pytest.mark.asyncio
async def test_duplicate_registration(auth_service, mock_user_repo):
    user_data = UserCreate(email="duplicate@example.com", name="Test User", password="Password123")
    mock_user_repo.get_by_email.return_value = User(id=uuid4(), email=user_data.email)
    
    with pytest.raises(BadRequestException):
        await auth_service.register_user(user_data)

@pytest.mark.asyncio
async def test_successful_login(auth_service, mock_user_repo):
    password = "ValidPassword123"
    hashed = get_password_hash(password)
    user = User(id=uuid4(), email="login@example.com", password_hash=hashed)
    mock_user_repo.get_by_email.return_value = user
    
    token = await auth_service.authenticate_user(email="login@example.com", password=password)
    assert token is not None
    payload = decode_access_token(token)
    assert payload["sub"] == str(user.id)

@pytest.mark.asyncio
async def test_invalid_credentials(auth_service, mock_user_repo):
    mock_user_repo.get_by_email.return_value = None
    with pytest.raises(UnauthorizedException):
        await auth_service.authenticate_user(email="wrong@example.com", password="Password123")

@pytest.mark.asyncio
async def test_jwt_validation():
    user_id = str(uuid4())
    token = create_access_token(subject=user_id)
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload

@pytest.mark.asyncio
async def test_current_user_endpoint(auth_service, mock_user_repo):
    user_id = uuid4()
    mock_user_repo.get_by_id.return_value = User(id=user_id, email="current@example.com")
    
    user = await auth_service.get_current_user(user_id=str(user_id))
    assert user.email == "current@example.com"
