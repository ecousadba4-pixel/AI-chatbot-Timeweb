from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import Settings
from app.services.timeweb_agent import TimewebAgentClient


@pytest.fixture
def anyio_backend() -> str:
    """Используем event loop asyncio для тестов."""

    return "asyncio"


class _RecorderTransport(httpx.MockTransport):
    """Mock транспорт, сохраняющий тело запроса."""

    def __init__(self, recorder: dict[str, Any]):
        def _handler(request: httpx.Request) -> httpx.Response:
            recorder["url"] = str(request.url)
            recorder["payload"] = json.loads(request.content)
            return httpx.Response(200, json={"output": {"answer": "ok"}})

        super().__init__(_handler)


@pytest.mark.anyio("asyncio")
async def test_timeweb_agent_client_builds_expected_payload() -> None:
    captured: dict[str, Any] = {}
    transport = _RecorderTransport(captured)

    settings = Settings(
        timeweb_api_base="https://example.com/custom/base",
        timeweb_api_token="token",
        timeweb_agent_id="agent",
    )

    async with httpx.AsyncClient(transport=transport) as http_client:
        agent = TimewebAgentClient(settings, http_client)
        answer = await agent.get_answer(prompt="Привет", context=[], session_id=None)

    assert answer == "ok"
    assert (
        captured["url"]
        == "https://example.com/custom/base/api/v1/ai-agents/run"
    )
    assert captured["payload"]["input"]["prompt"] == "Привет"
    assert "session_id" not in captured["payload"]


@pytest.mark.anyio("asyncio")
async def test_timeweb_agent_client_keeps_empty_session_id() -> None:
    captured: dict[str, Any] = {}
    transport = _RecorderTransport(captured)

    settings = Settings(
        timeweb_api_base="https://example.com/custom/base",
        timeweb_api_token="token",
        timeweb_agent_id="agent",
    )

    async with httpx.AsyncClient(transport=transport) as http_client:
        agent = TimewebAgentClient(settings, http_client)
        answer = await agent.get_answer(
            prompt="Привет",
            context=[],
            session_id="",
        )

    assert answer == "ok"
    assert captured["payload"]["session_id"] == ""
