from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .config import load_config
from .embeddings import get_embedder
from .indexer import build_index, get_status, query_index


mcp = FastMCP("rag-docs")


@mcp.tool()
def build_index_tool(
    docs_dir: str | None = None,
    data_dir: str | None = None,
    collection_name: str | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    embedding_backend: str | None = None,
    rebuild: bool = False,
) -> dict[str, object]:
    config = load_config()
    embedder = get_embedder(embedding_backend or config.embedding_backend)
    return build_index(
        docs_dir=Path(docs_dir) if docs_dir else config.docs_dir,
        data_dir=Path(data_dir) if data_dir else config.data_dir,
        collection_name=collection_name or config.collection_name,
        chunk_size=chunk_size if chunk_size is not None else config.chunk_size,
        chunk_overlap=chunk_overlap if chunk_overlap is not None else config.chunk_overlap,
        embedder=embedder,
        rebuild=rebuild,
    )


@mcp.tool()
def refresh_index_tool() -> dict[str, object]:
    config = load_config()
    embedder = get_embedder(config.embedding_backend)
    return build_index(
        docs_dir=config.docs_dir,
        data_dir=config.data_dir,
        collection_name=config.collection_name,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        embedder=embedder,
        rebuild=True,
    )


@mcp.tool()
def query_tool(
    query: str,
    data_dir: str | None = None,
    collection_name: str | None = None,
    top_k: int | None = None,
    embedding_backend: str | None = None,
) -> dict[str, object]:
    config = load_config()
    embedder = get_embedder(embedding_backend or config.embedding_backend)
    return query_index(
        query=query,
        data_dir=Path(data_dir) if data_dir else config.data_dir,
        collection_name=collection_name or config.collection_name,
        top_k=top_k if top_k is not None else config.top_k,
        embedder=embedder,
    )


@mcp.tool()
def status_tool(
    data_dir: str | None = None,
    collection_name: str | None = None,
) -> dict[str, object]:
    config = load_config()
    return get_status(
        data_dir=Path(data_dir) if data_dir else config.data_dir,
        collection_name=collection_name or config.collection_name,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
