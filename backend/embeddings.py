"""Embedding provider wrapper around HuggingFaceInferenceAPIEmbeddings with a
deterministic local fallback (hashing-based) so the app works fully offline in demo mode.
"""
from __future__ import annotations

import hashlib

import numpy as np

from backend.config import settings

EMBEDDING_DIM = 384


def _hash_embedding(text: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    """Deterministic pseudo-embedding derived from token hashes (offline demo fallback).

    Not semantically meaningful like a real model, but stable and fast — good enough to
    demonstrate the RAG *pipelines* end-to-end without any network calls or GPU/API cost.
    """
    vec = np.zeros(dim, dtype=np.float32)
    for token in text.lower().split():
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


class EmbeddingProvider:
    """Unified embeddings interface.

    Uses `langchain_community.embeddings.HuggingFaceInferenceAPIEmbeddings` when real
    credentials are configured, otherwise falls back to a local deterministic embedding
    so the demo runs without any external dependency or cost.
    """

    def __init__(self) -> None:
        self._client = None
        if settings.has_hf_credentials:
            try:
                from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

                self._client = HuggingFaceInferenceAPIEmbeddings(
                    api_key=settings.huggingfacehub_api_token,
                    model_name=settings.hf_embedding_model,
                )
            except Exception:
                self._client = None  # graceful fallback if package/network unavailable

    @property
    def is_live(self) -> bool:
        return self._client is not None

    def embed_query(self, text: str) -> np.ndarray:
        if self._client is not None:
            return np.array(self._client.embed_query(text), dtype=np.float32)
        return _hash_embedding(text)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if self._client is not None:
            return np.array(self._client.embed_documents(texts), dtype=np.float32)
        return np.stack([_hash_embedding(t) for t in texts])


embedding_provider = EmbeddingProvider()
