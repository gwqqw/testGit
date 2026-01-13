from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class ServerConfig:
    docs_dir: Path
    data_dir: Path
    collection_name: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    embedding_backend: str


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_config() -> ServerConfig:
    docs_dir = Path(os.getenv("MCP_DOCS_DIR", "docs"))
    data_dir = Path(os.getenv("MCP_DATA_DIR", "data"))
    collection_name = os.getenv("MCP_COLLECTION_NAME", "rag_docs")
    chunk_size = _env_int("MCP_CHUNK_SIZE", 1200)
    chunk_overlap = _env_int("MCP_CHUNK_OVERLAP", 200)
    top_k = _env_int("MCP_TOP_K", 3)
    embedding_backend = os.getenv("MCP_EMBEDDING_BACKEND", "sentence-transformer")
    return ServerConfig(
        docs_dir=docs_dir,
        data_dir=data_dir,
        collection_name=collection_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=top_k,
        embedding_backend=embedding_backend,
    )