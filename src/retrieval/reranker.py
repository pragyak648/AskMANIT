"""
src/retrieval/reranker.py — Cross-encoder reranker for AskMANIT.

Uses cross-encoder/ms-marco-MiniLM-L-6-v2 to rerank retrieval candidates
by computing a relevance score for each (query, document) pair.

Unlike bi-encoder embeddings, cross-encoders see both the query AND the
document simultaneously, yielding much higher relevance precision at the
cost of O(N) inference calls per query.

Usage:
    from src.retrieval.reranker import Reranker
    reranker = Reranker()
    top_docs = reranker.rerank("attendance policy", docs, top_n=5)
"""

from __future__ import annotations

from typing import NamedTuple

from langchain_core.documents import Document

from src.config import settings


class RankedDocument(NamedTuple):
    """A document with its reranker relevance score."""

    document: Document
    score: float


class Reranker:
    """
    Cross-encoder reranker using sentence-transformers.

    Scores every (query, chunk) pair and returns the top_n chunks
    sorted by descending relevance score.
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.reranker_model
        self._model = None  # lazy-loaded

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder  # noqa: PLC0415
            except ImportError as e:
                raise ImportError(
                    "sentence-transformers is required: pip install sentence-transformers"
                ) from e
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_n: int | None = None,
    ) -> list[Document]:
        """
        Rerank documents by cross-encoder relevance to the query.

        Args:
            query:     The user question.
            documents: Candidate documents from retrieval.
            top_n:     Number of top documents to return (defaults to
                       settings.top_k_final).

        Returns:
            List of the top_n most relevant Documents, sorted best-first.
        """
        top_n = top_n or settings.top_k_final

        if not documents:
            return []

        model = self._load_model()

        # Build (query, passage) pairs for cross-encoder scoring
        pairs = [(query, doc.page_content) for doc in documents]
        scores: list[float] = model.predict(pairs).tolist()

        # Pair documents with scores and sort descending
        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        # Attach reranker score to metadata for downstream use/logging
        result = []
        for doc, score in ranked[:top_n]:
            doc_copy = Document(
                page_content=doc.page_content,
                metadata={**doc.metadata, "reranker_score": round(score, 6)},
            )
            result.append(doc_copy)

        return result

    def rerank_with_scores(
        self,
        query: str,
        documents: list[Document],
        top_n: int | None = None,
    ) -> list[RankedDocument]:
        """
        Like rerank() but also returns the scores as named tuples.

        Returns:
            List of RankedDocument(document, score), best-first.
        """
        top_n = top_n or settings.top_k_final

        if not documents:
            return []

        model = self._load_model()
        pairs = [(query, doc.page_content) for doc in documents]
        scores: list[float] = model.predict(pairs).tolist()

        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return [RankedDocument(doc, score) for doc, score in ranked[:top_n]]


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_reranker_instance: Reranker | None = None


def get_reranker() -> Reranker:
    """Return (or create) the shared Reranker singleton."""
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = Reranker()
    return _reranker_instance


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from src.retrieval.vector_store import get_vector_store

    query = "What is the minimum attendance to sit for exams?"
    vs = get_vector_store()
    stats = vs.get_collection_stats()

    if stats["document_count"] == 0:
        print("No documents in ChromaDB. Run scripts/ingest.py first.")
    else:
        candidates = vs.similarity_search(query, k=10)
        reranker = Reranker()
        top_docs = reranker.rerank(query, candidates, top_n=5)

        print(f"Query: {query!r}")
        print(f"Candidates: {len(candidates)} → Reranked top 5:")
        for i, doc in enumerate(top_docs, 1):
            score = doc.metadata.get("reranker_score", "?")
            print(
                f"  [{i}] score={score:.4f} | p{doc.metadata['page_number']} | "
                f"{doc.page_content[:120]!r}"
            )
