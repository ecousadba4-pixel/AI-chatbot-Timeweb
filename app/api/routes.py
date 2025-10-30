from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.schemas import ChatRequest, ChatResponse
from app.core.config import get_settings
from app.services.timeweb_agent import TimewebAgentError, request_timeweb_answer

router = APIRouter()


@router.get("/health", tags=["service"])
def healthcheck() -> dict:
    """Проверка состояния сервиса."""

    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """Обработка запроса из виджета."""

    try:
        answer = await request_timeweb_answer(
            settings=get_settings(),
            prompt=request.question,
            context=request.context,
            session_id=request.session_id,
        )
    except TimewebAgentError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return ChatResponse(answer=answer)
