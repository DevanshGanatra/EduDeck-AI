from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse, Token
from app.schemas.base import StandardResponse, success_response
from app.services.auth import AuthService
from app.api.deps import get_auth_service, get_current_user
from app.models.core import User

router = APIRouter()

@router.post("/register", response_model=StandardResponse[UserResponse])
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.register_user(user_in)
    return success_response(data=user, message="User registered successfully")

@router.post("/login", response_model=StandardResponse[Token])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    access_token = await auth_service.authenticate_user(email=form_data.username, password=form_data.password)
    token = Token(access_token=access_token, token_type="bearer")
    return success_response(data=token, message="Login successful")

@router.get("/me", response_model=StandardResponse[UserResponse])
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return success_response(data=current_user, message="Current user retrieved successfully")
