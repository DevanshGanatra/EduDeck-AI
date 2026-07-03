from fastapi import FastAPI
from app.core.config import settings
from app.core.middleware import GlobalExceptionMiddleware
from app.api.v1.router import api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="EduDeck AI Platform API"
    )

    # Add Middlewares
    app.add_middleware(GlobalExceptionMiddleware)

    # Include API Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

app = create_app()
