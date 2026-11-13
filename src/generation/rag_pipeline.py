"""
src/generation/rag_pipeline.py — Core RAG pipeline for AskMANIT.

Wires together:
    1. Hybrid search (vector + BM25)  — HybridSearcher
    2. Cross-encoder reranking        — Reranker
    3. Prompt assembly                — prompt_templates.build_prompt()
    4. LLM generation                 — get_llm()

Entry point:
    from src.generation.rag_pipeline import RAGPipeline
    pipeline = RAGPipeline()
    result = pipeline.run_query("What is the attendance requirement?")

Result schema:
    {
        "answer":            str,
        "sources":           [{"source_doc", "page_number", "section_heading",
                               "content", "reranker_score"}, ...],
        "latency_breakdown": {"embed_retrieve_ms", "rerank_ms", "llm_ms", "total_ms"},
        "token_counts":      {"prompt_tokens", "completion_tokens", "total_tokens", "estimated_cost_usd"},
    }
"""

from __future__ import annotations

import json
import time
from typing import Any

from langchain_core.documents import Document

from src.generation.llm_client import get_llm
from src.generation.prompt_templates import REFUSAL_MESSAGE, build_prompt
from src.retrieval.hybrid_search import get_hybrid_searcher
from src.retrieval.reranker import get_reranker
from src.config import settings


# ---------------------------------------------------------------------------
# Token counting & cost helpers
# ---------------------------------------------------------------------------

def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token."""
    return max(1, len(text) // 4)


def _calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate estimated cost in USD based on provider and token counts."""
    provider = getattr(settings, "llm_provider", "local").lower()
    if provider == "openai":
        # standard gpt-4o-mini rates: $0.15 / 1M prompt, $0.60 / 1M completion
        return round((prompt_tokens * 0.15 + completion_tokens * 0.60) / 1_000_000, 6)
    elif provider == "anthropic":
        # claude-3-5-sonnet: $3.00 / 1M prompt, $15.00 / 1M completion
        return round((prompt_tokens * 3.00 + completion_tokens * 15.00) / 1_000_000, 6)
    # Local fallback or Ollama is 100% free
    return 0.0


def _extract_token_counts(response: Any, prompt_text: str, answer_text: str) -> dict[str, Any]:
    """
    Extract token usage from the LLM response if available, otherwise estimate.
    Includes estimated USD cost based on active provider pricing.
    """
    # Try to read from response metadata (works for Anthropic / OpenAI)
    usage = getattr(response, "usage_metadata", None) or getattr(response, "response_metadata", {}).get("usage", {})

    prompt_tokens = 0
    completion_tokens = 0

    if usage:
        prompt_tokens = int(
            getattr(usage, "input_tokens", None)
            or usage.get("input_tokens")
            or usage.get("prompt_tokens", 0)
        )
        completion_tokens = int(
            getattr(usage, "output_tokens", None)
            or usage.get("output_tokens")
            or usage.get("completion_tokens", 0)
        )

    if not prompt_tokens or not completion_tokens:
        # Fallback: character-based estimation
        prompt_tokens = _estimate_tokens(prompt_text)
        completion_tokens = _estimate_tokens(answer_text)

    total_tokens = prompt_tokens + completion_tokens
    cost = _calculate_cost(prompt_tokens, completion_tokens)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": cost,
    }


# ---------------------------------------------------------------------------
# Document → source dict
# ---------------------------------------------------------------------------

def _doc_to_source(doc: Document) -> dict[str, Any]:
    meta = doc.metadata
    return {
        "source_doc": meta.get("source_doc", "Unknown"),
        "page_number": meta.get("page_number", None),
        "section_heading": meta.get("section_heading", "") or "N/A",
        "content": doc.page_content[:500],  # snippet for UI display
        "reranker_score": meta.get("reranker_score", None),
    }


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class RAGPipeline:
    """
    End-to-end RAG pipeline:
        question → hybrid search → rerank → prompt → LLM → answer + citations
    """

    def __init__(self):
        self._searcher = get_hybrid_searcher()
        self._reranker = get_reranker()
        self._llm = None  # lazy-loaded (avoids import errors at module load time)

    def _get_llm(self):
        if self._llm is None:
            self._llm = get_llm()
        return self._llm

    def run_query(
        self,
        question: str,
        top_k_final: int | None = None,
        top_k_vector: int | None = None,
        chat_history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        Run the full RAG pipeline for a question.

        Args:
            question:     The user's question string.
            top_k_final:  Number of chunks sent to the LLM (after reranking).
            top_k_vector: Candidate pool size for retrieval.
            chat_history: Optional recent conversation history.

        Returns:
            Dict with keys: answer, sources, latency_breakdown, token_counts.
        """
        top_k_final = top_k_final or settings.top_k_final
        top_k_vector = top_k_vector or settings.top_k_vector

        # Fast path for conversational greetings
        clean_q = question.strip().lower().strip("?!.,")
        if clean_q in {"hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "help"}:
            return {
                "answer": (
                    "Hello! 👋 I am **AskMANIT**, your academic assistant for Maulana Azad National Institute of Technology.\n\n"
                    "You can ask me any question about official institute policies, including:\n"
                    "- 📋 **Attendance requirements** to sit for examinations\n"
                    "- 🎯 **Grading scales & CGPA calculation**\n"
                    "- 🔄 **Backlog rules & remedial exams**\n"
                    "- 🎓 **Degree credits & honors eligibility**\n"
                    "- 🏠 **Hostel rules, discipline, and campus services**\n\n"
                    "What would you like to know?"
                ),
                "sources": [],
                "latency_breakdown": {
                    "embed_retrieve_ms": 0,
                    "rerank_ms": 0,
                    "llm_ms": 0,
                    "total_ms": 1,
                },
                "token_counts": {
                    "prompt_tokens": len(question.split()),
                    "completion_tokens": 75,
                    "total_tokens": len(question.split()) + 75,
                    "estimated_cost_usd": 0.0,
                },
            }

        t_start = time.perf_counter()

        # Contextualize short follow-up questions using prior conversation turns
        retrieval_query = question.strip()
        effective_question = question.strip()
        words = set(retrieval_query.lower().split())
        followup_cues = {
            "more", "continue", "elaborate", "details", "explain", "expand",
            "further", "what", "why", "how", "and", "also", "tell", "tell me more"
        }
        if (len(retrieval_query.split()) <= 4 or bool(words & followup_cues)) and chat_history:
            last_user_q = ""
            for turn in reversed(chat_history):
                if turn.get("role") == "user":
                    cand = turn.get("content", "").strip()
                    if cand and cand.lower() != retrieval_query.lower():
                        last_user_q = cand
                        break
            if last_user_q:
                retrieval_query = f"{last_user_q} ({question})"
                effective_question = f"{last_user_q} (Follow-up request: {question})"

        # -------------------------------------------------------------------
        # Stage 1: Hybrid search (vector + BM25 + RRF)
        # -------------------------------------------------------------------
        t1 = time.perf_counter()
        candidates: list[Document] = self._searcher.hybrid_search(
            retrieval_query, k=top_k_vector
        )
        t2 = time.perf_counter()
        embed_retrieve_ms = round((t2 - t1) * 1000)

        # -------------------------------------------------------------------
        # Stage 2: Rerank
        # -------------------------------------------------------------------
        reranked: list[Document] = self._reranker.rerank(
            retrieval_query, candidates, top_n=top_k_final
        )
        t3 = time.perf_counter()
        rerank_ms = round((t3 - t2) * 1000)

        # -------------------------------------------------------------------
        # Stage 3: Prompt assembly
        # -------------------------------------------------------------------
        messages = build_prompt(effective_question, reranked, chat_history=chat_history)
        prompt_text = "\n".join(
            [msg.content for msg in messages]  # type: ignore[attr-defined]
        )

        # -------------------------------------------------------------------
        # Stage 4: LLM generation
        # -------------------------------------------------------------------
        llm = self._get_llm()
        response = llm.invoke(messages)
        t4 = time.perf_counter()
        llm_ms = round((t4 - t3) * 1000)

        answer: str = response.content  # type: ignore[attr-defined]

        # Clean up any prompt artifacts or instruction echoes
        meta_prefixes = [
            "answering the student's question using only the provided context",
            "answering the student's question using the provided context",
            "answering the student's question",
            "using only the provided context",
            "based on the provided context",
            "based on the provided documents",
            "based on the context provided",
            "here is the answer based on the provided context",
        ]
        cleaned_answer = answer.strip()
        for prefix in meta_prefixes:
            if cleaned_answer.lower().startswith(prefix):
                cleaned_answer = cleaned_answer[len(prefix):].lstrip(" :\n#*-")
        answer = cleaned_answer
        total_ms = round((t4 - t_start) * 1000)

        # -------------------------------------------------------------------
        # Stage 5: Assemble output & log
        # -------------------------------------------------------------------
        token_counts = _extract_token_counts(response, prompt_text, answer)

        try:
            log_dir = settings.logs_dir
            log_dir.mkdir(parents=True, exist_ok=True)
            log_entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "question": question,
                "retrieved_chunk_ids": [doc.metadata.get("chunk_id", "") for doc in reranked],
                "sources_count": len(reranked),
                "latency_breakdown": {
                    "embed_retrieve_ms": embed_retrieve_ms,
                    "rerank_ms": rerank_ms,
                    "llm_ms": llm_ms,
                    "total_ms": total_ms,
                },
                "token_counts": token_counts,
                "answer_length": len(answer),
            }
            with open(log_dir / "queries.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

        return {
            "answer": answer,
            "sources": [_doc_to_source(doc) for doc in reranked],
            "latency_breakdown": {
                "embed_retrieve_ms": embed_retrieve_ms,
                "rerank_ms": rerank_ms,
                "llm_ms": llm_ms,
                "total_ms": total_ms,
            },
            "token_counts": token_counts,
        }

    def run_query_streaming(self, question: str, top_k_final: int | None = None):
        """
        Run the pipeline and stream the LLM response token-by-token.
        """
        top_k_final = top_k_final or settings.top_k_final

        candidates = self._searcher.hybrid_search(question, k=settings.top_k_vector)
        reranked = self._reranker.rerank(question, candidates, top_n=top_k_final)
        messages = build_prompt(question, reranked)

        llm = self._get_llm()
        for chunk in llm.stream(messages):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_pipeline_instance: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    """Return (or create) the shared RAGPipeline singleton."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RAGPipeline()
    return _pipeline_instance

get_rag_pipeline = get_pipeline


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "What is the minimum attendance requirement to sit for exams?"
    )
    print(f"Question: {question!r}\n")

    pipeline = RAGPipeline()
    result = pipeline.run_query(question)

    print(f"Answer:\n{result['answer']}\n")
    print(f"Sources ({len(result['sources'])}):")
    for src in result["sources"]:
        print(f"  - {src['source_doc']}, p{src['page_number']}, {src['section_heading']}")
    print(f"\nLatency: {result['latency_breakdown']}")
    print(f"Tokens : {result['token_counts']}")
