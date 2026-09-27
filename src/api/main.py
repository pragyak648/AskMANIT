"""
src/api/main.py — FastAPI application entry point for AskMANIT.

Start the server:
    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import time
import json
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.api.routes import router
from src.config import settings, PROJECT_ROOT

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AskMANIT API",
    description=(
        "A RAG-powered chatbot API that answers questions about MANIT Bhopal's "
        "academic handbook, syllabus, and institutional policies — with citations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins for local development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup / Shutdown lifecycle
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup():
    """Record startup time and (optionally) pre-warm the pipeline."""
    app.state.startup_time = time.time()

    # Pre-warm: load embedder and vector store so the first query is fast
    try:
        from src.retrieval.vector_store import get_vector_store  # noqa: PLC0415
        vs = get_vector_store()
        stats = vs.get_collection_stats()
        print(
            f"[AskMANIT] ChromaDB ready — {stats['document_count']} chunks in collection."
        )
    except Exception as exc:
        print(f"[AskMANIT] Warning: could not pre-warm vector store: {exc}")


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    # Don't expose stack traces in production; log them server-side
    error_type = type(exc).__name__
    # Check for common LLM API errors
    if "AuthenticationError" in error_type or "APIStatusError" in error_type:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "LLM API error",
                "detail": f"{error_type}: Check your API key and provider settings.",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ---------------------------------------------------------------------------
# Per-request structured logging middleware
# ---------------------------------------------------------------------------

LOGS_DIR = Path(PROJECT_ROOT) / settings.logs_path


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    elapsed_ms = round((time.time() - t0) * 1000)

    # Log only /query POST requests in detail
    if request.url.path == "/query" and request.method == "POST":
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "total_ms": elapsed_ms,
        }
        try:
            with open(LOGS_DIR / "requests.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass  # Never fail a request because of logging

    return response


# ---------------------------------------------------------------------------
# Include routes
# ---------------------------------------------------------------------------
app.include_router(router)

# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
