from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import GlobalExceptionMiddleware
from app.api.v1.router import api_router

from fastapi.middleware.cors import CORSMiddleware
import app.models # Ensure SQLAlchemy loads all relationships
from fastapi.staticfiles import StaticFiles
import os

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="EduDeck AI Platform API"
    )

    # Add Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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
