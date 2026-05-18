"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql://sales_user:changeme@localhost:5435/sales_db"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    SLACK_WEBHOOK_URL: str | None = None
    API_KEY: str | None = None
    ENVIRONMENT: str = "development"
    MAX_RESEARCH_ITERATIONS: int = 2
    CORS_ORIGINS: str = "http://localhost:8502,http://localhost:8501"

    @property
    def use_mock_llm(self) -> bool:
        if self.ENVIRONMENT == "test":
            return True
        key = self.OPENAI_API_KEY or ""
        return not key or key.startswith("sk-dummy") or key == "sk-fake"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
