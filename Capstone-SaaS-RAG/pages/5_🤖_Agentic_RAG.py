import streamlit as st

from backend.rag.agentic_rag import run_agentic_rag
from frontend.ui_helpers import query_input, render_rag_result

st.set_page_config(page_title="Agentic RAG", page_icon="🤖", layout="wide")
st.title("🤖 Agentic RAG")
st.caption(
    "A Planner, Retriever-Critic, Writer, and final Critic agent (AutoGen-style multi-agent "
    "loop) collaborate iteratively instead of a single retrieve-then-generate pass."
)

query, submitted = query_input(
    default_query="Design a RAG strategy for questions that require multi-step reasoning across policies.",
    key="agentic",
)

if submitted and query.strip():
    with st.spinner("Running Agentic RAG multi-agent pipeline..."):
        result = run_agentic_rag(query)
    render_rag_result(result)
