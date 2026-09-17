import streamlit as st

from backend.rag.fusion_rag import run_fusion_rag
from frontend.ui_helpers import query_input, render_rag_result

st.set_page_config(page_title="Fusion RAG", page_icon="🔀", layout="wide")
st.title("🔀 Fusion RAG")
st.caption(
    "Combines BM25 (lexical/keyword) and FAISS (dense/semantic) retrieval, merged via "
    "**Reciprocal Rank Fusion** — robust to both exact-term and paraphrased questions."
)

query, submitted = query_input(
    default_query="What is the current cloud cost optimization policy?", key="fusion"
)

if submitted and query.strip():
    with st.spinner("Running Fusion RAG pipeline..."):
        result = run_fusion_rag(query)
    render_rag_result(result)
