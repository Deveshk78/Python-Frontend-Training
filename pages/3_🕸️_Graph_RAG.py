import streamlit as st

from backend.rag.graph_rag import run_graph_rag
from frontend.ui_helpers import query_input, render_rag_result

st.set_page_config(page_title="Graph RAG", page_icon="🕸️", layout="wide")
st.title("🕸️ Graph RAG")
st.caption(
    "Seeds with dense vector retrieval, then expands context by walking a tag-based "
    "knowledge graph — surfacing multi-hop, cross-document relationships."
)

query, submitted = query_input(
    default_query="How do AutoGen agents relate to vector databases in our architecture?",
    key="graph",
)
hops = st.slider("Graph expansion hops", min_value=1, max_value=3, value=2, key="graph_hops")

if submitted and query.strip():
    with st.spinner("Running Graph RAG pipeline..."):
        result = run_graph_rag(query, hops=hops)
    render_rag_result(result)
