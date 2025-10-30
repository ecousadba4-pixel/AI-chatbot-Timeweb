"""HTTP-клиент для обращения к Timeweb AI-Agent."""
from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Iterable, Mapping

import httpx

from app.core.config import Settings

__all__ = [
    "TimewebAgentClient",
    "TimewebAgentError",
    "timeweb_agent_client",
]


class TimewebAgentError(RuntimeError):
    """Общее исключение для ошибок при запросе к Timeweb AI-Agent."""


@dataclass(slots=True)
class TimewebAgentClient:
    """Инкапсулирует работу с Timeweb AI-Agent."""

    _settings: Settings
    _http: httpx.AsyncClient

    async def get_answer(
        self,
        *,
        prompt: str,
        context: Iterable[Mapping[str, Any]],
        session_id: str | None,
    ) -> str:
        """Запрашивает ответ у агента и возвращает текст ответа."""

        payload: dict[str, Any] = {
            "agent_id": self._settings.timeweb_agent_id,
            "input": {
                "prompt": prompt,
                "context": _normalize_context(context),
            },
            "generation_config": {
                "temperature": self._settings.timeweb_temperature,
                "top_p": self._settings.timeweb_top_p,
            },
        }

        if session_id is not None:
            payload["session_id"] = session_id

        endpoint = f"{self._settings.timeweb_api_base}/api/v1/ai-agents/run"

        try:
            response = await self._http.post(endpoint, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise TimewebAgentError(
                (
                    "Timeweb агент вернул ошибку "
                    f"{exc.response.status_code}: {exc.response.text}"
                )
            ) from exc
        except httpx.HTTPError as exc:
            raise TimewebAgentError("Не удалось связаться с Timeweb агентом") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise TimewebAgentError("Некорректный JSON от Timeweb агента") from exc

        try:
            answer = data["output"]["answer"]
        except (KeyError, TypeError) as exc:
            raise TimewebAgentError(
                "Ответ Timeweb агента не содержит поле output.answer"
            ) from exc

        if not isinstance(answer, str):
            raise TimewebAgentError("Поле output.answer должно быть строкой")

        return answer


@asynccontextmanager
async def timeweb_agent_client(settings: Settings) -> AsyncIterator[TimewebAgentClient]:
    """Создаёт и управляет ресурсами HTTP-клиента агента."""

    headers = {
        "Authorization": f"Bearer {settings.timeweb_api_token}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(30.0, connect=10.0)

    async with httpx.AsyncClient(headers=headers, timeout=timeout) as http_client:
        yield TimewebAgentClient(settings, http_client)


def _normalize_context(context: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Подготавливает контекст в формате, который ожидает API агента."""

    return [dict(item) for item in context]
