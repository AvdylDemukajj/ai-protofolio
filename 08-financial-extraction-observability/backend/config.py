import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    DB_URL: str = "postgresql://user:pass@localhost/db"
    
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadminpassword"
    MINIO_BUCKET: str = "financial-docs"
    
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 5
    
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()