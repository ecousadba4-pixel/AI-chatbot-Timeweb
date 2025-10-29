"""Простейшая заглушка httpx.AsyncClient."""
from __future__ import annotations

from typing import Any, Dict


class Response:
    def __init__(self, status_code: int = 200, json_data: Dict[str, Any] | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text or ""

    def json(self) -> Dict[str, Any]:
        return self._json_data


class AsyncClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        self._response = Response()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN401
        return None

    async def post(self, url: str, json: Dict[str, Any], headers: Dict[str, Any]) -> Response:  # noqa: ANN401
        return self._response


__all__ = ["AsyncClient", "Response"]
