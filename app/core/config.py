from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурация приложения."""

    app_env: str = Field(default="development", alias="APP_ENV")
    app_port: int = Field(default=8000, alias="APP_PORT")

    timeweb_api_base: AnyHttpUrl = Field(default="https://api.timeweb.cloud", alias="TIMEWEB_API_BASE")
    timeweb_api_token: str = Field(default="dummy-token", alias="TIMEWEB_API_TOKEN")
    timeweb_agent_id: str = Field(default="agent", alias="TIMEWEB_AGENT_ID")
    timeweb_temperature: float = Field(default=0.2, alias="TIMEWEB_TEMPERATURE")
    timeweb_top_p: float = Field(default=0.9, alias="TIMEWEB_TOP_P")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


@lru_cache
def get_settings() -> Settings:
    """Возвращает кэшированный экземпляр настроек."""

    return Settings()
