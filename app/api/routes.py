from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import ChatRequest, ChatResponse
from app.services.opensearch_client import get_opensearch_client, OpenSearchClient
from app.services.timeweb_agent import TimewebAgentClient, TimewebAgentError, get_timeweb_agent_client

router = APIRouter()


def _format_context(documents: List[dict]) -> List[str]:
    """Превращает документы из OpenSearch в список строк."""

    context_blocks: List[str] = []
    for doc in documents:
        title = doc.get("title", "Без названия")
        content = doc.get("content", "")
        url = doc.get("url")
        block = f"{title}\n{content.strip()}"
        if url:
            block += f"\nИсточник: {url}"
        context_blocks.append(block)
    return context_blocks


@router.get("/health", tags=["service"])
def healthcheck() -> dict:
    """Проверка состояния сервиса."""

    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    request: ChatRequest,
    opensearch: OpenSearchClient = Depends(get_opensearch_client),
    agent: TimewebAgentClient = Depends(get_timeweb_agent_client),
) -> ChatResponse:
    """Обработка запроса из виджета."""

    documents = opensearch.search(request.question)
    context_blocks = _format_context(documents)

    try:
        answer = await agent.generate_answer(request.question, documents)
    except TimewebAgentError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return ChatResponse(answer=answer, context=context_blocks)
