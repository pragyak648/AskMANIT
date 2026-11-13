"""
tests/test_api.py — API route, schema, and integration tests for AskMANIT.
"""
import pytest
from pydantic import ValidationError

from src.api.main import app
from src.api.schemas import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    SourceChunk,
    LatencyBreakdown,
    TokenCounts,
)


def test_app_metadata_and_routes():
    """Verify FastAPI application has correct title, docs, and registered routes."""
    assert app.title == "AskMANIT API"
    route_paths = [r.path for r in app.routes]
    assert "/" in route_paths
    assert "/health" in route_paths
    assert "/query" in route_paths
    assert "/query/stream" in route_paths


def test_query_request_validation():
    """Verify QueryRequest enforces validation constraints."""
    # Valid request
    req = QueryRequest(question="What is the attendance policy?", top_k=5)
    assert req.question == "What is the attendance policy?"
    assert req.top_k == 5

    # Question too short (< 3 chars)
    with pytest.raises(ValidationError):
        QueryRequest(question="hi")

    # Empty question
    with pytest.raises(ValidationError):
        QueryRequest(question="")

    # top_k out of bounds (> 20)
    with pytest.raises(ValidationError):
        QueryRequest(question="Valid question here", top_k=25)

    # top_k out of bounds (< 1)
    with pytest.raises(ValidationError):
        QueryRequest(question="Valid question here", top_k=0)


def test_query_response_schema():
    """Verify QueryResponse properly serializes with required fields."""
    source = SourceChunk(
        source_doc="manit_student_handbook_2026",
        page_number=7,
        section_heading="8. MCA at MANIT Bhopal",
        content="The MCA is 3 years in duration...",
        reranker_score=0.92,
    )
    latency = LatencyBreakdown(
        embed_retrieve_ms=100,
        rerank_ms=50,
        llm_ms=200,
        total_ms=350,
    )
    tokens = TokenCounts(
        prompt_tokens=150,
        completion_tokens=50,
        total_tokens=200,
    )
    res = QueryResponse(
        answer="The MCA program is 3 years long.",
        sources=[source],
        latency_breakdown=latency,
        token_counts=tokens,
    )

    assert res.answer.startswith("The MCA")
    assert len(res.sources) == 1
    assert res.sources[0].page_number == 7
    assert res.latency_breakdown.total_ms == 350
    assert res.token_counts.total_tokens == 200


def test_health_response_schema():
    """Verify HealthResponse schema validation."""
    health = HealthResponse(
        status="ok",
        uptime_seconds=12.5,
        document_count=31,
        llm_provider="anthropic",
        embedding_model="BAAI/bge-small-en-v1.5",
    )
    assert health.status == "ok"
    assert health.document_count == 31
