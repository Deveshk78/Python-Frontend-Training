"""Synthetic demo corpus — a small enterprise knowledge base used across all RAG demos.

Each document has metadata (source, published_at) so Temporal RAG and Graph RAG
have something meaningful to reason over, without needing any external data source.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    source: str
    published_at: datetime
    tags: list[str] = field(default_factory=list)


SAMPLE_DOCUMENTS: list[Document] = [
    Document(
        doc_id="doc-1",
        title="Cloud Cost Optimization Policy v1",
        text=(
            "In 2022, the company mandated that all cloud workloads be reviewed quarterly "
            "for right-sizing. Reserved instances were recommended for steady-state workloads, "
            "and spot instances for batch jobs."
        ),
        source="internal-wiki",
        published_at=datetime(2022, 3, 1),
        tags=["finops", "cloud", "policy"],
    ),
    Document(
        doc_id="doc-2",
        title="Cloud Cost Optimization Policy v2",
        text=(
            "As of 2024, the policy was updated: all workloads must use auto-scaling groups, "
            "reserved instances are now purchased centrally by the platform team, and spot "
            "instances are mandatory for all non-critical batch workloads."
        ),
        source="internal-wiki",
        published_at=datetime(2024, 6, 15),
        tags=["finops", "cloud", "policy"],
    ),
    Document(
        doc_id="doc-3",
        title="Retrieval-Augmented Generation Overview",
        text=(
            "Retrieval-Augmented Generation (RAG) combines a retriever, which fetches relevant "
            "passages from an external knowledge base, with a generator (an LLM) that synthesizes "
            "an answer grounded in the retrieved context, reducing hallucination."
        ),
        source="engineering-handbook",
        published_at=datetime(2023, 1, 10),
        tags=["genai", "rag", "architecture"],
    ),
    Document(
        doc_id="doc-4",
        title="Hybrid Search: BM25 + Dense Vectors",
        text=(
            "Hybrid search fuses lexical retrieval (BM25, good at exact term/keyword matches) "
            "with dense vector retrieval (good at semantic similarity), often combined via "
            "Reciprocal Rank Fusion (RRF) to get the benefits of both."
        ),
        source="engineering-handbook",
        published_at=datetime(2023, 5, 20),
        tags=["genai", "search", "bm25", "faiss"],
    ),
    Document(
        doc_id="doc-5",
        title="Data Retention and Compliance Guidelines",
        text=(
            "Customer data must be retained for no longer than 24 months unless required by "
            "regulation. Personally identifiable information (PII) must be encrypted at rest "
            "using AES-256 and in transit using TLS 1.2 or higher."
        ),
        source="legal-compliance",
        published_at=datetime(2021, 11, 5),
        tags=["compliance", "security", "data"],
    ),
    Document(
        doc_id="doc-6",
        title="Incident Response Runbook",
        text=(
            "On detecting a Sev-1 incident, the on-call engineer must page the incident "
            "commander within 5 minutes, open a war room, and post updates every 15 minutes "
            "until mitigation."
        ),
        source="sre-runbooks",
        published_at=datetime(2023, 9, 12),
        tags=["sre", "incident", "process"],
    ),
    Document(
        doc_id="doc-7",
        title="Multi-Agent Orchestration with AutoGen",
        text=(
            "AutoGen enables multiple specialized LLM agents (e.g., a Planner, a Retriever "
            "agent, a Critic, and a Writer) to collaborate via structured conversation to solve "
            "tasks that a single-shot LLM call struggles with, especially multi-step reasoning."
        ),
        source="engineering-handbook",
        published_at=datetime(2024, 2, 2),
        tags=["genai", "agents", "autogen"],
    ),
    Document(
        doc_id="doc-8",
        title="Vector Database Selection Guide",
        text=(
            "FAISS is a fast, in-process library ideal for prototyping and moderate-scale "
            "vector search. For production multi-tenant SaaS, a managed store like Cosmos DB's "
            "vector search or a dedicated vector DB is preferred for durability and scale."
        ),
        source="engineering-handbook",
        published_at=datetime(2024, 8, 1),
        tags=["genai", "faiss", "cosmosdb", "vector-db"],
    ),
]


def get_documents() -> list[Document]:
    return SAMPLE_DOCUMENTS
