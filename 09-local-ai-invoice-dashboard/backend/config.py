import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://invoice_user:SecurePass123!@localhost:5432/invoice_db"
    OLLAMA_HOST: str = "http://ollama:11434"
    USE_LOCAL_LLM: bool = True
    OPENAI_API_KEY: str = ""
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    UPLOAD_DIR: str = "/app/uploads"

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)