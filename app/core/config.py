from __future__ import annotations

from functools import lru_cache
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения."""

    app_env: str = Field(default="development", alias="APP_ENV")
    app_port: int = Field(default=8000, alias="APP_PORT")

    timeweb_api_base: str = Field(default="https://api.timeweb.cloud", alias="TIMEWEB_API_BASE")
    timeweb_api_token: str = Field(default="dummy-token", alias="TIMEWEB_API_TOKEN")
    timeweb_agent_id: str = Field(default="agent", alias="TIMEWEB_AGENT_ID")
    timeweb_temperature: float = Field(default=0.2, alias="TIMEWEB_TEMPERATURE")
    timeweb_top_p: float = Field(default=0.9, alias="TIMEWEB_TOP_P")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

    @field_validator("timeweb_api_base", mode="after")
    @classmethod
    def _validate_timeweb_api_base(cls, value: str) -> str:
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("TIMEWEB_API_BASE должен использовать схему http или https")

        if not parsed.hostname:
            raise ValueError("TIMEWEB_API_BASE должен содержать хост")

        normalized = value.rstrip("/")

        if not normalized:
            raise ValueError("TIMEWEB_API_BASE не может быть пустым")

        return normalized


@lru_cache
def get_settings() -> Settings:
    """Возвращает кэшированный экземпляр настроек."""

    return Settings()
