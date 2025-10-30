from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services.timeweb_agent import get_timeweb_agent_client


class DummyAgent:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[object] | None, str | None]] = []

    async def generate_answer(
        self, prompt: str, context: list[object] | None = None, session_id: str | None = None
    ) -> str:
        self.calls.append((prompt, context, session_id))
        return "Ответ"


def test_chat_endpoint_forwards_session_and_context() -> None:
    agent = DummyAgent()
    app.dependency_overrides[get_timeweb_agent_client] = lambda: agent
    client = TestClient(app)

    payload = {
        "question": "Что нового?",
        "session_id": "session-777",
        "context": [
            {"role": "system", "content": "Ты дружелюбный помощник"},
            {"role": "user", "content": "Привет"},
        ],
    }

    try:
        response = client.post("/chat", json=payload)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"answer": "Ответ", "context": []}

    assert agent.calls, "Клиент агента должен быть вызван"
    prompt, context, session_id = agent.calls[0]

    assert prompt == payload["question"]
    assert session_id == payload["session_id"]
    assert context is not None
    assert len(context) == len(payload["context"])

    for original, passed in zip(payload["context"], context, strict=True):
        assert getattr(passed, "role", None) == original["role"]
        assert getattr(passed, "content", None) == original["content"]
