from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:tony@localhost:5432/fastapi_cs"
    
    SECRET_KEY: str = "your-super-secret-key-here_for_secretstuff"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Cleaning System API"
    
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()