from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Запрос от фронтенда."""

    question: str = Field(description="Вопрос пользователя")
    session_id: Optional[str] = Field(default=None, description="Идентификатор сессии")
    context: List[Dict[str, str]] = Field(
        default_factory=list,
        description="История сообщений чата, передаваемая агенту",
    )


class ChatResponse(BaseModel):
    """Ответ сервера."""

    answer: str = Field(description="Ответ агента")
