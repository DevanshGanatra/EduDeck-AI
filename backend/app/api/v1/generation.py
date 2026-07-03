from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from app.schemas.base import StandardResponse, success_response
from app.models.core import User
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.generation import GenerationService

router = APIRouter()

class GenerationRequest(BaseModel):
    project_id: UUID
    prompt: str

class GenerationResponse(BaseModel):
    download_url: str

@router.post("/generate", response_model=StandardResponse[GenerationResponse])
async def generate_presentation(
    req: GenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    svc = GenerationService(db)
    download_url = await svc.generate_presentation(prompt=req.prompt, project_id=req.project_id)
    
    return success_response(
        data=GenerationResponse(download_url=download_url),
        message="Presentation generated successfully"
    )
