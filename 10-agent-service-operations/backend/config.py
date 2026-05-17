import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://ops_user:SecurePass123!@localhost:5432/ops_db"
    OPENAI_API_KEY: str = ""
    ALLOW_DESTRUCTIVE_ACTIONS: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()