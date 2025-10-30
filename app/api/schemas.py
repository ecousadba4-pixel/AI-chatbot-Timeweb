from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Сообщение чата."""

    role: str = Field(description="Роль автора сообщения")
    content: str = Field(description="Текст сообщения")


class ChatRequest(BaseModel):
    """Запрос от фронтенда."""

    question: str = Field(description="Вопрос пользователя")
    session_id: Optional[str] = Field(default=None, description="Идентификатор сессии")
    context: List[ChatMessage] = Field(
        default_factory=list,
        description="История сообщений чата, передаваемая агенту",
    )


class ChatResponse(BaseModel):
    """Ответ сервера."""

    answer: str = Field(description="Ответ агента")
    context: List[str] = Field(default_factory=list, description="Фрагменты знаний")
