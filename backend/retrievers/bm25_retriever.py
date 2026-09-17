"""BM25 lexical retriever using rank-bm25, with a pure-Python fallback if unavailable."""
from __future__ import annotations

import math
import re
from collections import Counter

from backend.data.sample_docs import Document


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class SimpleBM25:
    """Minimal BM25 implementation (Okapi BM25) — used if `rank_bm25` isn't installed."""

    def __init__(self, corpus_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.corpus_tokens = corpus_tokens
        self.doc_lens = [len(d) for d in corpus_tokens]
        self.avgdl = sum(self.doc_lens) / len(self.doc_lens) if corpus_tokens else 0
        self.df = Counter()
        for doc in corpus_tokens:
            for term in set(doc):
                self.df[term] += 1
        self.n_docs = len(corpus_tokens)

    def _idf(self, term: str) -> float:
        n_qi = self.df.get(term, 0)
        return math.log((self.n_docs - n_qi + 0.5) / (n_qi + 0.5) + 1)

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        scores = [0.0] * self.n_docs
        for term in query_tokens:
            idf = self._idf(term)
            for i, doc in enumerate(self.corpus_tokens):
                freq = doc.count(term)
                if freq == 0:
                    continue
                denom = freq + self.k1 * (1 - self.b + self.b * self.doc_lens[i] / self.avgdl)
                scores[i] += idf * (freq * (self.k1 + 1)) / denom
        return scores


class BM25Retriever:
    def __init__(self, documents: list[Document]):
        self.documents = documents
        tokenized = [_tokenize(d.title + " " + d.text) for d in documents]
        try:
            from rank_bm25 import BM25Okapi

            self._bm25 = BM25Okapi(tokenized)
            self._backend = "rank_bm25"
        except Exception:
            self._bm25 = SimpleBM25(tokenized)
            self._backend = "simple_fallback"

    def search(self, query: str, top_k: int = 5) -> list[tuple[Document, float]]:
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(zip(self.documents, scores), key=lambda x: x[1], reverse=True)
        return [(doc, score) for doc, score in ranked[:top_k] if score > 0]
