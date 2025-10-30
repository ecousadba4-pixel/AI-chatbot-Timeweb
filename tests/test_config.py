from __future__ import annotations

from typing import Generator

import pytest
from pydantic import ValidationError

from app.core import config


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Generator[None, None, None]:
    """Сбрасывает кэш настроек перед и после тестов."""

    config.get_settings.cache_clear()
    try:
        yield
    finally:
        config.get_settings.cache_clear()


def test_settings_accepts_internal_hostname(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIMEWEB_API_BASE", "http://timeweb-api:8080/api")

    settings = config.get_settings()

    assert settings.timeweb_api_base == "http://timeweb-api:8080/api".rstrip("/")


def test_settings_rejects_invalid_scheme(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIMEWEB_API_BASE", "ftp://timeweb-api")

    with pytest.raises(ValidationError):
        config.get_settings()
