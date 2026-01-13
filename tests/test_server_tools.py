from __future__ import annotations

from pathlib import Path

from rag_mcp.server import build_index_tool, query_tool, status_tool


def test_server_tools_workflow(tmp_path: Path, monkeypatch) -> None:
    docs_dir = tmp_path / "docs"
    data_dir = tmp_path / "data"
    docs_dir.mkdir()

    (docs_dir / "alpha.txt").write_text("Alpha content for server test", encoding="utf-8")

    monkeypatch.setenv("MCP_DOCS_DIR", str(docs_dir))
    monkeypatch.setenv("MCP_DATA_DIR", str(data_dir))
    monkeypatch.setenv("MCP_COLLECTION_NAME", "tool_docs")
    monkeypatch.setenv("MCP_EMBEDDING_BACKEND", "simple")

    build_result = build_index_tool(rebuild=True)
    assert build_result["doc_count"] == 1

    query_result = query_tool("alpha", top_k=1)
    assert query_result["results"]
    assert "Alpha content" in query_result["results"][0]["content"]

    status_result = status_tool()
    assert status_result["doc_count"] == 1