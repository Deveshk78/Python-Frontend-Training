import streamlit as st

from backend.rag.speculative_rag import run_speculative_rag
from frontend.ui_helpers import query_input, render_rag_result

st.set_page_config(page_title="Speculative RAG", page_icon="⚡", layout="wide")
st.title("⚡ Speculative RAG")
st.caption(
    "Drafts several candidate answers in parallel from small document clusters, then a "
    "verifier pass selects/synthesizes the best-grounded final answer — lower latency at scale."
)

query, submitted = query_input(
    default_query="How does hybrid search combine BM25 and dense vectors?", key="speculative"
)

if submitted and query.strip():
    with st.spinner("Running Speculative RAG pipeline..."):
        result = run_speculative_rag(query)
    render_rag_result(result)
