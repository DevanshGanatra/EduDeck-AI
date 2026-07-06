from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduDeck AI"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/edudeck"
    
    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        # Ensure it works with asyncpg driver for SQLAlchemy
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
        
    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # ChromaDB Configuration
    CHROMA_HOST: Optional[str] = None
    CHROMA_PORT: Optional[int] = 8000
    CHROMA_PERSIST_DIR: str = "data/chroma"
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_SECRET_KEY"
    SECRET_KEY: str = "secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # AI Providers (Extracted for architecture compliance)
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    PRIMARY_LLM_MODEL: str = "gpt-4o"
    PRIMARY_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Storage
    STORAGE_LOCAL_DIR: str = "storage/"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

