import asyncio
from arq.connections import RedisSettings
from app.core.config import settings

async def generate_pptx_task(ctx, project_id: str, prompt: str, job_id: str):
    from app.db.session import async_session_maker
    from app.services.generation import GenerationService
    from uuid import UUID
    
    async with async_session_maker() as db:
        service = GenerationService(db)
        try:
            # We pass job_id so the service doesn't create a new one, but uses this one!
            url = await service.generate_presentation(prompt, UUID(project_id), UUID(job_id))
            return url
        except Exception as e:
            # Mark job as failed
            print(f"Job {job_id} failed: {str(e)}")
            await service.mark_job_failed(UUID(job_id), str(e))
            raise e

async def startup(ctx):
    pass

async def shutdown(ctx):
    pass

redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

class WorkerSettings:
    functions = [generate_pptx_task]
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown
