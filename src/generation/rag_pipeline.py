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
        "token_counts":      {"prompt_tokens", "completion_tokens", "total_tokens"},
    }
"""

from __future__ import annotations

import time
from typing import Any

from langchain_core.documents import Document

from src.generation.llm_client import get_llm
from src.generation.prompt_templates import REFUSAL_MESSAGE, build_prompt
from src.retrieval.hybrid_search import get_hybrid_searcher
from src.retrieval.reranker import get_reranker
from src.config import settings


# ---------------------------------------------------------------------------
# Token counting helpers (best-effort, provider-agnostic)
# ---------------------------------------------------------------------------

def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token."""
    return max(1, len(text) // 4)


def _extract_token_counts(response: Any, prompt_text: str, answer_text: str) -> dict[str, int]:
    """
    Extract token usage from the LLM response if available, otherwise estimate.
    """
    # Try to read from response metadata (works for Anthropic / OpenAI)
    usage = getattr(response, "usage_metadata", None) or getattr(response, "response_metadata", {}).get("usage", {})

    if usage:
        prompt_tokens = (
            getattr(usage, "input_tokens", None)
            or usage.get("input_tokens")
            or usage.get("prompt_tokens", 0)
        )
        completion_tokens = (
            getattr(usage, "output_tokens", None)
            or usage.get("output_tokens")
            or usage.get("completion_tokens", 0)
        )
        if prompt_tokens and completion_tokens:
            return {
                "prompt_tokens": int(prompt_tokens),
                "completion_tokens": int(completion_tokens),
                "total_tokens": int(prompt_tokens) + int(completion_tokens),
            }

    # Fallback: character-based estimation
    pt = _estimate_tokens(prompt_text)
    ct = _estimate_tokens(answer_text)
    return {
        "prompt_tokens": pt,
        "completion_tokens": ct,
        "total_tokens": pt + ct,
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
    ) -> dict[str, Any]:
        """
        Run the full RAG pipeline for a question.

        Args:
            question:     The user's question string.
            top_k_final:  Number of chunks sent to the LLM (after reranking).
            top_k_vector: Candidate pool size for retrieval.

        Returns:
            Dict with keys: answer, sources, latency_breakdown, token_counts.
        """
        top_k_final = top_k_final or settings.top_k_final
        top_k_vector = top_k_vector or settings.top_k_vector

        t_start = time.perf_counter()

        # -------------------------------------------------------------------
        # Stage 1: Hybrid search (vector + BM25 + RRF)
        # -------------------------------------------------------------------
        t1 = time.perf_counter()
        candidates: list[Document] = self._searcher.hybrid_search(
            question, k=top_k_vector
        )
        t2 = time.perf_counter()
        embed_retrieve_ms = round((t2 - t1) * 1000)

        # -------------------------------------------------------------------
        # Stage 2: Rerank
        # -------------------------------------------------------------------
        reranked: list[Document] = self._reranker.rerank(
            question, candidates, top_n=top_k_final
        )
        t3 = time.perf_counter()
        rerank_ms = round((t3 - t2) * 1000)

        # -------------------------------------------------------------------
        # Stage 3: Prompt assembly
        # -------------------------------------------------------------------
        messages = build_prompt(question, reranked)
        # Build prompt string for token estimation
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
        total_ms = round((t4 - t_start) * 1000)

        # -------------------------------------------------------------------
        # Stage 5: Assemble output
        # -------------------------------------------------------------------
        token_counts = _extract_token_counts(response, prompt_text, answer)

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

        Yields:
            str — Successive text chunks from the LLM stream.

        Note:
            Sources and latency are NOT yielded during streaming; they are
            only available when the stream ends. The caller should call
            run_query() for the full structured response.
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


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

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
