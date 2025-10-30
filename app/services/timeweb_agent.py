from __future__ import annotations

from functools import lru_cache
from json import JSONDecodeError
from typing import Any, Callable, Mapping, MutableMapping, Sequence

import httpx

from app.core.config import get_settings


class TimewebAgentError(RuntimeError):
    """Базовая ошибка взаимодействия с TimeWeb AI-Агентом."""


ContextPayload = Sequence[Mapping[str, Any]] | None


class TimewebAgentClient:
    """Клиент для вызова TimeWeb AI-Агента."""

    _ENDPOINT = "/api/v1/ai-agents/run"

    def __init__(self, client_factory: Callable[[], httpx.AsyncClient] | None = None) -> None:
        settings = get_settings()
        self._base_url = str(settings.timeweb_api_base).rstrip("/")
        self._token = settings.timeweb_api_token
        self._agent_id = settings.timeweb_agent_id
        self._temperature = settings.timeweb_temperature
        self._top_p = settings.timeweb_top_p
        self._client_factory = client_factory or self._default_client_factory

    async def generate_answer(self, prompt: str, context: ContextPayload = None) -> str:
        """Отправляет запрос агенту и возвращает ответ."""

        payload = self._build_payload(prompt, context)

        try:
            async with self._client_factory() as client:
                response = await client.post(self._ENDPOINT, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            detail = exc.response.text
            raise TimewebAgentError(
                f"Ошибка TimeWeb AI-Агента: {status_code} {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise TimewebAgentError("Не удалось связаться с TimeWeb AI-Агентом") from exc

        data = self._parse_response(response)
        answer = self._extract_answer(data)

        return answer

    def _build_payload(self, prompt: str, context: ContextPayload) -> dict[str, Any]:
        prepared_context = [dict(item) for item in context] if context else []

        return {
            "agent_id": self._agent_id,
            "input": {
                "prompt": prompt,
                "context": prepared_context,
            },
            "generation_config": {
                "temperature": self._temperature,
                "top_p": self._top_p,
            },
        }

    def _default_client_factory(self) -> httpx.AsyncClient:
        headers: MutableMapping[str, str] = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        return httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=httpx.Timeout(30.0),
        )

    def _parse_response(self, response: httpx.Response) -> dict[str, Any]:
        try:
            return response.json()
        except (JSONDecodeError, ValueError) as exc:
            raise TimewebAgentError("Некорректный JSON-ответ TimeWeb AI-Агента") from exc

    def _extract_answer(self, data: Mapping[str, Any]) -> str:
        try:
            answer = data["output"]["answer"]
        except (KeyError, TypeError) as exc:
            raise TimewebAgentError(
                "Ответ TimeWeb AI-Агента не содержит поля output.answer"
            ) from exc

        if not isinstance(answer, str):
            raise TimewebAgentError("Поле output.answer должно быть строкой")

        return answer


@lru_cache
def _cached_timeweb_agent_client() -> TimewebAgentClient:
    return TimewebAgentClient()


def get_timeweb_agent_client() -> TimewebAgentClient:
    """Возвращает экземпляр клиента TimeWeb AI-Агента."""

    return _cached_timeweb_agent_client()
