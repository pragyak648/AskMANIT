"""
tests/test_retrieval.py — Unit tests for vector store and hybrid retrieval.
"""
import pytest
from src.retrieval.vector_store import get_vector_store
from src.retrieval.hybrid_search import get_hybrid_searcher
from src.retrieval.reranker import get_reranker


def test_vector_store_stats():
    """Verify vector store is populated and returns collection stats."""
    vs = get_vector_store()
    stats = vs.get_collection_stats()
    assert stats["document_count"] > 0
    assert stats["collection_name"] == "askmanit_docs"


def test_vector_store_similarity_search():
    """Verify vector similarity search returns matching chunks."""
    vs = get_vector_store()
    results = vs.similarity_search("attendance policy", k=3)
    assert len(results) > 0
    assert "page_number" in results[0].metadata


def test_hybrid_search():
    """Verify hybrid search returns fused candidates."""
    hs = get_hybrid_searcher()
    results = hs.hybrid_search("MCA entrance exam NIMCET", k=3)
    assert len(results) > 0
    contents = " ".join(r.page_content for r in results)
    assert "NIMCET" in contents or "MCA" in contents or "1988" in contents


def test_reranker():
    """Verify cross-encoder reranker scores and sorts chunks."""
    vs = get_vector_store()
    reranker = get_reranker()

    candidates = vs.similarity_search("hostel rules and curfew", k=5)
    assert len(candidates) > 0

    reranked = reranker.rerank("hostel rules and curfew", candidates, top_n=3)
    assert len(reranked) <= 3
    assert "reranker_score" in reranked[0].metadata

