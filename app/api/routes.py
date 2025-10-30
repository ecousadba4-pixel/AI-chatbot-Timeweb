from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import ChatRequest, ChatResponse
from app.api.dependencies import get_timeweb_agent
from app.services.timeweb_agent import TimewebAgentClient, TimewebAgentError

router = APIRouter()


@router.get("/health", tags=["service"])
def healthcheck() -> dict:
    """Проверка состояния сервиса."""

    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    request: ChatRequest,
    agent: TimewebAgentClient = Depends(get_timeweb_agent),
) -> ChatResponse:
    """Обработка запроса из виджета."""

    try:
        answer = await agent.get_answer(
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
