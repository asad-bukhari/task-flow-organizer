from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Task Management API"
    VERSION: str = "1.0.0"

    # CORS - Production settings
    # In production, set specific origins in .env file
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",   # Next.js dev server
        "http://localhost:8000",   # FastAPI dev server
        "http://localhost:8080",   # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
    ]

    # Security
    ALLOW_CREDENTIALS: bool = True
    CORS_MAX_AGE: int = 600  # 10 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
