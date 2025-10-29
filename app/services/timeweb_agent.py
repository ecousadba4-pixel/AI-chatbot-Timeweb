from __future__ import annotations

import httpx
from typing import Any, Dict, List

from app.core.config import get_settings


class TimewebAgentError(RuntimeError):
    """Базовая ошибка взаимодействия с TimeWeb AI-Агентом."""


class TimewebAgentClient:
    """Клиент для вызова TimeWeb AI-Агента."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.timeweb_api_base.rstrip("/")
        self._token = settings.timeweb_api_token
        self._agent_id = settings.timeweb_agent_id
        self._temperature = settings.timeweb_temperature
        self._top_p = settings.timeweb_top_p

    async def generate_answer(self, prompt: str, context: List[Dict[str, Any]]) -> str:
        """Отправляет запрос агенту и возвращает ответ."""

        payload: Dict[str, Any] = {
            "agent_id": self._agent_id,
            "input": {
                "prompt": prompt,
                "context": context,
            },
            "generation_config": {
                "temperature": self._temperature,
                "top_p": self._top_p,
            },
        }

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        url = f"{self._base_url}/api/v1/ai-agents/run"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            raise TimewebAgentError(
                f"Ошибка TimeWeb AI-Агента: {response.status_code} {response.text}"
            )

        data = response.json()
        return data.get("output", {}).get("answer", "")


def get_timeweb_agent_client() -> TimewebAgentClient:
    """Возвращает экземпляр клиента TimeWeb AI-Агента."""

    return TimewebAgentClient()
