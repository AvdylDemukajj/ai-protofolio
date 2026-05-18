"""Application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://rag_user:changeme@localhost:5436/rag_db"
    OPENAI_API_KEY: str | None = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o-mini"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    API_KEY: str | None = None

    @property
    def use_mock_llm(self) -> bool:
        if self.ENVIRONMENT == "test":
            return True
        key = self.OPENAI_API_KEY or ""
        return not key or key.startswith("sk-dummy")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
