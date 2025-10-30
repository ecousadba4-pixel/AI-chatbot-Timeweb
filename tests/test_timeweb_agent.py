from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import Settings
from app.services import timeweb_agent


class _DummyResponse:
    def __init__(self, payload: dict[str, Any]):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def test_request_timeweb_answer_respects_base_path(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    async def _dummy_post(self: httpx.AsyncClient, path: str, json: dict[str, Any]) -> _DummyResponse:  # type: ignore[override]
        captured["path"] = path
        captured["url"] = str(self.base_url.join(path))
        captured["payload"] = json
        return _DummyResponse({"output": {"answer": "ok"}})

    monkeypatch.setattr(httpx.AsyncClient, "post", _dummy_post)

    settings = Settings(
        timeweb_api_base="https://example.com/custom/base",
        timeweb_api_token="token",
        timeweb_agent_id="agent",
    )

    async def _run() -> None:
        answer = await timeweb_agent.request_timeweb_answer(
            settings=settings,
            prompt="Привет",
            context=[],
            session_id=None,
        )

        assert answer == "ok"
        assert captured["path"] == "api/v1/ai-agents/run"
        assert captured["url"] == "https://example.com/custom/base/api/v1/ai-agents/run"
        assert captured["payload"]["input"]["prompt"] == "Привет"
        assert "session_id" not in captured["payload"]

    asyncio.run(_run())
