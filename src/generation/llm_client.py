"""
src/generation/llm_client.py — Pluggable LLM factory for AskMANIT.

Returns the appropriate LangChain chat model based on settings.effective_llm_provider:
  - "anthropic" → ChatAnthropic (requires ANTHROPIC_API_KEY)
  - "openai"    → ChatOpenAI   (requires OPENAI_API_KEY)
  - "ollama"    → ChatOllama   (requires local Ollama daemon + model pulled)

Usage:
    from src.generation.llm_client import get_llm
    llm = get_llm()
    response = llm.invoke("Hello!")
"""

from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models import BaseChatModel

from src.config import settings


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """
    Return a LangChain chat model based on the configured LLM provider.

    The result is cached (singleton pattern) so the model is only instantiated
    once per process.

    Returns:
        A LangChain BaseChatModel instance.

    Raises:
        ValueError: If the configured provider is not supported.
        ImportError: If the required provider package is not installed.
    """
    provider = settings.effective_llm_provider

    if provider == "anthropic":
        return _build_anthropic()
    elif provider == "openai":
        return _build_openai()
    elif provider == "ollama":
        return _build_ollama()
    elif provider in ("mock", "fallback"):
        return GroundedFallbackChatModel()
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. "
            "Must be one of: 'anthropic', 'openai', 'ollama', 'mock'."
        )


# ---------------------------------------------------------------------------
# Fallback Model for Local / Keyless Operation
# ---------------------------------------------------------------------------

from typing import Any, List, Optional
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks.manager import CallbackManagerForLLMRun


import re


def _format_concise_grounded_answer(raw_context: str) -> str:
    """
    Synthesize a clean, concise, student-friendly answer from the retrieved passages
    instead of dumping thousands of characters of raw text.
    """
    blocks = raw_context.split("\n\n---\n\n")
    if not blocks:
        blocks = [raw_context]

    primary_block = blocks[0].strip()

    header_match = re.search(
        r"\[Context \d+\]\s*Source:\s*([^,]+),\s*Page\s*([^,]+),\s*Section:\s*([^\n]+)",
        primary_block,
    )
    doc_name = header_match.group(1).strip() if header_match else "MANIT Regulations"
    page_num = header_match.group(2).strip() if header_match else "N/A"
    section_name = header_match.group(3).strip() if header_match else "General"

    body = re.sub(r"\[Context \d+\].*?\n", "", primary_block)
    body = re.sub(
        r"MAULANA\s+AZAD\s+NATIONAL\s+INSTITUTE\s+OF(\s+TECHNOLOGY)?(\s*,?\s*BHOPAL)?",
        "",
        body,
        flags=re.IGNORECASE,
    )
    body = re.sub(
        r"ACADEMIC\s+REGULATIONS\s*(&\s*ORDINANCES)?(\s*\(.*?\))?",
        "",
        body,
        flags=re.IGNORECASE,
    )
    body = re.sub(r"STUDENT\s+HANDBOOK(\s+20\d\d)?", "", body, flags=re.IGNORECASE)

    # Split into numbered clauses or paragraphs (rejoining broken PDF lines)
    raw_items = re.split(r"\n(?=\d+\.\d+|\b[A-Z][a-z]+:|\bSection\b|\b[A-Z\s]{4,}:)", body)
    cleaned_points = []
    curr_len = 0

    for item in raw_items:
        # Join lines within the same clause
        single_line = " ".join([w.strip() for w in item.split("\n") if w.strip()])
        # Remove standalone Section header lines
        single_line = re.sub(r"^Section\s+\d+:\s*[^\n]+", "", single_line, flags=re.IGNORECASE).strip()
        single_line = re.sub(r"^(technology, bhopal|bhopal|regulations)\b", "", single_line, flags=re.IGNORECASE).strip()
        if len(single_line) < 15:
            continue
        # Format key prefixes like '1.1 Minimum Attendance:' -> '**Minimum Attendance:**'
        formatted_line = re.sub(r"^\d+(\.\d+)*\s*([A-Za-z\s]+:)", r"**\2**", single_line)
        formatted_line = re.sub(r"^\d+(\.\d+)*\s*", "", formatted_line)
        cleaned_points.append(f"- {formatted_line}")
        curr_len += len(formatted_line)
        if curr_len > 650:
            break

    if not cleaned_points:
        summary_text = body[:450].strip()
    else:
        summary_text = "\n".join(cleaned_points)

    response_text = (
        f"### 📌 Policy & Regulation Summary\n\n"
        f"{summary_text}\n\n"
        f"---\n"
        f"📍 **Primary Source**: *{doc_name}* (Page {page_num}, {section_name})\n\n"
        f"*💡 Tip: Expand **Verified Sources & Citations** below to read the original text passages.*"
    )
    return response_text


class GroundedFallbackChatModel(BaseChatModel):
    """
    Fallback chat model when no external LLM API key (OpenAI/Anthropic) is configured.
    Synthesizes and presents the retrieved passages concisely with citations.
    """

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        user_msg = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), None)
        text = str(user_msg.content) if user_msg else ""

        if "(No relevant context found in the documents.)" in text:
            response_text = (
                "I'm sorry, but I couldn't find an answer to your question in the MANIT "
                "academic handbook or syllabus documents. Please check the official MANIT "
                "website (https://www.manit.ac.in) or contact the Academic Section directly."
            )
        else:
            context_blocks = text.split("## Relevant Context from MANIT Documents")
            content_part = context_blocks[1] if len(context_blocks) > 1 else text
            for d in ("## Student Question", "## User Question:"):
                if d in content_part:
                    content_part = content_part.split(d)[0].strip()
                    break

            response_text = _format_concise_grounded_answer(content_part)

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response_text))])

    @property
    def _llm_type(self) -> str:
        return "grounded-fallback"


# ---------------------------------------------------------------------------
# Provider builders
# ---------------------------------------------------------------------------

def _build_anthropic() -> "BaseChatModel":
    try:
        from langchain_anthropic import ChatAnthropic  # noqa: PLC0415
    except ImportError as e:
        raise ImportError(
            "langchain-anthropic is required: pip install langchain-anthropic"
        ) from e

    if not settings.anthropic_api_key:
        print("[AskMANIT] ANTHROPIC_API_KEY not set. Using local GroundedFallbackChatModel.")
        return GroundedFallbackChatModel()

    return ChatAnthropic(
        model=settings.anthropic_model,
        api_key=settings.anthropic_api_key,  # type: ignore[arg-type]
        max_tokens=2048,
        temperature=0.1,  # Low temperature for factual Q&A
    )


def _build_openai() -> "BaseChatModel":
    try:
        from langchain_openai import ChatOpenAI  # noqa: PLC0415
    except ImportError as e:
        raise ImportError(
            "langchain-openai is required: pip install langchain-openai"
        ) from e

    if not settings.openai_api_key:
        print("[AskMANIT] OPENAI_API_KEY not set. Using local GroundedFallbackChatModel.")
        return GroundedFallbackChatModel()

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,  # type: ignore[arg-type]
        max_tokens=2048,
        temperature=0.1,
    )


def _build_ollama() -> "BaseChatModel":
    try:
        from langchain_community.chat_models import ChatOllama  # noqa: PLC0415
    except ImportError as e:
        raise ImportError(
            "langchain-community is required: pip install langchain-community"
        ) from e

    return ChatOllama(
        model=settings.ollama_model,
        temperature=0.1,
    )


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Provider: {settings.effective_llm_provider}")
    try:
        llm = get_llm()
        print(f"LLM class: {type(llm).__name__}")
        response = llm.invoke("Say 'AskMANIT is ready' in one sentence.")
        print(f"Test response: {response.content}")
    except Exception as exc:
        print(f"Error: {exc}")
