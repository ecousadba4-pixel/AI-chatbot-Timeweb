"""Зависимости FastAPI для роутов приложения."""

from __future__ import annotations

from fastapi import Request

from app.services.timeweb_agent import TimewebAgentClient


def get_timeweb_agent(request: Request) -> TimewebAgentClient:
    """Возвращает инициализированный клиент Timeweb Agent из состояния приложения."""

    agent = getattr(request.app.state, "timeweb_agent", None)

    if agent is None:
        raise RuntimeError("TimewebAgentClient ещё не инициализирован")

    return agent
