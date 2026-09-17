"""Capstone SaaS demo — Home page.

Run with: streamlit run app.py   (from the Capstone-SaaS-RAG/ directory)
"""
from __future__ import annotations

import streamlit as st

from backend.config import settings
from backend.data.sample_docs import get_documents
from frontend.ui_helpers import render_status_badges

st.set_page_config(page_title=settings.app_title, page_icon="🧠", layout="wide")

st.title("🧠 " + settings.app_title)
st.caption(
    "A generative AI SaaS reference architecture: AutoGen multi-agent orchestration, "
    "Claude Sonnet, hybrid BM25 + FAISS retrieval, HuggingFace embeddings, Cosmos DB "
    "persistence — demonstrating **Fusion, Speculative, Graph, Temporal, and Agentic RAG**."
)

render_status_badges()

st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("What this demo shows")
    st.markdown(
        """
        Use the sidebar to navigate between five advanced Retrieval-Augmented Generation (RAG)
        architectures, each implemented against the **same shared enterprise knowledge base** so
        you can directly compare their retrieval strategy, latency profile, and answer quality:

        | Page | Strategy | Best for |
        |---|---|---|
        | 🔀 Fusion RAG | BM25 + dense retrieval fused via Reciprocal Rank Fusion | Balancing keyword-exact and semantic recall |
        | ⚡ Speculative RAG | Parallel draft generation + verification pass | Lower latency at scale |
        | 🕸️ Graph RAG | Vector seed + knowledge-graph multi-hop expansion | Multi-hop / relational questions |
        | 🕰️ Temporal RAG | Recency-weighted re-ranking | Resolving conflicting/superseded documents |
        | 🤖 Agentic RAG | Planner → Retriever-Critic → Writer → Critic loop | Complex, multi-step reasoning |

        Open **📊 Architecture Dashboard** to run all five side-by-side for a single question —
        ideal for a live architect/management walkthrough.
        """
    )
with col2:
    st.subheader("Knowledge base")
    docs = get_documents()
    st.metric("Documents indexed", len(docs))
    for d in docs:
        st.caption(f"• **{d.title}** — {d.source} ({d.published_at.date()})")

st.divider()
st.subheader("Reference architecture")
st.markdown(
    """
```mermaid
flowchart LR
    U[User via Streamlit] --> R{RAG Strategy Selector}
    R --> BM25[BM25 Lexical Retriever]
    R --> FAISS[FAISS Dense Retriever]
    R --> GRAPH[Knowledge Graph]
    BM25 & FAISS & GRAPH --> FUSE[Fusion / Rerank Layer]
    FUSE --> AGENTS[AutoGen Multi-Agent Loop]
    AGENTS --> CLAUDE[Claude Sonnet]
    CLAUDE --> U
    EMB[HuggingFace Inference API Embeddings] --> FAISS
    COSMOS[(Cosmos DB)] --> BM25
    COSMOS --> FAISS
```
    """
)
st.caption(
    "Every external dependency (Claude, HF embeddings, Cosmos DB) has a transparent, "
    "deterministic offline fallback — this demo runs end-to-end with zero API keys, "
    "and switches to live services automatically once credentials are set in `.env`."
)
