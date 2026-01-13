from __future__ import annotations

import math
import os
import re
import zlib


DEFAULT_MODEL = "BAAI/bge-m3"


class Embedder:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is required for the default embedding backend"
            ) from exc

        self._model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]


class SimpleKeywordEmbedder(Embedder):
    def __init__(self, dim: int = 64) -> None:
        self._dim = dim
        self._pattern = re.compile(r"[A-Za-z0-9_]+")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            bucket = [0.0] * self._dim
            for token in self._pattern.findall(text.lower()):
                idx = zlib.adler32(token.encode("utf-8")) % self._dim
                bucket[idx] += 1.0
            norm = math.sqrt(sum(value * value for value in bucket))
            if norm > 0:
                bucket = [value / norm for value in bucket]
            vectors.append(bucket)
        return vectors


def get_embedder(backend: str | None = None) -> Embedder:
    backend_name = (backend or os.getenv("MCP_EMBEDDING_BACKEND", "sentence-transformer")).lower()
    if backend_name in {"sentence-transformer", "sentence", "st"}:
        return SentenceTransformerEmbedder()
    if backend_name in {"simple", "test"}:
        return SimpleKeywordEmbedder()
    raise ValueError(f"Unknown embedding backend: {backend_name}")