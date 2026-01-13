from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from .documents import Document, load_documents
from .embeddings import Embedder, get_embedder


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    content: str
    source_path: str
    index: int


class DocStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._docs: dict[str, dict[str, str]] = {}

    def load(self) -> None:
        if not self._path.exists():
            self._docs = {}
            return
        data = json.loads(self._path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            self._docs = data
        else:
            self._docs = {}

    def clear(self) -> None:
        self._docs = {}
        if self._path.exists():
            self._path.unlink()

    def add(self, document: Document) -> None:
        self._docs[document.doc_id] = {
            "path": document.path.as_posix(),
            "content": document.content,
        }

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._docs, ensure_ascii=True, indent=2), encoding="utf-8")

    def get(self, doc_id: str) -> dict[str, str] | None:
        return self._docs.get(doc_id)

    def count(self) -> int:
        return len(self._docs)


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    overlap = max(0, min(chunk_overlap, chunk_size - 1))
    chunks: list[str] = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = end - overlap
    return chunks


def _ensure_chroma_client(data_dir: Path):
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError as exc:
        raise RuntimeError("chromadb is required to store the vector index") from exc

    data_dir.mkdir(parents=True, exist_ok=True)
    settings = Settings(anonymized_telemetry=False)
    return chromadb.PersistentClient(path=str(data_dir), settings=settings)


def _create_collection(client, name: str):
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def _recreate_collection(client, name: str):
    try:
        client.delete_collection(name=name)
    except Exception:
        pass
    return client.create_collection(name=name, metadata={"hnsw:space": "cosine"})


def _build_chunks(documents: list[Document], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        for index, chunk in enumerate(chunk_text(document.content, chunk_size, chunk_overlap)):
            chunk_id = f"{document.doc_id}:{index}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    doc_id=document.doc_id,
                    content=chunk,
                    source_path=document.path.as_posix(),
                    index=index,
                )
            )
    return chunks


def build_index(
    docs_dir: Path,
    data_dir: Path,
    collection_name: str,
    chunk_size: int,
    chunk_overlap: int,
    embedder: Embedder | None = None,
    rebuild: bool = False,
) -> dict[str, object]:
    docs_dir = Path(docs_dir)
    data_dir = Path(data_dir)
    documents = load_documents(docs_dir)

    client = _ensure_chroma_client(data_dir)
    if rebuild:
        collection = _recreate_collection(client, collection_name)
    else:
        collection = _create_collection(client, collection_name)

    doc_store = DocStore(data_dir / "doc_store.json")
    if rebuild:
        doc_store.clear()
    else:
        doc_store.load()

    for document in documents:
        doc_store.add(document)
    doc_store.save()

    chunks = _build_chunks(documents, chunk_size, chunk_overlap)
    if not chunks:
        return {
            "docs_dir": docs_dir.as_posix(),
            "data_dir": data_dir.as_posix(),
            "collection": collection_name,
            "doc_count": len(documents),
            "chunk_count": 0,
        }

    embedder = embedder or get_embedder()
    embeddings = embedder.embed_texts([chunk.content for chunk in chunks])

    payload = {
        "ids": [chunk.chunk_id for chunk in chunks],
        "documents": [chunk.content for chunk in chunks],
        "metadatas": [
            {
                "doc_id": chunk.doc_id,
                "source_path": chunk.source_path,
                "chunk_index": chunk.index,
            }
            for chunk in chunks
        ],
        "embeddings": embeddings,
    }
    if hasattr(collection, "upsert"):
        collection.upsert(**payload)
    else:
        collection.add(**payload)

    return {
        "docs_dir": docs_dir.as_posix(),
        "data_dir": data_dir.as_posix(),
        "collection": collection_name,
        "doc_count": len(documents),
        "chunk_count": len(chunks),
    }


def query_index(
    query: str,
    data_dir: Path,
    collection_name: str,
    top_k: int,
    embedder: Embedder | None = None,
) -> dict[str, object]:
    data_dir = Path(data_dir)
    client = _ensure_chroma_client(data_dir)
    collection = _create_collection(client, collection_name)

    doc_store = DocStore(data_dir / "doc_store.json")
    doc_store.load()

    if doc_store.count() == 0:
        return {"query": query, "results": []}

    embedder = embedder or get_embedder()
    query_embedding = embedder.embed_texts([query])

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["metadatas", "distances"],
    )

    metadatas = results.get("metadatas", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    best_scores: dict[str, float] = {}
    for metadata, distance in zip(metadatas, distances):
        doc_id = metadata.get("doc_id") if metadata else None
        if not doc_id:
            continue
        current = best_scores.get(doc_id)
        if current is None or distance < current:
            best_scores[doc_id] = distance

    ranked = sorted(best_scores.items(), key=lambda item: item[1])[:top_k]
    response = []
    for doc_id, distance in ranked:
        stored = doc_store.get(doc_id)
        if not stored:
            continue
        response.append(
            {
                "doc_id": doc_id,
                "source_path": stored.get("path", ""),
                "score": 1.0 - distance,
                "content": stored.get("content", ""),
            }
        )

    return {"query": query, "results": response}


def get_status(data_dir: Path, collection_name: str) -> dict[str, object]:
    data_dir = Path(data_dir)
    doc_store = DocStore(data_dir / "doc_store.json")
    doc_store.load()

    client = _ensure_chroma_client(data_dir)
    collection = _create_collection(client, collection_name)

    return {
        "data_dir": data_dir.as_posix(),
        "collection": collection_name,
        "doc_count": doc_store.count(),
        "chunk_count": collection.count(),
    }
