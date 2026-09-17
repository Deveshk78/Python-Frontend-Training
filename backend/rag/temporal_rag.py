"""Temporal RAG: retrieval is biased toward recency and resolves conflicting document
versions by preferring the most recently published source (e.g., policy v1 vs v2).
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

from backend.llm_client import claude_client
from backend.rag.base import RAGResult, RetrievedChunk, RetrieverBundle
from backend.utils.metrics import PipelineMetrics, timed_stage

HALF_LIFE_DAYS = 365  # recency decay half-life for time-weighted scoring


def _recency_weight(published_at: datetime, now: datetime) -> float:
    age_days = (now.replace(tzinfo=None) - published_at.replace(tzinfo=None)).days
    return math.pow(0.5, max(age_days, 0) / HALF_LIFE_DAYS)


def run_temporal_rag(query: str, top_k: int = 5, now: datetime | None = None) -> RAGResult:
    metrics = PipelineMetrics(pipeline_name="Temporal RAG")
    bundle = RetrieverBundle.instance()
    now = now or datetime.now(timezone.utc)

    with timed_stage(metrics, "dense_retrieval"):
        candidates = bundle.faiss.search(query, top_k=top_k * 2)  # over-fetch, then time-rerank

    with timed_stage(metrics, "temporal_reranking"):
        reranked = []
        for doc, sim_score in candidates:
            weight = _recency_weight(doc.published_at, now)
            combined = 0.6 * sim_score + 0.4 * weight
            reranked.append((doc, combined, weight))
        reranked.sort(key=lambda x: x[1], reverse=True)
        top_chunks = [
            RetrievedChunk(document=doc, score=combined, retriever="temporal-reranked")
            for doc, combined, _w in reranked[:top_k]
        ]

    with timed_stage(metrics, "llm_generation"):
        context = "\n\n".join(
            f"[{c.document.title} | published {c.document.published_at.date()}] {c.document.text}"
            for c in top_chunks
        )
        prompt = (
            f"Question: {query}\n\nContext (each item tagged with publish date):\n{context}\n\n"
            "If sources conflict, prefer the most recently published one and say so explicitly."
        )
        answer = claude_client.generate(prompt)

    return RAGResult(
        answer=answer,
        retrieved=top_chunks,
        metrics=metrics,
        explanation=(
            "Over-fetched candidates by semantic similarity, then re-ranked using a combined "
            "score of similarity + exponential recency decay (365-day half-life), so newer "
            "documents that supersede older/conflicting ones are prioritized in the final answer."
        ),
    )
