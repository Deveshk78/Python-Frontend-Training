"""Agentic RAG: a multi-agent (AutoGen-style) loop that plans, retrieves, critiques and writes,
iterating rather than doing a single retrieve-then-generate pass.
"""
from __future__ import annotations

from backend.agents.autogen_agents import AUTOGEN_AVAILABLE, run_agent_pipeline
from backend.rag.base import RAGResult, RetrievedChunk, RetrieverBundle
from backend.utils.metrics import PipelineMetrics, timed_stage


def run_agentic_rag(query: str, top_k: int = 5) -> RAGResult:
    metrics = PipelineMetrics(pipeline_name="Agentic RAG")
    bundle = RetrieverBundle.instance()

    with timed_stage(metrics, "hybrid_retrieval"):
        bm25_hits = bundle.bm25.search(query, top_k=top_k)
        faiss_hits = bundle.faiss.search(query, top_k=top_k)
        seen = set()
        chunks: list[RetrievedChunk] = []
        for doc, score in bm25_hits + faiss_hits:
            if doc.doc_id not in seen:
                seen.add(doc.doc_id)
                chunks.append(RetrievedChunk(document=doc, score=score, retriever="hybrid"))

    with timed_stage(metrics, "multi_agent_reasoning_loop"):
        agent_steps = run_agent_pipeline(query, chunks)

    final_answer = agent_steps[-1].output if agent_steps else "No answer produced."

    explanation = (
        "A Planner agent decomposed the question, a Retriever-Critic agent assessed evidence "
        "sufficiency, a Writer agent drafted a grounded answer, and a final Critic agent "
        "reviewed/corrected it — an autonomous, multi-step reasoning loop rather than a single "
        "retrieve-then-generate call. "
        + ("(Running with `pyautogen` installed.)" if AUTOGEN_AVAILABLE else "(Simulated agent roles — install `pyautogen` for real multi-agent orchestration.)")
    )

    result = RAGResult(answer=final_answer, retrieved=chunks, metrics=metrics, explanation=explanation)
    result.agent_steps = agent_steps  # type: ignore[attr-defined]  # extra info for the UI transcript
    return result
