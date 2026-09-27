"""
src/retrieval/hybrid_search.py — Hybrid retrieval for AskMANIT.

Combines:
  1. Dense vector search  — ChromaDB + BGE embeddings
  2. Sparse keyword search — BM25 (rank-bm25) over all indexed documents

Results are merged via Reciprocal Rank Fusion (RRF), which is robust to
score distribution differences between the two retrieval systems.

Usage:
    from src.retrieval.hybrid_search import HybridSearcher
    searcher = HybridSearcher()
    results = searcher.hybrid_search("attendance requirement", k=5)
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from langchain_core.documents import Document

from src.config import settings
from src.retrieval.vector_store import get_vector_store


# ---------------------------------------------------------------------------
# RRF constants
# ---------------------------------------------------------------------------
_RRF_K = 60  # Standard RRF constant (per Cormack et al., 2009)


def _rrf_score(rank: int, k: int = _RRF_K) -> float:
    """Reciprocal rank fusion score for a document at the given rank."""
    return 1.0 / (k + rank)


# ---------------------------------------------------------------------------
# BM25 index builder
# ---------------------------------------------------------------------------

class _BM25Index:
    """Thin wrapper around rank-bm25's BM25Okapi for the full corpus."""

    def __init__(self, docs: list[Document]):
        try:
            from rank_bm25 import BM25Okapi  # noqa: PLC0415
        except ImportError as e:
            raise ImportError(
                "rank-bm25 is required: pip install rank-bm25"
            ) from e

        self._docs = docs
        tokenized = [doc.page_content.lower().split() for doc in docs]
        self._bm25 = BM25Okapi(tokenized)

    def search(self, query: str, k: int) -> list[tuple[Document, float]]:
        """
        Search the BM25 index.

        Returns:
            List of (Document, bm25_score) sorted descending by score.
        """
        if not self._docs:
            return []
        tokens = query.lower().split()
        scores = self._bm25.get_scores(tokens)
        # Pair docs with scores and sort
        paired = list(zip(self._docs, scores))
        paired.sort(key=lambda x: x[1], reverse=True)
        return paired[:k]


# ---------------------------------------------------------------------------
# Main HybridSearcher
# ---------------------------------------------------------------------------

class HybridSearcher:
    """
    Hybrid retriever combining dense vector search and BM25.

    The BM25 index is built lazily over all documents currently in ChromaDB.
    Call refresh_bm25_index() after new documents are ingested.
    """

    def __init__(self):
        self._vs = get_vector_store()
        self._bm25_index: _BM25Index | None = None

    def _get_bm25_index(self) -> _BM25Index:
        if self._bm25_index is None:
            self.refresh_bm25_index()
        return self._bm25_index  # type: ignore[return-value]

    def refresh_bm25_index(self) -> int:
        """Rebuild the BM25 index from all documents in ChromaDB."""
        all_docs = self._vs.get_all_documents()
        self._bm25_index = _BM25Index(all_docs)
        return len(all_docs)

    def hybrid_search(
        self,
        query: str,
        k: int | None = None,
        vector_k: int | None = None,
    ) -> list[Document]:
        """
        Retrieve the top-k most relevant documents using hybrid RRF fusion.

        Args:
            query:    The user question.
            k:        Number of final results (defaults to settings.top_k_final).
            vector_k: Candidates fetched from each retriever before fusion
                      (defaults to settings.top_k_vector).

        Returns:
            List of Documents sorted by RRF score (most relevant first).
        """
        k = k or settings.top_k_final
        vector_k = vector_k or settings.top_k_vector

        # 1. Dense vector retrieval
        try:
            vector_results = self._vs.similarity_search(query, k=vector_k)
        except Exception:
            vector_results = []

        # 2. BM25 sparse retrieval
        try:
            bm25_index = self._get_bm25_index()
            bm25_results_with_scores = bm25_index.search(query, k=vector_k)
            bm25_results = [doc for doc, _ in bm25_results_with_scores]
        except Exception:
            bm25_results = []

        # 3. Reciprocal Rank Fusion
        merged = _reciprocal_rank_fusion(
            [vector_results, bm25_results],
            k=k,
        )
        return merged


def _reciprocal_rank_fusion(
    result_lists: list[list[Document]],
    k: int,
) -> list[Document]:
    """
    Merge multiple ranked document lists using RRF.

    Documents are identified by their chunk_id metadata. The score for each
    document is the sum of its RRF scores across all result lists.

    Args:
        result_lists: Each element is a ranked list of Documents.
        k:            Number of documents to return.

    Returns:
        Deduplicated, RRF-sorted list of top-k Documents.
    """
    rrf_scores: dict[str, float] = defaultdict(float)
    # Map chunk_id → Document for the final output
    id_to_doc: dict[str, Document] = {}

    for result_list in result_lists:
        for rank, doc in enumerate(result_list, start=1):
            chunk_id = doc.metadata.get("chunk_id", "")
            if not chunk_id:
                # Fallback key: use first 100 chars of content
                chunk_id = doc.page_content[:100]
            rrf_scores[chunk_id] += _rrf_score(rank)
            if chunk_id not in id_to_doc:
                id_to_doc[chunk_id] = doc

    # Sort by RRF score descending
    sorted_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)
    return [id_to_doc[cid] for cid in sorted_ids[:k]]


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_searcher_instance: HybridSearcher | None = None


def get_hybrid_searcher() -> HybridSearcher:
    """Return (or create) the shared HybridSearcher singleton."""
    global _searcher_instance
    if _searcher_instance is None:
        _searcher_instance = HybridSearcher()
    return _searcher_instance


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "attendance requirement"
    print(f"Hybrid search: '{query}'")

    searcher = HybridSearcher()
    results = searcher.hybrid_search(query, k=5)

    print(f"Top {len(results)} results:")
    for i, doc in enumerate(results, 1):
        meta = doc.metadata
        print(
            f"  [{i}] p{meta.get('page_number')} — "
            f"{meta.get('source_doc')} — "
            f"{doc.page_content[:120]!r}"
        )
