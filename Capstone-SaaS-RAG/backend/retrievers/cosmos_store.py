"""Cosmos DB persistence layer for documents/chat history, with an in-memory fallback.

In demo mode (or if the SDK/credentials aren't available) this transparently uses an
in-process dict so the rest of the app is agnostic to whether Cosmos DB is live.
"""
from __future__ import annotations

from typing import Any

from backend.config import settings
from backend.data.sample_docs import Document, get_documents


class CosmosStore:
    def __init__(self) -> None:
        self._container = None
        self._memory: dict[str, dict[str, Any]] = {
            d.doc_id: {
                "id": d.doc_id,
                "title": d.title,
                "text": d.text,
                "source": d.source,
                "published_at": d.published_at.isoformat(),
                "tags": d.tags,
            }
            for d in get_documents()
        }

        if settings.has_cosmos_credentials:
            try:
                from azure.cosmos import CosmosClient

                client = CosmosClient(settings.cosmos_endpoint, settings.cosmos_key)
                db = client.create_database_if_not_exists(settings.cosmos_database)
                self._container = db.create_container_if_not_exists(
                    id=settings.cosmos_container, partition_key="/id"
                )
            except Exception:
                self._container = None

    @property
    def is_live(self) -> bool:
        return self._container is not None

    def upsert_document(self, doc: Document) -> None:
        item = {
            "id": doc.doc_id,
            "title": doc.title,
            "text": doc.text,
            "source": doc.source,
            "published_at": doc.published_at.isoformat(),
            "tags": doc.tags,
        }
        if self._container is not None:
            self._container.upsert_item(item)
        else:
            self._memory[doc.doc_id] = item

    def list_documents(self) -> list[dict[str, Any]]:
        if self._container is not None:
            return list(self._container.read_all_items())
        return list(self._memory.values())

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        if self._container is not None:
            try:
                return self._container.read_item(doc_id, partition_key=doc_id)
            except Exception:
                return None
        return self._memory.get(doc_id)


cosmos_store = CosmosStore()
