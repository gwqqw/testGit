from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument

from rag_mcp.documents import load_documents


def test_load_documents_from_txt_and_docx(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "alpha.txt").write_text("Alpha content", encoding="utf-8")

    docx_path = docs_dir / "beta.docx"
    doc = DocxDocument()
    doc.add_paragraph("Beta content")
    doc.save(docx_path)

    documents = load_documents(docs_dir)
    contents = {doc.content for doc in documents}

    assert len(documents) == 2
    assert "Alpha content" in contents
    assert "Beta content" in contents