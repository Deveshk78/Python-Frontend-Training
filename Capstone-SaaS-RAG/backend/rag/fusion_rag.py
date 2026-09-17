"""Fusion RAG: hybrid BM25 + dense (FAISS) retrieval combined via Reciprocal Rank Fusion (RRF).

RRF is robust because it only needs the *rank* (not the raw score scale) of each result
from each retriever, avoiding the need to normalize BM25 scores against cosine similarities.
"""
from __future__ import annotations

from backend.data.sample_docs import Document
from backend.llm_client import claude_client
from backend.rag.base import RAGResult, RetrievedChunk, RetrieverBundle
from backend.utils.metrics import PipelineMetrics, timed_stage

RRF_K = 60  # standard damping constant from the RRF paper


def reciprocal_rank_fusion(
    ranked_lists: dict[str, list[tuple[Document, float]]], top_k: int = 5
) -> list[RetrievedChunk]:
    scores: dict[str, float] = {}
    doc_lookup: dict[str, Document] = {}
    source_of: dict[str, str] = {}

    for retriever_name, ranked in ranked_lists.items():
        for rank, (doc, _raw_score) in enumerate(ranked):
            scores.setdefault(doc.doc_id, 0.0)
            scores[doc.doc_id] += 1.0 / (RRF_K + rank + 1)
            doc_lookup[doc.doc_id] = doc
            source_of.setdefault(doc.doc_id, retriever_name)

    ranked_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        RetrievedChunk(document=doc_lookup[doc_id], score=score, retriever=f"fusion({source_of[doc_id]}+)")
        for doc_id, score in ranked_ids
    ]


def run_fusion_rag(query: str, top_k: int = 5) -> RAGResult:
    metrics = PipelineMetrics(pipeline_name="Fusion RAG")
    bundle = RetrieverBundle.instance()

    with timed_stage(metrics, "bm25_retrieval"):
        bm25_results = bundle.bm25.search(query, top_k=top_k)

    with timed_stage(metrics, "faiss_retrieval"):
        faiss_results = bundle.faiss.search(query, top_k=top_k)

    with timed_stage(metrics, "reciprocal_rank_fusion"):
        fused = reciprocal_rank_fusion({"bm25": bm25_results, "faiss": faiss_results}, top_k=top_k)

    with timed_stage(metrics, "llm_generation"):
        context = "\n\n".join(f"[{c.document.title}] {c.document.text}" for c in fused)
        prompt = f"Question: {query}\n\nContext:\n{context}\n\nAnswer using only the context above."
        answer = claude_client.generate(prompt)

    return RAGResult(
        answer=answer,
        retrieved=fused,
        metrics=metrics,
        explanation=(
            "Retrieved candidates independently from BM25 (lexical) and FAISS (dense semantic), "
            "then merged rankings using Reciprocal Rank Fusion so keyword-exact and "
            "semantically-similar matches both surface, before grounding the LLM answer."
        ),
    )
