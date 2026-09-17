import streamlit as st

from backend.rag.temporal_rag import run_temporal_rag
from frontend.ui_helpers import query_input, render_rag_result

st.set_page_config(page_title="Temporal RAG", page_icon="🕰️", layout="wide")
st.title("🕰️ Temporal RAG")
st.caption(
    "Re-ranks retrieved documents using a recency-weighted score, so newer documents that "
    "supersede older/conflicting ones (e.g., policy v1 vs v2) are prioritized."
)

query, submitted = query_input(
    default_query="What is our cloud cost optimization policy?", key="temporal"
)

if submitted and query.strip():
    with st.spinner("Running Temporal RAG pipeline..."):
        result = run_temporal_rag(query)
    render_rag_result(result)
