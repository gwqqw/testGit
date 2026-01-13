from __future__ import annotations

from pathlib import Path

from rag_mcp.embeddings import SimpleKeywordEmbedder
from rag_mcp.indexer import build_index, query_index


def test_build_and_query_index(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    data_dir = tmp_path / "data"
    docs_dir.mkdir()

    (docs_dir / "alpha.txt").write_text("Alpha topic and shared term", encoding="utf-8")
    (docs_dir / "beta.txt").write_text("Beta topic only", encoding="utf-8")

    embedder = SimpleKeywordEmbedder()

    build_result = build_index(
        docs_dir=docs_dir,
        data_dir=data_dir,
        collection_name="test_docs",
        chunk_size=200,
        chunk_overlap=20,
        embedder=embedder,
        rebuild=True,
    )

    assert build_result["doc_count"] == 2
    assert build_result["chunk_count"] >= 2

    query_result = query_index(
        query="alpha topic",
        data_dir=data_dir,
        collection_name="test_docs",
        top_k=1,
        embedder=embedder,
    )

    assert query_result["results"]
    assert "Alpha" in query_result["results"][0]["content"]