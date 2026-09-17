"""Side-by-side comparison of all 5 RAG strategies for one question — the page designed
specifically for live demos to architects/management: answer quality + latency at a glance.
"""
import pandas as pd
import streamlit as st

from backend.rag.agentic_rag import run_agentic_rag
from backend.rag.fusion_rag import run_fusion_rag
from backend.rag.graph_rag import run_graph_rag
from backend.rag.speculative_rag import run_speculative_rag
from backend.rag.temporal_rag import run_temporal_rag
from frontend.ui_helpers import render_status_badges

st.set_page_config(page_title="Architecture Dashboard", page_icon="📊", layout="wide")
st.title("📊 Architecture Dashboard — Compare All RAG Strategies")
st.caption(
    "Run one question through all five RAG pipelines simultaneously to compare grounded "
    "answers, retrieval strategy, and latency — built for architect/management walkthroughs."
)

render_status_badges()
st.divider()

query = st.text_input(
    "Question to run through every strategy",
    value="What is our current cloud cost optimization policy, and how does it relate to our RAG architecture?",
)
run = st.button("▶️ Run all 5 strategies", type="primary")

STRATEGIES = {
    "Fusion RAG": run_fusion_rag,
    "Speculative RAG": run_speculative_rag,
    "Graph RAG": run_graph_rag,
    "Temporal RAG": run_temporal_rag,
    "Agentic RAG": run_agentic_rag,
}

if run and query.strip():
    results = {}
    progress = st.progress(0.0, text="Starting...")
    for i, (name, fn) in enumerate(STRATEGIES.items()):
        progress.progress((i) / len(STRATEGIES), text=f"Running {name}...")
        results[name] = fn(query)
    progress.progress(1.0, text="Done")
    progress.empty()

    st.subheader("Latency comparison")
    latency_df = pd.DataFrame(
        [{"strategy": name, "total_ms": r.metrics.total_ms} for name, r in results.items()]
    ).set_index("strategy")
    st.bar_chart(latency_df)

    st.subheader("Answers side-by-side")
    tabs = st.tabs(list(results.keys()))
    for tab, (name, r) in zip(tabs, results.items()):
        with tab:
            st.info(r.answer)
            st.caption(f"🧠 {r.explanation}")
            st.caption(
                f"⏱️ {r.metrics.total_ms:.1f} ms total · 📚 {len(r.retrieved)} chunks retrieved"
            )

    st.subheader("Retrieval overlap")
    overlap_rows = []
    for name, r in results.items():
        titles = ", ".join(sorted({c.document.title for c in r.retrieved}))
        overlap_rows.append({"strategy": name, "documents_used": titles})
    st.dataframe(pd.DataFrame(overlap_rows), use_container_width=True, hide_index=True)
else:
    st.info("Enter a question and click **Run all 5 strategies** to populate the comparison.")
