"""
src/api/routes.py — API route handlers for AskMANIT.

Routes:
    GET  /                 — Welcome message
    GET  /health           — Health check with ChromaDB stats
    POST /query            — Synchronous RAG query
    GET  /query/stream     — Server-Sent Events streaming RAG query
"""

from __future__ import annotations

import json
import time
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from src.api.schemas import (
    ErrorResponse,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    SourceChunk,
    LatencyBreakdown,
    TokenCounts,
)
from src.config import settings
from src.generation.rag_pipeline import get_pipeline
from src.retrieval.vector_store import get_vector_store

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

@router.get("/", tags=["General"])
async def root():
    """Welcome endpoint — confirms the API is running."""
    return {
        "message": "Welcome to the AskMANIT API",
        "docs": "/docs",
        "health": "/health",
        "query": "POST /query",
    }


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["General"],
    summary="Health check",
)
async def health(request: Request):
    """Return service health, document count, and config info."""
    startup_time: float = getattr(request.app.state, "startup_time", time.time())

    try:
        vs = get_vector_store()
        stats = vs.get_collection_stats()
        doc_count = stats["document_count"]
    except Exception:
        doc_count = -1

    return HealthResponse(
        status="ok",
        uptime_seconds=round(time.time() - startup_time, 2),
        document_count=doc_count,
        llm_provider=settings.effective_llm_provider,
        embedding_model=settings.embedding_model,
    )


# ---------------------------------------------------------------------------
# POST /query
# ---------------------------------------------------------------------------

@router.post(
    "/query",
    response_model=QueryResponse,
    tags=["RAG"],
    summary="Ask a question about MANIT academic policies",
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def query(body: QueryRequest):
    """
    Run the full RAG pipeline and return a structured response with citations.
    """
    pipeline = get_pipeline()
    try:
        result = pipeline.run_query(
            body.question,
            top_k_final=body.top_k,
            chat_history=body.chat_history,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    # Map raw dicts to Pydantic models
    sources = [
        SourceChunk(
            source_doc=s["source_doc"],
            page_number=s.get("page_number"),
            section_heading=s.get("section_heading", "N/A"),
            content=s["content"],
            reranker_score=s.get("reranker_score"),
        )
        for s in result["sources"]
    ]

    lb = result["latency_breakdown"]
    tc = result["token_counts"]

    return QueryResponse(
        answer=result["answer"],
        sources=sources,
        latency_breakdown=LatencyBreakdown(
            embed_retrieve_ms=lb["embed_retrieve_ms"],
            rerank_ms=lb["rerank_ms"],
            llm_ms=lb["llm_ms"],
            total_ms=lb["total_ms"],
        ),
        token_counts=TokenCounts(
            prompt_tokens=tc["prompt_tokens"],
            completion_tokens=tc["completion_tokens"],
            total_tokens=tc["total_tokens"],
        ),
    )


# ---------------------------------------------------------------------------
# GET /query/stream — Server-Sent Events streaming
# ---------------------------------------------------------------------------

@router.get(
    "/query/stream",
    tags=["RAG"],
    summary="Stream a RAG answer token-by-token via SSE",
    response_description="Server-Sent Events stream of answer tokens",
)
async def query_stream(question: str, top_k: int = 5):
    """
    Stream the LLM answer for a question using Server-Sent Events.

    Query parameters:
        question: The question to answer.
        top_k:    Number of chunks to retrieve.

    Returns:
        An SSE stream. Each event is a JSON object:
            {"type": "token",  "content": "<token text>"}
            {"type": "done",   "content": ""}
            {"type": "error",  "content": "<error message>"}
    """
    if len(question) < 3:
        raise HTTPException(status_code=422, detail="Question must be at least 3 characters.")

    pipeline = get_pipeline()

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            for token in pipeline.run_query_streaming(question, top_k_final=top_k):
                data = json.dumps({"type": "token", "content": token})
                yield f"data: {data}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
        except Exception as exc:
            error_data = json.dumps({"type": "error", "content": str(exc)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
