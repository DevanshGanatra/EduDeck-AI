from typing import AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.db.session import async_session_maker
from app.db.repositories.user import UserRepository
from app.db.repositories.project import ProjectRepository
from app.services.auth import AuthService
from app.services.project import ProjectService
from app.models.core import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session=db)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo=user_repo)

def get_project_repository(db: AsyncSession = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(session=db)

def get_project_service(project_repo: ProjectRepository = Depends(get_project_repository)) -> ProjectService:
    return ProjectService(project_repo=project_repo)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id_str: str = payload.get("sub")
        if user_id_str is None or payload.get("type") != "access":
            raise UnauthorizedException(message="Could not validate credentials")
    except jwt.InvalidTokenError:
        raise UnauthorizedException(message="Could not validate credentials")
    
    return await auth_service.get_current_user(user_id=user_id_str)
