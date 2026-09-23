# AskMANIT

> A retrieval-augmented generation (RAG) chatbot that answers student questions about MANIT's academic handbook, syllabus, and institutional policies — with citations.

## Overview

AskMANIT lets MANIT students ask natural-language questions like:
- *"What is the minimum attendance requirement to sit for exams?"*
- *"How many credits do I need to graduate?"*
- *"What happens to my CGPA if I have a backlog in semester 3?"*

It retrieves relevant passages from official documents, reranks them, and generates grounded answers with page/section citations — so answers are verifiable, not hallucinated.

## Architecture

```
PDFs → Parser → Chunker → Embedder → ChromaDB
Question → Embed → Hybrid Search (vector + BM25) → Rerank → LLM → Answer + Citations
```

Full architecture diagrams: see `ASKMANIT_PROJECT_SPEC.md`.

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangChain |
| Vector Store | ChromaDB (local, persistent) |
| Embeddings | `BAAI/bge-small-en-v1.5` (local) |
| LLM | Claude / OpenAI / Ollama (pluggable) |
| PDF Parsing | PyMuPDF + unstructured |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Evaluation | ragas |

## Setup

```bash
# 1. Clone and enter the project
git clone <repo>
cd askmanit

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and fill in your API keys

# 5. Add PDF source documents
# Place MANIT handbook and syllabus PDFs in data/raw/

# 6. Run ingestion pipeline
python scripts/ingest.py

# 7. Start the backend API
uvicorn src.api.main:app --reload

# 8. Start the frontend (in a separate terminal)
streamlit run frontend/streamlit_app.py
```

## Project Status

See `PROJECT_STATE.md` for current phase and task status.
See `tasks/tasks.json` for the full task tracker.

## Evaluation

```bash
python scripts/eval.py
```

Results are saved to `PROJECT_STATE.md`.
