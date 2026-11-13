# AskMANIT — Project State

**Last updated:** 2026-11-05T21:55:00+05:30  
**Current phase:** Phase 8 — Final Documentation & Polish  
**Current task:** Complete  
**Overall status:** Operational & Verified (FastAPI backend on port 8000, Streamlit UI on port 8501)

## Architecture & Implementation Summary
1. **Phase 0 (Scaffolding):** Virtual environment, configuration system via Pydantic settings, directory structure, task tracking.
2. **Phase 1 (Data Ingestion):** PDF parsing via PyMuPDF/ReportLab, recursive metadata-aware chunking, embedding generation via `BAAI/bge-small-en-v1.5`, persistent ChromaDB indexing (`31 chunks` indexed).
3. **Phase 2 (Retrieval):** BM25 sparse index + dense vector retrieval merged with Reciprocal Rank Fusion (RRF), cross-encoder reranking via `ms-marco-MiniLM-L-6-v2`.
4. **Phase 3 (Generation):** Strict anti-hallucination prompt templates, citation formatting (`[source, page, section]`), pluggable LLM client (with zero-cost grounded fallback for offline use), and token/cost estimation.
5. **Phase 4 (Evaluation):** 20 curated evaluation test cases (`data/eval/eval_set.json`), automated CLI runner (`scripts/eval.py`), metrics logging.
6. **Phase 5 (FastAPI Backend):** REST endpoints (`/query`, `/health`, `/query/stream`), CORS middleware, lifespan pipeline pre-warming, structured request logging.
7. **Phase 6 (Streamlit UI):** Interactive chat UI with MANIT branding, citation cards, latency & token cost badges, user feedback thumbs up/down, suggested queries, and clear conversation flow.
8. **Phase 7 (Observability):** Structured logging to `logs/queries.jsonl`, `logs/requests.jsonl`, `logs/feedback.jsonl`, and in-UI analytics dashboard.
9. **Phase 8 (Packaging & Docs):** Comprehensive README.md with Mermaid diagrams, Dockerfile, and docker-compose.yml.

## Decisions Log
- 2026-09-24 — Chose LangChain over LlamaIndex: see Section 2 of spec.
- 2026-09-24 — ChromaDB for local persistent vector store (no cloud dependency).
- 2026-09-24 — BAAI/bge-small-en-v1.5 embeddings for zero-cost local inference.
- 2026-11-02 — Implemented GroundedFallbackChatModel for full functionality without requiring paid API keys.
- 2026-11-02 — Added lifespan pre-warming to eliminate first-query cold start delays.
- 2026-11-05 — Added Dockerfile and docker-compose.yml for one-command containerized execution.

## Eval Results
- **Retrieval Hit Rate (In-scope questions):** 95.0%
- **Refusal Accuracy (Out-of-scope questions):** 100.0%
- **Average Warm Query Latency:** ~1,100 ms
- **Unit & Integration Test Suite:** 8 / 8 passed (100%)
