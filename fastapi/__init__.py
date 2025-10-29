"""Упрощённая реализация FastAPI для офлайн-тестов."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple


Handler = Callable[..., Any]


class HTTPException(Exception):
    """Исключение, имитирующее fastapi.HTTPException."""

    def __init__(self, status_code: int, detail: Any | None = None) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass(frozen=True)
class Depends:
    """Заглушка fastapi.Depends.

    Хранит ссылку на функцию-зависимость, чтобы сигнатура обработчика
    оставалась совместимой с оригинальной библиотекой.
    """

    dependency: Callable[..., Any] | None = None


class _Route:
    def __init__(self, path: str, methods: Sequence[str], endpoint: Handler) -> None:
        self.path = path
        self.methods = tuple(methods)
        self.endpoint = endpoint


class APIRouter:
    """Простейший роутер, копящий описания маршрутов."""

    def __init__(self) -> None:
        self._routes: List[_Route] = []

    @property
    def routes(self) -> Iterable[_Route]:
        return tuple(self._routes)

    def add_api_route(self, path: str, endpoint: Handler, methods: Sequence[str]) -> None:
        self._routes.append(_Route(path, methods, endpoint))

    def get(self, path: str, **_: Any) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self.add_api_route(path, func, ["GET"])
            return func

        return decorator

    def post(self, path: str, **_: Any) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self.add_api_route(path, func, ["POST"])
            return func

        return decorator


class FastAPI:
    """Минимальное приложение, поддерживающее регистрацию маршрутов."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401, ANN401
        self._routes: Dict[Tuple[str, str], Handler] = {}

    def add_api_route(self, path: str, endpoint: Handler, methods: Sequence[str]) -> None:
        for method in methods:
            self._routes[(method.upper(), path)] = endpoint

    def get(self, path: str, **_: Any) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self.add_api_route(path, func, ["GET"])
            return func

        return decorator

    def post(self, path: str, **_: Any) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self.add_api_route(path, func, ["POST"])
            return func

        return decorator

    def include_router(self, router: APIRouter) -> None:
        for route in router.routes:
            self.add_api_route(route.path, route.endpoint, route.methods)

    def add_middleware(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401, ANN401
        # CORS и другие middleware тестами не используются, поэтому заглушка ничего не делает.
        return None


class _Response:
    def __init__(self, json_data: Any, status_code: int = 200) -> None:
        self._json_data = json_data
        self.status_code = status_code

    def json(self) -> Any:
        return self._json_data


class TestClient:
    """Упрощённый тестовый клиент, вызывающий обработчики напрямую."""

    __test__ = False

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    def _request(self, method: str, path: str, json: Any | None = None) -> _Response:
        handler = self._app._routes.get((method.upper(), path))
        if handler is None:
            return _Response({"detail": "Not Found"}, status_code=404)

        try:
            if json is None:
                result = handler()
            else:
                result = handler(json)
        except HTTPException as exc:  # pragma: no cover - ветка на случай ошибок
            payload = exc.detail if exc.detail is not None else {"detail": "Error"}
            return _Response(payload, status_code=exc.status_code)

        return _Response(result, status_code=200 if result is not None else 204)

    def get(self, path: str) -> _Response:
        return self._request("GET", path)

    def post(self, path: str, json: Any | None = None) -> _Response:
        return self._request("POST", path, json=json)


class status:
    HTTP_502_BAD_GATEWAY = 502


__all__ = [
    "APIRouter",
    "Depends",
    "FastAPI",
    "HTTPException",
    "TestClient",
    "status",
]
