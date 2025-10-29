from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

from opensearchpy import OpenSearch, RequestsHttpConnection

from app.core.config import get_settings


class OpenSearchClient:
    """Клиент для работы с OpenSearch."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = OpenSearch(
            hosts=[settings.opensearch_host],
            http_auth=(settings.opensearch_user, settings.opensearch_password),
            use_ssl=settings.opensearch_host.scheme == "https",
            verify_certs=settings.opensearch_verify_ssl,
            connection_class=RequestsHttpConnection,
        )
        self._index = settings.opensearch_index

    def search(self, query: str, size: int = 3) -> List[Dict[str, Any]]:
        """Выполняет полнотекстовый поиск по индексу."""

        body = {
            "size": size,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            },
            "_source": ["title", "content", "url"],
        }

        response = self._client.search(index=self._index, body=body)
        hits = response.get("hits", {}).get("hits", [])
        return [hit.get("_source", {}) for hit in hits]


@lru_cache
def get_opensearch_client() -> OpenSearchClient:
    """Возвращает экземпляр клиента OpenSearch."""

    return OpenSearchClient()
