"""Упрощённая реализация FastAPI для офлайн-тестов."""
from __future__ import annotations

import asyncio
import inspect
import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

try:  # pragma: no cover - в реальной среде используется настоящая библиотека
    from pydantic import BaseModel
except Exception:  # pragma: no cover - защита от неожиданных ошибок импорта
    BaseModel = object  # type: ignore[assignment]


def _is_pydantic_model(annotation: Any) -> bool:
    return isinstance(annotation, type) and (
        hasattr(annotation, "model_fields") or hasattr(annotation, "__fields__")
    )


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


class _NotFound(Exception):
    """Внутреннее исключение для обозначения отсутствующего маршрута."""


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
        self._routes: Dict[Tuple[str, str], _Route] = {}

    def add_api_route(self, path: str, endpoint: Handler, methods: Sequence[str]) -> None:
        route = _Route(path, methods, endpoint)
        for method in methods:
            self._routes[(method.upper(), path)] = route

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

    async def __call__(self, scope: Mapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[None]]) -> None:
        if scope.get("type") != "http":  # pragma: no cover - uvicorn всегда передаёт http
            raise RuntimeError("Unsupported scope type")

        method = scope.get("method", "GET").upper()
        path = scope.get("path", "/")

        try:
            body = await self._read_body(receive) if method in {"POST", "PUT", "PATCH"} else None
            result = await self._dispatch(method, path, body)
            status_code = 204 if result is None else 200
            payload = self._serialize_response(result)
        except _NotFound:
            status_code = 404
            payload = {"detail": "Not Found"}
        except HTTPException as exc:
            status_code = exc.status_code
            payload = self._format_detail(exc.detail)

        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        body_bytes = b"" if payload is None else json.dumps(payload).encode("utf-8")
        await send({"type": "http.response.body", "body": body_bytes})

    async def _dispatch(self, method: str, path: str, body: Any) -> Any:
        route = self._routes.get((method.upper(), path))
        if route is None:
            raise _NotFound

        kwargs = await self._build_kwargs(route.endpoint, body)
        result = route.endpoint(**kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result

    async def _build_kwargs(self, endpoint: Handler, body: Any) -> Dict[str, Any]:
        signature = inspect.signature(endpoint)
        kwargs: Dict[str, Any] = {}
        for param in signature.parameters.values():
            default = param.default
            if isinstance(default, Depends):
                dependency = default.dependency
                if dependency is None:
                    raise RuntimeError("Dependency callable is required")
                value = dependency()
                if inspect.isawaitable(value):
                    value = await value
                kwargs[param.name] = value
                continue

            if param.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
                continue

            value = self._extract_body_argument(param, body)
            kwargs[param.name] = value

        return kwargs

    def _extract_body_argument(self, param: inspect.Parameter, body: Any) -> Any:
        if body is None:
            return None

        annotation = param.annotation

        if annotation is inspect._empty:
            return body

        if _is_pydantic_model(annotation):
            if isinstance(body, dict):
                return annotation(**body)
            return annotation(body)

        try:
            if isinstance(body, dict) and param.name in body:
                return annotation(body[param.name])
            return annotation(body)
        except Exception:  # pragma: no cover - fallback на необрабатываемые типы
            return body

    def _serialize_response(self, result: Any) -> Any:
        if result is None:
            return None

        if hasattr(result, "model_dump") and callable(result.model_dump):
            return result.model_dump()

        if hasattr(result, "dict") and callable(result.dict):
            return result.dict()

        return result

    def _format_detail(self, detail: Any) -> Any:
        if detail is None:
            return {"detail": "Error"}
        if isinstance(detail, Mapping):
            return dict(detail)
        return {"detail": detail}

    async def _read_body(self, receive: Callable[[], Awaitable[MutableMapping[str, Any]]]) -> Any:
        chunks: List[bytes] = []
        while True:
            message = await receive()
            if message.get("type") == "http.disconnect":  # pragma: no cover - на случай обрыва соединения
                return None
            body = message.get("body", b"")
            if body:
                chunks.append(body)
            if not message.get("more_body", False):
                break
        raw = b"".join(chunks)
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON") from exc


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

    def _run(self, coro: Awaitable[Any]) -> Any:
        return asyncio.run(coro)

    def _request(self, method: str, path: str, json: Any | None = None) -> _Response:
        try:
            result = self._run(self._app._dispatch(method, path, json))
        except _NotFound:
            return _Response({"detail": "Not Found"}, status_code=404)
        except HTTPException as exc:
            payload = self._app._format_detail(exc.detail)
            return _Response(payload, status_code=exc.status_code)

        status_code = 204 if result is None else 200
        payload = self._app._serialize_response(result)
        return _Response(payload, status_code=status_code)

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
