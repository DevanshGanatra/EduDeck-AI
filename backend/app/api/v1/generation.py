from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends, BackgroundTasks
from app.schemas.base import StandardResponse, success_response
from app.models.core import User, Presentation
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.generation import GenerationService

import uuid
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings
from app.models.ai import GenerationJob, JobStatus

router = APIRouter()

class GenerationRequest(BaseModel):
    project_id: UUID
    prompt: str

class GenerationResponse(BaseModel):
    job_id: UUID

class GenerationStatusResponse(BaseModel):
    status: str
    download_url: str | None = None
    error_message: str | None = None

@router.post("/generate", response_model=StandardResponse[GenerationResponse])
async def generate_presentation(
    req: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Create a PENDING job
    job_id = uuid.uuid4()
    job = GenerationJob(id=job_id, project_id=req.project_id, status=JobStatus.PENDING)
    db.add(job)
    await db.commit()
    
    # 2. Try to Enqueue the ARQ task, fallback to BackgroundTasks
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        
        # Redis is available, use ARQ
        redis_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
        await redis_pool.enqueue_job("generate_pptx_task", str(req.project_id), req.prompt, str(job_id))
        print("Enqueued generation task to ARQ Redis Queue.")
    except Exception as e:
        print(f"Redis not available ({e}). Falling back to FastAPI BackgroundTasks.")
        # Redis is down (e.g. local dev without Docker), use BackgroundTasks
        from worker import generate_pptx_task
        background_tasks.add_task(generate_pptx_task, None, str(req.project_id), req.prompt, str(job_id))
    
    return success_response(
        data=GenerationResponse(job_id=job_id),
        message="Presentation generation started"
    )

@router.get("/generate/status/{job_id}", response_model=StandardResponse[GenerationStatusResponse])
async def get_generation_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.future import select
    
    # Get Job
    job_res = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
    job = job_res.scalars().first()
    
    if not job:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(message="Job not found")
        
    download_url = None
    if job.status == JobStatus.COMPLETED:
        # Get associated Presentation to find URL
        pres_res = await db.execute(select(Presentation).where(Presentation.job_id == job_id))
        pres = pres_res.scalars().first()
        if pres:
            download_url = pres.file_url
            
    return success_response(
        data=GenerationStatusResponse(
            status=job.status.value,
            download_url=download_url,
            error_message=job.error_message
        ),
        message="Job status retrieved"
    )
