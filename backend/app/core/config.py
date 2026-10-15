"""Application settings loaded from environment variables.

All configuration is read via pydantic-settings so that values can come from
a `.env` file or real environment variables. Nothing here is hard-coded.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- App ----
    APP_NAME: str = "FinanceFlow"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"

    # ---- MySQL ----
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "financeflow"
    MYSQL_USER: str = "financeflow"
    MYSQL_PASSWORD: str = "change_me_in_production"
    MYSQL_ROOT_PASSWORD: str = "change_me_root_in_production"

    # ---- SQLAlchemy ----
    DATABASE_URL: str = ""

    # ---- JWT / Auth ----
    JWT_SECRET_KEY: str = Field(
        default="replace_with_a_strong_random_secret_at_least_32_chars_long",
        min_length=16,
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ---- CORS ----
    CORS_ORIGINS: Union[str, List[str]] = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return list(value)

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def _ensure_database_url(cls, value: str, info) -> str:
        if value:
            return value
        data = info.data
        host = data.get("MYSQL_HOST", "127.0.0.1")
        port = data.get("MYSQL_PORT", 3306)
        db = data.get("MYSQL_DATABASE", "financeflow")
        user = data.get("MYSQL_USER", "financeflow")
        password = data.get("MYSQL_PASSWORD", "")
        return (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"
        )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor used as a FastAPI dependency."""
    return Settings()


settings = get_settings()
