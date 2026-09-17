"""Graph RAG: seed via dense retrieval, then expand context by walking the knowledge graph
(shared tags/entities) so multi-hop relationships surface answers a single vector lookup
would miss (e.g., connecting a policy document to the engineering handbook via shared tags).
"""
from __future__ import annotations

from backend.graph.knowledge_graph import get_knowledge_graph
from backend.llm_client import claude_client
from backend.rag.base import RAGResult, RetrievedChunk, RetrieverBundle
from backend.utils.metrics import PipelineMetrics, timed_stage


def run_graph_rag(query: str, top_k: int = 3, hops: int = 2) -> RAGResult:
    metrics = PipelineMetrics(pipeline_name="Graph RAG")
    bundle = RetrieverBundle.instance()
    kg = get_knowledge_graph()

    with timed_stage(metrics, "seed_retrieval"):
        seed_results = bundle.faiss.search(query, top_k=top_k)
        seed_chunks = [RetrievedChunk(document=d, score=s, retriever="faiss-seed") for d, s in seed_results]

    with timed_stage(metrics, "graph_expansion"):
        expanded_docs = {}
        for chunk in seed_chunks:
            for related in kg.related_documents(chunk.document.doc_id, hops=hops):
                expanded_docs[related.doc_id] = related
        graph_chunks = [
            RetrievedChunk(document=doc, score=0.5, retriever="graph-expansion")
            for doc in expanded_docs.values()
            if doc.doc_id not in {c.document.doc_id for c in seed_chunks}
        ]

    all_chunks = seed_chunks + graph_chunks

    with timed_stage(metrics, "llm_generation"):
        context = "\n\n".join(
            f"[{c.document.title} | tags={c.document.tags}] {c.document.text}" for c in all_chunks
        )
        prompt = (
            f"Question: {query}\n\nContext (including graph-expanded related documents):\n{context}\n\n"
            "Answer using the context, and mention any cross-document relationships you used."
        )
        answer = claude_client.generate(prompt)

    return RAGResult(
        answer=answer,
        retrieved=all_chunks,
        metrics=metrics,
        explanation=(
            f"Seeded with {len(seed_chunks)} dense-retrieved documents, then expanded via a "
            f"{hops}-hop walk over a tag-based knowledge graph, pulling in {len(graph_chunks)} "
            "additional related documents that a pure vector search might have missed."
        ),
    )
