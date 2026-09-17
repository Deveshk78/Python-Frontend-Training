"""Shared Streamlit rendering helpers used across every RAG demo page."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.config import settings
from backend.embeddings import embedding_provider
from backend.llm_client import claude_client
from backend.rag.base import RAGResult
from backend.retrievers.cosmos_store import cosmos_store


def render_status_badges() -> None:
    """Shows whether each backing service is running live or in offline demo-fallback mode —
    important for an architect audience to see the system's graceful-degradation design."""
    cols = st.columns(4)
    badges = [
        ("Claude Sonnet", claude_client.is_live),
        ("HF Embeddings", embedding_provider.is_live),
        ("Cosmos DB", cosmos_store.is_live),
        ("Demo Mode", settings.demo_mode),
    ]
    for col, (label, is_on) in zip(cols, badges):
        with col:
            if label == "Demo Mode":
                st.metric(label, "ON" if is_on else "OFF")
            else:
                st.metric(label, "LIVE" if is_on else "OFFLINE FALLBACK")


def render_rag_result(result: RAGResult) -> None:
    st.subheader("Answer")
    st.info(result.answer)

    if result.explanation:
        st.caption(f"🧠 **How this strategy works:** {result.explanation}")

    with st.expander(f"📚 Retrieved context ({len(result.retrieved)} chunks)", expanded=False):
        rows = [
            {
                "title": c.document.title,
                "source": c.document.source,
                "retriever": c.retriever,
                "score": round(c.score, 4),
                "published_at": c.document.published_at.date().isoformat(),
            }
            for c in result.retrieved
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("⏱️ Pipeline latency breakdown", expanded=False):
        stage_df = pd.DataFrame(
            [{"stage": s.stage, "duration_ms": round(s.duration_ms, 1)} for s in result.metrics.stages]
        )
        st.bar_chart(stage_df.set_index("stage"))
        st.caption(f"Total pipeline latency: **{result.metrics.total_ms:.1f} ms**")

    agent_steps = getattr(result, "agent_steps", None)
    if agent_steps:
        with st.expander("🤖 Multi-agent transcript", expanded=True):
            for step in agent_steps:
                with st.chat_message("assistant"):
                    st.markdown(f"**{step.agent}**\n\n{step.output}")


def query_input(default_query: str, key: str) -> tuple[str, bool]:
    query = st.text_input("Ask a question about the demo knowledge base", value=default_query, key=f"q_{key}")
    submitted = st.button("Run", key=f"btn_{key}", type="primary")
    return query, submitted
