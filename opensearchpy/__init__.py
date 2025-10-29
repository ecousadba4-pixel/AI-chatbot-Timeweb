"""Заглушка клиента OpenSearch."""
from __future__ import annotations

from typing import Any, Dict


class RequestsHttpConnection:  # noqa: D401
    """Пустой класс для совместимости."""


class OpenSearch:
    """Простейший клиент, возвращающий статический ответ."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401, ANN401
        self._storage: list[Dict[str, Any]] = []

    def search(self, index: str, body: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        return {"hits": {"hits": []}}


__all__ = ["OpenSearch", "RequestsHttpConnection"]
