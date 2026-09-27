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
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. "
            "Must be one of: 'anthropic', 'openai', 'ollama'."
        )


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
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. "
            "Add it to your .env file or set the environment variable."
        )

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
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file or set the environment variable."
        )

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
