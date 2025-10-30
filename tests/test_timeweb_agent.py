from __future__ import annotations

from json import JSONDecodeError
from typing import Any, Dict, Optional

import httpx
import pytest

from app.services.timeweb_agent import TimewebAgentClient, TimewebAgentError


pytestmark = pytest.mark.anyio("asyncio")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class DummyResponse:
    def __init__(self, status_code: int = 200, json_data: Optional[Dict[str, Any]] = None, text: str = "") -> None:
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "http://testserver")
            raise httpx.HTTPStatusError("error", request=request, response=self)

    def json(self) -> Dict[str, Any]:
        if isinstance(self._json_data, Exception):
            raise self._json_data
        if self._json_data is None:
            raise ValueError("no data")
        return self._json_data


class DummyAsyncClient:
    def __init__(self, response: Optional[DummyResponse] = None, error: Optional[Exception] = None) -> None:
        self._response = response
        self._error = error

    async def __aenter__(self) -> DummyAsyncClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - интерфейс контекстного менеджера
        return None

    async def post(self, *args: Any, **kwargs: Any) -> DummyResponse:
        if self._error is not None:
            raise self._error
        assert self._response is not None
        return self._response


async def test_generate_answer_success(anyio_backend: str) -> None:
    response = DummyResponse(json_data={"output": {"answer": "Привет"}})
    client = TimewebAgentClient(client_factory=lambda: DummyAsyncClient(response=response))

    result = await client.generate_answer("?", [])

    assert result == "Привет"


@pytest.mark.parametrize(
    "response, expected_message",
    [
        (DummyResponse(status_code=500, text="boom", json_data={}), "Ошибка TimeWeb AI-Агента: 500 boom"),
        (
            DummyResponse(
                json_data=JSONDecodeError("bad json", doc="{}", pos=0)
            ),
            "Некорректный JSON-ответ TimeWeb AI-Агента",
        ),
        (DummyResponse(json_data={}), "Ответ TimeWeb AI-Агента не содержит поля output.answer"),
        (DummyResponse(json_data={"output": {"answer": 123}}), "Поле output.answer должно быть строкой"),
    ],
)
async def test_generate_answer_invalid_response(
    anyio_backend: str, response: DummyResponse, expected_message: str
) -> None:
    client = TimewebAgentClient(client_factory=lambda: DummyAsyncClient(response=response))

    with pytest.raises(TimewebAgentError) as exc:
        await client.generate_answer("?", [])

    assert expected_message in str(exc.value)


async def test_generate_answer_network_error(anyio_backend: str) -> None:
    class DummyHttpError(httpx.HTTPError):
        pass

    client = TimewebAgentClient(client_factory=lambda: DummyAsyncClient(error=DummyHttpError("fail")))

    with pytest.raises(TimewebAgentError) as exc:
        await client.generate_answer("?", [])

    assert "Не удалось связаться с TimeWeb AI-Агентом" in str(exc.value)
