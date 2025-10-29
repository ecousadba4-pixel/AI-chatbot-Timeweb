"""Простейшая заглушка CORS middleware."""
from __future__ import annotations

from typing import Any


class CORSMiddleware:  # noqa: D401
    """Хранит параметры, но не выполняет реальной логики."""

    def __init__(
        self,
        app: Any,
        allow_origins: list[str] | None = None,
        allow_credentials: bool = False,
        allow_methods: list[str] | None = None,
        allow_headers: list[str] | None = None,
    ) -> None:
        self.app = app
        self.allow_origins = allow_origins or ["*"]
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
