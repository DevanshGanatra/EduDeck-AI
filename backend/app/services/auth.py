from uuid import UUID
from app.db.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.models.core import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import BadRequestException, UnauthorizedException

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_in: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise BadRequestException(message="User with this email already exists.")
        
        user = User(
            email=user_in.email,
            name=user_in.name,
            password_hash=get_password_hash(user_in.password)
        )
        return await self.user_repo.create(user)

    async def authenticate_user(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedException(message="Incorrect email or password")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedException(message="Incorrect email or password")
        
        return create_access_token(subject=user.id)

    async def get_current_user(self, user_id: UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException(message="User not found")
        return user
