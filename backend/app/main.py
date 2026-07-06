from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import GlobalExceptionMiddleware
from app.api.v1.router import api_router
from app.db.session import engine
from app.models.core import Base
import app.models # Ensure SQLAlchemy loads all relationships

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup (especially helpful on cloud setups)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="EduDeck AI Platform API",
        lifespan=lifespan
    )

    # Add Middlewares
    origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GlobalExceptionMiddleware)

    # Mount static files for PPTX downloads
    os.makedirs("public/downloads", exist_ok=True)
    app.mount("/downloads", StaticFiles(directory="public/downloads"), name="downloads")

    # Include API Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

app = create_app()

