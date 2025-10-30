"""Упрощённая заглушка httpx для unit-тестов."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping


@dataclass
class Request:
    method: str
    url: str


class HTTPError(Exception):
    """Базовая ошибка HTTPX."""


class HTTPStatusError(HTTPError):
    """Исключение при HTTP-ответе с ошибочным статусом."""

    def __init__(self, message: str, *, request: Request, response: Response) -> None:  # type: ignore[name-defined]
        super().__init__(message)
        self.request = request
        self.response = response


@dataclass
class Timeout:
    """Имитация объекта таймаута httpx.Timeout."""

    read: float

    def __init__(self, timeout: float) -> None:
        self.read = timeout


class Response:
    def __init__(self, status_code: int = 200, json_data: Mapping[str, Any] | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._json_data = dict(json_data or {})
        self.text = text

    def json(self) -> Dict[str, Any]:
        return dict(self._json_data)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPStatusError(
                f"HTTP {self.status_code}",
                request=Request("POST", ""),
                response=self,
            )


class AsyncClient:
    def __init__(
        self,
        base_url: str | None = None,
        headers: MutableMapping[str, str] | None = None,
        timeout: Timeout | float | None = None,
    ) -> None:
        self.base_url = base_url
        self.headers: MutableMapping[str, str] = dict(headers or {})
        self.timeout = timeout
        self._response = Response()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001, D401 - интерфейс контекстного менеджера
        return None

    async def post(self, url: str, json: Dict[str, Any]) -> Response:  # noqa: ANN401 - совместимость с настоящим httpx
        return self._response


__all__ = [
    "AsyncClient",
    "HTTPError",
    "HTTPStatusError",
    "Request",
    "Response",
    "Timeout",
]
