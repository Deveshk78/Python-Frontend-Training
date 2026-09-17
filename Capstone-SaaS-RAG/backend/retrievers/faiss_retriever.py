"""FAISS dense vector retriever built over the demo corpus embeddings."""
from __future__ import annotations

import numpy as np

from backend.data.sample_docs import Document
from backend.embeddings import embedding_provider


class FaissRetriever:
    def __init__(self, documents: list[Document]):
        self.documents = documents
        texts = [f"{d.title}. {d.text}" for d in documents]
        self.embeddings = embedding_provider.embed_documents(texts)
        self._index = None
        self._backend = "numpy_fallback"
        try:
            import faiss

            dim = self.embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)  # cosine similarity on normalized vectors
            index.add(self.embeddings)
            self._index = index
            self._backend = "faiss"
        except Exception:
            self._index = None

    def search(self, query: str, top_k: int = 5) -> list[tuple[Document, float]]:
        q_vec = embedding_provider.embed_query(query).reshape(1, -1)
        if self._index is not None:
            scores, idxs = self._index.search(q_vec, top_k)
            results = [
                (self.documents[i], float(scores[0][rank]))
                for rank, i in enumerate(idxs[0])
                if i != -1
            ]
            return results
        # numpy cosine-similarity fallback (identical math, no faiss dependency)
        sims = self.embeddings @ q_vec[0]
        top_idx = np.argsort(-sims)[:top_k]
        return [(self.documents[i], float(sims[i])) for i in top_idx]
