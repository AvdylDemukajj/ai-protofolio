import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://invoice_user:SecurePass123!@localhost:5432/invoice_db"
    OPENAI_API_KEY: str = ""
    ENVIRONMENT: str = "development"
    UPLOAD_DIR: str = "./uploads"
    CONFIDENCE_THRESHOLD: float = 0.85

    class Config:
        env_file = ".env"

settings = Settings()