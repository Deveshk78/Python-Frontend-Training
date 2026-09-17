"""A tiny in-memory knowledge graph (networkx) built from document tags/entities.

In a production system this would be built via NER/entity-linking over the corpus and
persisted (e.g., in Cosmos DB Gremlin API or a dedicated graph DB). Here it's derived
directly from document tags to keep the demo self-contained and fast.
"""
from __future__ import annotations

from backend.data.sample_docs import Document, get_documents

try:
    import networkx as nx

    _HAS_NETWORKX = True
except Exception:  # pragma: no cover - fallback if networkx isn't installed
    _HAS_NETWORKX = False


class KnowledgeGraph:
    def __init__(self, documents: list[Document]):
        self.documents = documents
        self._adjacency: dict[str, set[str]] = {}
        self._graph = nx.Graph() if _HAS_NETWORKX else None
        self._build()

    def _build(self) -> None:
        for doc in self.documents:
            node_id = doc.doc_id
            self._adjacency.setdefault(node_id, set())
            if self._graph is not None:
                self._graph.add_node(node_id, title=doc.title, tags=doc.tags)
            for tag in doc.tags:
                self._adjacency.setdefault(tag, set())
                self._adjacency[node_id].add(tag)
                self._adjacency[tag].add(node_id)
                if self._graph is not None:
                    self._graph.add_node(tag, kind="tag")
                    self._graph.add_edge(node_id, tag)

    def related_documents(self, doc_id: str, hops: int = 2) -> list[Document]:
        """Returns documents reachable within `hops` graph edges (shared tags) of doc_id."""
        if self._graph is not None:
            lengths = nx.single_source_shortest_path_length(self._graph, doc_id, cutoff=hops)
            related_ids = {
                n for n in lengths if n != doc_id and any(n == d.doc_id for d in self.documents)
            }
        else:
            frontier = {doc_id}
            visited = {doc_id}
            for _ in range(hops):
                next_frontier = set()
                for node in frontier:
                    next_frontier |= self._adjacency.get(node, set())
                frontier = next_frontier - visited
                visited |= frontier
            related_ids = {n for n in visited if n != doc_id and any(n == d.doc_id for d in self.documents)}

        by_id = {d.doc_id: d for d in self.documents}
        return [by_id[i] for i in related_ids if i in by_id]

    def documents_for_tags(self, tags: list[str]) -> list[Document]:
        return [d for d in self.documents if set(d.tags) & set(tags)]


_kg_instance: KnowledgeGraph | None = None


def get_knowledge_graph() -> KnowledgeGraph:
    global _kg_instance
    if _kg_instance is None:
        _kg_instance = KnowledgeGraph(get_documents())
    return _kg_instance
