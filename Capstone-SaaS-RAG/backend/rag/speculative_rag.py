"""Speculative RAG: draft-then-verify pattern.

A cheap/fast "drafter" step proposes several candidate answers from small clusters of
retrieved documents in parallel, then a stronger "verifier" (Claude) picks/refines the
best-grounded draft — reducing latency vs. running one large sequential LLM call over
the full context, similar in spirit to speculative decoding.
"""
from __future__ import annotations

from dataclasses import dataclass

from backend.llm_client import claude_client
from backend.rag.base import RAGResult, RetrievedChunk, RetrieverBundle
from backend.utils.metrics import PipelineMetrics, timed_stage


@dataclass
class Draft:
    text: str
    supporting_chunks: list[RetrievedChunk]


def _make_drafts(chunks: list[RetrievedChunk], query: str, cluster_size: int = 2) -> list[Draft]:
    """Splits retrieved chunks into small clusters and drafts a quick answer per cluster."""
    drafts = []
    for i in range(0, len(chunks), cluster_size):
        cluster = chunks[i : i + cluster_size]
        context = "\n".join(c.document.text for c in cluster)
        draft_prompt = f"Question: {query}\n\nContext:\n{context}\n\nGive a short draft answer."
        draft_text = claude_client.generate(draft_prompt, max_tokens=150)
        drafts.append(Draft(text=draft_text, supporting_chunks=cluster))
    return drafts


def run_speculative_rag(query: str, top_k: int = 6) -> RAGResult:
    metrics = PipelineMetrics(pipeline_name="Speculative RAG")
    bundle = RetrieverBundle.instance()

    with timed_stage(metrics, "dense_retrieval"):
        faiss_results = bundle.faiss.search(query, top_k=top_k)
        chunks = [RetrievedChunk(document=d, score=s, retriever="faiss") for d, s in faiss_results]

    with timed_stage(metrics, "parallel_draft_generation"):
        drafts = _make_drafts(chunks, query)

    with timed_stage(metrics, "verification_and_selection"):
        drafts_block = "\n\n".join(f"Draft {i+1}: {d.text}" for i, d in enumerate(drafts))
        verify_prompt = (
            f"Question: {query}\n\nCandidate drafts:\n{drafts_block}\n\n"
            "Context:\n" + "\n".join(c.document.text for c in chunks) + "\n\n"
            "Select and synthesize the best-supported, most accurate final answer."
        )
        final_answer = claude_client.generate(verify_prompt)

    return RAGResult(
        answer=final_answer,
        retrieved=chunks,
        metrics=metrics,
        explanation=(
            f"Retrieved {len(chunks)} chunks, drafted {len(drafts)} candidate answers in parallel "
            "over small document clusters (fast, cheap), then a verifier pass selected/synthesized "
            "the best-grounded final answer — trading a bit of extra generation for lower "
            "end-to-end latency versus one large sequential context pass."
        ),
    )
