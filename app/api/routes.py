from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import ChatRequest, ChatResponse
from app.services.timeweb_agent import TimewebAgentClient, TimewebAgentError, get_timeweb_agent_client

router = APIRouter()


@router.get("/health", tags=["service"])
def healthcheck() -> dict:
    """Проверка состояния сервиса."""

    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    request: ChatRequest,
    agent: TimewebAgentClient = Depends(get_timeweb_agent_client),
) -> ChatResponse:
    """Обработка запроса из виджета."""

    documents: List[dict] = []
    context_blocks: List[str] = []

    try:
        answer = await agent.generate_answer(request.question, documents)
    except TimewebAgentError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return ChatResponse(answer=answer, context=context_blocks)
