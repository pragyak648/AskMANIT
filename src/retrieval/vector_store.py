"""
src/retrieval/vector_store.py — ChromaDB vector store wrapper for AskMANIT.

Provides a persistent, file-based ChromaDB store backed by BGE embeddings.

Key operations:
    add_documents(docs)          — Upsert LangChain Documents (idempotent via chunk_id)
    similarity_search(query, k)  — Top-k vector similarity search
    get_collection_stats()       — Count and collection info

Usage:
    from src.retrieval.vector_store import VectorStore
    vs = VectorStore()
    vs.add_documents(docs)
    results = vs.similarity_search("attendance policy", k=10)
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import settings
from src.ingestion.embedder import get_embedder

_COLLECTION_NAME = "askmanit_docs"


class VectorStore:
    """
    Thin wrapper around a persistent ChromaDB Chroma LangChain integration.

    The store is persisted at settings.chroma_db_dir. Documents are upserted
    using their chunk_id as the ChromaDB document ID, so re-ingestion is safe.
    """

    def __init__(
        self,
        persist_dir: str | Path | None = None,
        collection_name: str = _COLLECTION_NAME,
    ):
        self._persist_dir = Path(persist_dir or settings.chroma_db_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._collection_name = collection_name
        self._embedder = get_embedder()
        self._db: Chroma | None = None

    def _get_db(self) -> Chroma:
        if self._db is None:
            self._db = Chroma(
                collection_name=self._collection_name,
                embedding_function=self._embedder,
                persist_directory=str(self._persist_dir),
            )
        return self._db

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add_documents(self, docs: list[Document]) -> int:
        """
        Upsert documents into ChromaDB.

        Uses each document's metadata['chunk_id'] as the ChromaDB document ID,
        so re-running is idempotent (existing chunks are overwritten, not duplicated).

        Args:
            docs: List of LangChain Documents (must have 'chunk_id' in metadata).

        Returns:
            Number of documents upserted.
        """
        if not docs:
            return 0

        db = self._get_db()
        ids = [doc.metadata["chunk_id"] for doc in docs]

        # Chroma's add_documents with ids performs upsert behaviour
        db.add_documents(documents=docs, ids=ids)
        return len(docs)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def similarity_search(
        self,
        query: str,
        k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[Document]:
        """
        Retrieve top-k most similar documents for a query.

        Args:
            query:  The user question.
            k:      Number of results (defaults to settings.top_k_vector).
            filter: Optional ChromaDB metadata filter dict.

        Returns:
            List of Documents ordered by descending similarity.
        """
        k = k or settings.top_k_vector
        db = self._get_db()
        return db.similarity_search(query=query, k=k, filter=filter)

    def similarity_search_with_score(
        self,
        query: str,
        k: int | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[tuple[Document, float]]:
        """
        Like similarity_search but also returns scores.

        Returns:
            List of (Document, score) tuples — lower score = more similar
            (ChromaDB uses L2 distance by default).
        """
        k = k or settings.top_k_vector
        db = self._get_db()
        return db.similarity_search_with_score(query=query, k=k, filter=filter)

    def get_all_documents(self) -> list[Document]:
        """
        Retrieve ALL documents from the collection (useful for BM25 index build).

        Returns:
            List of all stored Documents.
        """
        db = self._get_db()
        result = db.get(include=["documents", "metadatas"])
        docs = []
        for content, meta in zip(result["documents"], result["metadatas"]):
            docs.append(Document(page_content=content, metadata=meta))
        return docs

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_collection_stats(self) -> dict[str, Any]:
        """Return basic statistics about the collection."""
        db = self._get_db()
        count = db._collection.count()
        return {
            "collection_name": self._collection_name,
            "document_count": count,
            "persist_dir": str(self._persist_dir),
        }

    def reset_collection(self) -> None:
        """Delete and recreate the collection (WARNING: destroys all data)."""
        db = self._get_db()
        db.delete_collection()
        self._db = None


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_vs_instance: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Return (or create) the shared VectorStore singleton."""
    global _vs_instance
    if _vs_instance is None:
        _vs_instance = VectorStore()
    return _vs_instance


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    vs = VectorStore()
    stats = vs.get_collection_stats()
    print(f"Collection: {stats['collection_name']}")
    print(f"Documents : {stats['document_count']}")
    print(f"Persist   : {stats['persist_dir']}")

    if stats["document_count"] > 0:
        t0 = time.time()
        results = vs.similarity_search("attendance policy", k=3)
        elapsed = (time.time() - t0) * 1000
        print(f"\nTop-3 results for 'attendance policy' ({elapsed:.0f}ms):")
        for i, doc in enumerate(results, 1):
            print(f"  [{i}] p{doc.metadata['page_number']} — {doc.page_content[:100]}…")
