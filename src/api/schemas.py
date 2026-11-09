"""
src/api/schemas.py — Pydantic request/response models for the AskMANIT API.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    """Request body for the /query endpoint."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The student's question about MANIT academic policies.",
        examples=["What is the minimum attendance to sit for exams?"],
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of source chunks to retrieve and return.",
    )
    chat_history: Optional[list[dict[str, str]]] = Field(
        default=None,
        description="Prior conversation turns for follow-up query contextualization.",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class SourceChunk(BaseModel):
    """A single retrieved source passage with its metadata."""

    source_doc: str = Field(..., description="Name of the source document (PDF stem).")
    page_number: Optional[int] = Field(None, description="Page number in the source PDF.")
    section_heading: str = Field("N/A", description="Section heading extracted from the page.")
    content: str = Field(..., description="Text snippet from this chunk (up to 500 chars).")
    reranker_score: Optional[float] = Field(
        None, description="Cross-encoder relevance score (higher = more relevant)."
    )


class LatencyBreakdown(BaseModel):
    """Per-stage latency in milliseconds."""

    embed_retrieve_ms: int = Field(..., description="Embedding + hybrid retrieval time (ms).")
    rerank_ms: int = Field(..., description="Cross-encoder reranking time (ms).")
    llm_ms: int = Field(..., description="LLM generation time (ms).")
    total_ms: int = Field(..., description="Total end-to-end latency (ms).")


class TokenCounts(BaseModel):
    """Token usage for the LLM call."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float = Field(
        default=0.0, description="Estimated dollar cost for prompt and completion tokens."
    )


class QueryResponse(BaseModel):
    """Response body from the /query endpoint."""

    answer: str = Field(..., description="The generated answer, with inline citations.")
    sources: list[SourceChunk] = Field(
        ..., description="Ranked list of source passages used to generate the answer."
    )
    latency_breakdown: LatencyBreakdown
    token_counts: TokenCounts


class HealthResponse(BaseModel):
    """Response body from the /health endpoint."""

    status: str = Field("ok", description="Service status.")
    uptime_seconds: float = Field(..., description="Seconds since the API started.")
    document_count: int = Field(..., description="Number of chunks in ChromaDB.")
    llm_provider: str = Field(..., description="Active LLM provider.")
    embedding_model: str = Field(..., description="Active embedding model.")


class ErrorResponse(BaseModel):
    """Standard error response body."""

    error: str = Field(..., description="Error message.")
    detail: Optional[str] = Field(None, description="Additional error context.")
