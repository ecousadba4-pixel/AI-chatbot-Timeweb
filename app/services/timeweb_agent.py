"""Упрощённый клиент для обращения к Timeweb AI-Agent."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

import httpx

from app.core.config import Settings


class TimewebAgentError(RuntimeError):
    """Общее исключение для ошибок при запросе к агенту."""


def _normalize_context(context: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Подготавливает контекст в формате, который ожидает API агента."""

    normalized: list[dict[str, Any]] = []

    for item in context:
        normalized.append(dict(item))

    return normalized


async def request_timeweb_answer(
    *,
    settings: Settings,
    prompt: str,
    context: Iterable[Mapping[str, Any]],
    session_id: str | None,
) -> str:
    """Отправляет запрос к Timeweb AI-Agent и возвращает ответ."""

    payload: dict[str, Any] = {
        "agent_id": settings.timeweb_agent_id,
        "input": {"prompt": prompt, "context": _normalize_context(context)},
        "generation_config": {
            "temperature": settings.timeweb_temperature,
            "top_p": settings.timeweb_top_p,
        },
    }

    if session_id is not None:
        payload["session_id"] = session_id

    async with httpx.AsyncClient(
        base_url=settings.timeweb_api_base,
        headers={
            "Authorization": f"Bearer {settings.timeweb_api_token}",
            "Content-Type": "application/json",
        },
        timeout=httpx.Timeout(30.0),
    ) as client:
        try:
            response = await client.post("api/v1/ai-agents/run", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise TimewebAgentError(
                f"Timeweb агент вернул ошибку {exc.response.status_code}: {exc.response.text}"
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
        raise TimewebAgentError("Ответ Timeweb агента не содержит output.answer") from exc

    if not isinstance(answer, str):
        raise TimewebAgentError("Поле output.answer должно быть строкой")

    return answer
