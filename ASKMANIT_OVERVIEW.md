# AskMANIT — Project Documentation

> **A Retrieval-Augmented Generation (RAG) Chatbot for MANIT Bhopal Academic Handbook**
> *Grounded answers with verified citations — not hallucinations.*

---

## Table of Contents

1. [Project Introduction](#1-project-introduction)
2. [Objectives](#2-objectives)
3. [System Architecture](#3-system-architecture)
4. [Pipeline Overview](#4-pipeline-overview)
5. [Technology Stack](#5-technology-stack)
6. [Methodology and Data Flow](#6-methodology-and-data-flow)
7. [Module Breakdown](#7-module-breakdown)
8. [Running the Project](#8-running-the-project)

---

## 1. Project Introduction

**AskMANIT** is an AI-powered question-answering system built for students of **Maulana Azad National Institute of Technology (MANIT), Bhopal**. It leverages **Retrieval-Augmented Generation (RAG)** — combining semantic document search with large language model reasoning — to deliver precise, verifiable answers from official institutional documents.

### The Problem It Solves

Students routinely search through 100+ page handbooks for policies on attendance, credits, backlogs, and hostel rules. Word-of-mouth answers are often outdated or incorrect.

**AskMANIT solves this by:**
- Ingesting official MANIT PDFs into a persistent vector database
- Answering student questions using hybrid search + LLM generation
- Grounding every answer in specific **page and section citations**
- Refusing to answer out-of-scope questions rather than hallucinating

---

## 2. Objectives

| # | Objective | Status |
|---|---|---|
| 1 | Ingest MANIT academic PDFs into a searchable vector store | Done |
| 2 | Build hybrid retrieval combining dense vector search + BM25 keyword matching | Done |
| 3 | Apply cross-encoder reranking to improve retrieval precision | Done |
| 4 | Generate context-grounded answers with in-text citations via LLM | Done |
| 5 | Expose a FastAPI REST backend with /query, /query/stream, and /health | Done |
| 6 | Build an interactive Streamlit chat UI with expandable source citations | Done |
| 7 | Log feedback, latency metrics, and token costs locally | Done |
| 8 | Evaluate retrieval quality using ragas metrics | Planned |
| 9 | Add Docker Compose for one-command startup | Planned |

---

## 3. System Architecture

### Ingestion Pipeline (Offline)

`
Raw PDFs (data/raw/)
     |
     v
  Parser (PyMuPDF / unstructured)
     |
     v
  Chunker (LangChain RecursiveCharacterTextSplitter)
     |
     v
  Embedder (BAAI/bge-small-en-v1.5)
     |
     v
  ChromaDB (Persistent at data/chroma_db/)
`

### Query Pipeline (Online)

`
User Question
     |
     v
Hybrid Retrieval (RRF Fusion)
  [Vector Search (ChromaDB/BGE)]  +  [BM25 Search (rank-bm25)]
                   |
          Reciprocal Rank Fusion
     |
     v
Cross-Encoder Reranker
(cross-encoder/ms-marco-MiniLM-L-6-v2)
     |
     v
Prompt Assembly
(System Prompt + Ranked Context + User Question)
     |
     v
LLM Generation
(Claude / OpenAI GPT-4o-mini / Ollama / Fallback)
     |
     v
Answer + Citations + Latency Breakdown
     |
  +--+--+--+
  |     |   |
FastAPI Streamlit Local Logs
(8000) (8501) (logs/*.jsonl)
`

### Architecture Highlights

| Component | Design Decision | Rationale |
|---|---|---|
| ChromaDB | Local, persistent, file-based | No cloud dependency; zero cost during development |
| Hybrid Search | Vector + BM25 via RRF | Captures both semantic similarity and keyword relevance |
| Cross-encoder Reranker | ms-marco-MiniLM-L-6-v2 | Re-scores top candidates for precision; free, local inference |
| LLM | Pluggable via .env config | Works with OpenAI, Anthropic, Ollama, or a no-API fallback |
| Streamlit | Frontend choice for v1 | Fastest path to a demoable, production-like chat UI |
| FastAPI | Backend API | Async, auto-docs, streaming support, resume-relevant |

---

## 4. Pipeline Overview

### 4.1 Ingestion Pipeline (Offline — Run Once)

**Step 1: PARSE**
- Input: Official MANIT PDFs in data/raw/
- Tool: PyMuPDF (fitz) for text; unstructured for table-heavy pages
- Output: List of page dicts: {text, page_number, source_doc, has_table}

**Step 2: CHUNK**
- Input: Page dicts from parser
- Tool: LangChain RecursiveCharacterTextSplitter
- Params: chunk_size=600 tokens, chunk_overlap=100 tokens
- Output: LangChain Documents with metadata: {chunk_id, source_doc, page_number, section_heading}

**Step 3: EMBED**
- Input: LangChain Documents
- Model: BAAI/bge-small-en-v1.5 (384-dim, local inference via sentence-transformers)
- Output: Float32 vectors per chunk

**Step 4: STORE**
- Input: Documents + Vectors
- Store: ChromaDB (persistent at data/chroma_db)
- Key: chunk_id used as document ID — enables idempotent re-ingestion

### 4.2 Query Pipeline (Online — Per User Request)

**Step 1: EMBED QUERY**
- Input: User question string
- Model: BAAI/bge-small-en-v1.5 (same model as ingestion)
- Output: 384-dim query vector

**Step 2: HYBRID SEARCH**
- Sub-step A: Dense Vector Search — Query ChromaDB for top-K similar chunks
- Sub-step B: BM25 Keyword Search — Query BM25 index built from all ChromaDB docs
- Merge via Reciprocal Rank Fusion (RRF): combines and deduplicates both result lists
- Output: Top-K merged candidate chunks

**Step 3: CROSS-ENCODER RERANK**
- Input: User question + top-K candidate chunks
- Model: cross-encoder/ms-marco-MiniLM-L-6-v2
- Output: Top-N chunks sorted by cross-encoder relevance score

**Step 4: PROMPT ASSEMBLY**
- Input: Reranked chunks + user question
- Format: Numbered context blocks with source metadata + system instructions
- System constraint: Answer ONLY from context, cite page/section, refuse if not found

**Step 5: LLM GENERATION**
- Input: [SystemMessage, HumanMessage] prompt
- LLM: OpenAI GPT-4o-mini / Anthropic Claude / Ollama Llama3 / Local Fallback
- Output: Answer text with in-line [Source: doc, Page N, Section S] citations

**Step 6: LOG AND RESPOND**
- Logs: logs/queries.jsonl (timestamp, question, latency_breakdown, token_counts)
- Return: {answer, sources[], latency_breakdown, token_counts}

---

## 5. Technology Stack

### Core Frameworks

| Layer | Technology | Version | Role |
|---|---|---|---|
| Orchestration | LangChain + LangChain-Community | 0.3.7 | Chain/pipeline construction, LLM abstraction |
| Vector Store | ChromaDB | 0.5.18 | Persistent local vector database |
| Vector Integration | langchain-chroma | 0.2.3 | LangChain <-> ChromaDB bridge |

### AI / ML Models

| Model | Provider | Dimensions | Role |
|---|---|---|---|
| BAAI/bge-small-en-v1.5 | HuggingFace (local) | 384 | Dense embedding for documents and queries |
| cross-encoder/ms-marco-MiniLM-L-6-v2 | HuggingFace (local) | - | Cross-encoder relevance reranking |
| gpt-4o-mini | OpenAI (cloud, optional) | - | LLM generation |
| claude-3-5-haiku | Anthropic (cloud, optional) | - | LLM generation |
| llama3 | Ollama (local, optional) | - | Free local LLM generation |

### Retrieval and Search

| Technology | Purpose |
|---|---|
| sentence-transformers | Local embedding and reranking model inference |
| rank-bm25 (BM25Okapi) | Sparse keyword retrieval (BM25 algorithm) |
| Reciprocal Rank Fusion (RRF) | Score merging across vector + BM25 result lists |

### Document Processing

| Technology | Purpose |
|---|---|
| pymupdf (fitz) | Fast text extraction from PDFs |
| unstructured | Structure-aware extraction for table-heavy pages |
| LangChain RecursiveCharacterTextSplitter | Semantic chunking with overlap |

### Backend API

| Technology | Purpose |
|---|---|
| FastAPI 0.115.4 | Async REST API with auto-docs |
| uvicorn 0.32.0 | ASGI server |
| pydantic 2.9.2 | Request/response validation |
| pydantic-settings 2.6.1 | Typed environment variable loading |

### Frontend

| Technology | Purpose |
|---|---|
| streamlit 1.40.1 | Interactive chat web UI |
| requests | HTTP client for backend communication |

### Evaluation and Testing

| Technology | Purpose |
|---|---|
| ragas 0.2.5 | RAG evaluation: faithfulness, context precision, answer relevancy |
| pytest 8.3.3 | Unit and integration testing |
| httpx 0.27.2 | Async HTTP client for API testing |

---

## 6. Methodology and Data Flow

### 6.1 Chunking Strategy

1. PyMuPDF extracts plain text per page from PDFs
2. Table-heavy pages route through unstructured (hi-res strategy)
3. Text passes through RecursiveCharacterTextSplitter (separators: paragraph, line, space)
4. chunk_size = 600 tokens captures a coherent policy clause
5. chunk_overlap = 100 tokens preserves context at chunk boundaries
6. Each chunk gets a deterministic chunk_id for upsert idempotency: {source_doc}_p{page}_c{idx}

### 6.2 Embedding and Indexing

- Text chunks encoded by sentence-transformers into 384-dimensional L2-normalised float32 vectors
- Vectors upserted into ChromaDB using chunk_id as document ID
- ChromaDB persists to data/chroma_db/ across restarts
- Re-running ingest.py does NOT duplicate documents (idempotent by design)

### 6.3 Hybrid Search via Reciprocal Rank Fusion

Both retrieval methods run in parallel on the same query:

- **Dense Vector Search**: BGE embedding -> ChromaDB ANN search -> ranked document list A
- **BM25 Keyword Search**: Tokenized query -> BM25Okapi scores -> ranked document list B

RRF merges these lists: rf_score(doc) += 1 / (60 + rank)

Documents in both lists get cumulative scores. Deduplicated and sorted by total RRF score.

**Why RRF?** Robust to score-scale mismatches between cosine distances and BM25 term frequencies. No weight-interpolation tuning required.

### 6.4 Cross-Encoder Reranking

The cross-encoder jointly encodes the question and each candidate passage together, producing a single relevance score — far more accurate than bi-encoder cosine similarity:

`
Hybrid candidates (top-10)
  |
  v
CrossEncoder.predict([(question, chunk_1), ..., (question, chunk_10)])
  |
  v
Sort by score descending -> Return top-5 reranked chunks
`

### 6.5 Prompt Design

The system prompt enforces three hard constraints:

1. **Grounding**: Answer ONLY from the provided context passages. Never use general knowledge.
2. **Citation**: Cite every claim with [Source: document_name, Page N, Section: heading]
3. **Refusal**: If the answer is NOT in the context, refuse with a standard message rather than hallucinating.

### 6.6 Response Schema

`json
{
  "answer": "Answer text with inline citations...",
  "sources": [
    {
      "source_doc": "manit_academic_regulations",
      "page_number": 1,
      "section_heading": "Section 1: Attendance Requirements",
      "content": "1.1 Minimum Attendance: Every student must maintain...",
      "reranker_score": 0.912
    }
  ],
  "latency_breakdown": {
    "embed_retrieve_ms": 320,
    "rerank_ms": 45,
    "llm_ms": 1800,
    "total_ms": 2165
  },
  "token_counts": {
    "prompt_tokens": 1250,
    "completion_tokens": 280,
    "total_tokens": 1530
  }
}
`

### 6.7 Logging and Observability

`
logs/
+-- queries.jsonl      per-query: timestamp, question, chunk_ids, latency, token counts
+-- requests.jsonl     per-HTTP-request: path, status_code, total_ms
+-- feedback.jsonl     per-feedback: timestamp, question, answer, thumbs up/down rating
`

---

## 7. Module Breakdown

`
src/
+-- config.py                    Typed settings from .env via pydantic-settings
+-- ingestion/
|   +-- parser.py                PDF -> page dicts (PyMuPDF + unstructured)
|   +-- chunker.py               Page dicts -> LangChain Documents with metadata
|   +-- embedder.py              BGE wrapper, LangChain Embeddings interface
+-- retrieval/
|   +-- vector_store.py          ChromaDB wrapper: add, search, stats, reset
|   +-- hybrid_search.py         BM25 index + RRF fusion over vector + BM25 results
|   +-- reranker.py              Cross-encoder reranker (ms-marco-MiniLM-L-6-v2)
+-- generation/
|   +-- llm_client.py            Pluggable LLM factory (Anthropic/OpenAI/Ollama/Fallback)
|   +-- prompt_templates.py      System prompt + context formatter + build_prompt()
|   +-- rag_pipeline.py          End-to-end: search -> rerank -> prompt -> LLM -> response
+-- api/
|   +-- main.py                  FastAPI app, CORS, error handlers, logging middleware
|   +-- routes.py                GET /, GET /health, POST /query, GET /query/stream
|   +-- schemas.py               Pydantic models: QueryRequest, QueryResponse, SourceChunk
+-- eval/
    +-- run_eval.py              (Phase 4) ragas evaluation runner

frontend/
+-- streamlit_app.py             Chat UI, citations, feedback logging, sidebar status

scripts/
+-- ingest.py                    CLI: parse -> chunk -> embed -> ChromaDB
+-- eval.py                      CLI: run ragas evaluation, save report to logs/
+-- create_sample_handbook.py    Utility: generate sample MANIT regulations PDF
`

---

## 8. Running the Project

### Prerequisites

- Python 3.10 or 3.11
- (Optional) An OpenAI or Anthropic API key for full LLM generation

### Setup

`ash
# 1. Create and activate virtual environment
py -3.10 -m venv venv
venv\Scripts\activate

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Configure environment — edit .env with your API key (optional)
# OPENAI_API_KEY=sk-...   OR   ANTHROPIC_API_KEY=sk-ant-...

# 4. Add MANIT PDFs to data/raw/
# (a sample handbook is auto-generated if the directory is empty)

# 5. Run the ingestion pipeline
python scripts/ingest.py

# 6. Start the FastAPI backend (Terminal 1)
venv\Scripts\uvicorn.exe src.api.main:app --host 127.0.0.1 --port 8000

# 7. Start the Streamlit frontend (Terminal 2)
venv\Scripts\streamlit.exe run frontend/streamlit_app.py --server.port 8501
`

### Access Points

| Service | URL | Description |
|---|---|---|
| Chat UI | http://localhost:8501 | Streamlit chat interface |
| API Root | http://127.0.0.1:8000 | Welcome message |
| API Docs | http://127.0.0.1:8000/docs | Swagger / OpenAPI auto-docs |
| Health | http://127.0.0.1:8000/health | System status and document count |
| Query | POST /query | Submit a question, receive answer with citations |

### LLM Provider Configuration (.env)

`env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# OR for Anthropic:
ANTHROPIC_API_KEY=sk-ant-...

# OR for free local inference via Ollama:
USE_OLLAMA=true
OLLAMA_MODEL=llama3
`

> **Note:** Without any API key, AskMANIT runs in **Grounded Fallback Mode** — it surfaces retrieved document passages directly with full citations, no LLM call, no API cost.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| ChromaDB over Pinecone/Weaviate | Zero external dependency, no cloud account, data stays local |
| BGE-small-en over OpenAI Embeddings | Free, local, no per-token cost; 384 dims sufficient for handbook-scale corpus |
| RRF over weighted interpolation | No score-scale calibration needed between vector cosine and BM25 term frequencies |
| Cross-encoder after bi-encoder retrieval | Bi-encoder is fast for recall; cross-encoder is precise for top-N selection |
| Streamlit for v1 frontend | Fastest demoable UI; swap for React/Next.js in v2 |
| LangChain orchestration | Most widely recognized in industry; large ecosystem for future extensions |

---

*Last updated: 2026-09-29 | Author: AskMANIT Development Team*
