"""Shared types & retriever bundle used by all five RAG strategies."""
from __future__ import annotations

from dataclasses import dataclass, field

from backend.data.sample_docs import Document, get_documents
from backend.retrievers.bm25_retriever import BM25Retriever
from backend.retrievers.faiss_retriever import FaissRetriever
from backend.utils.metrics import PipelineMetrics


@dataclass
class RetrievedChunk:
    document: Document
    score: float
    retriever: str  # "bm25" | "faiss" | "graph" | "temporal"


@dataclass
class RAGResult:
    answer: str
    retrieved: list[RetrievedChunk]
    metrics: PipelineMetrics
    explanation: str = ""  # human-readable description of what the strategy did


class RetrieverBundle:
    """Lazily builds and caches the BM25 + FAISS indexes over the shared demo corpus."""

    _instance: "RetrieverBundle | None" = None

    def __init__(self) -> None:
        self.documents: list[Document] = get_documents()
        self.bm25 = BM25Retriever(self.documents)
        self.faiss = FaissRetriever(self.documents)

    @classmethod
    def instance(cls) -> "RetrieverBundle":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
