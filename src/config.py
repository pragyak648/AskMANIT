"""
src/config.py — Central configuration for AskMANIT.

Loads settings from environment variables (via .env file) and exposes
typed settings objects for use throughout the application.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Root of the project (two levels up from this file: src/ → project root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Central settings object. Values are loaded from environment variables,
    falling back to the defaults defined here. A `.env` file in the project
    root is automatically picked up.
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # LLM provider selection
    # ------------------------------------------------------------------
    llm_provider: Literal["anthropic", "openai", "ollama"] = Field(
        default="anthropic",
        description="Which LLM backend to use: 'anthropic', 'openai', or 'ollama'.",
    )
    use_ollama: bool = Field(
        default=False,
        description="Shortcut flag: if True, overrides llm_provider to 'ollama'.",
    )

    # ------------------------------------------------------------------
    # API keys
    # ------------------------------------------------------------------
    anthropic_api_key: str = Field(default="", description="Anthropic API key.")
    openai_api_key: str = Field(default="", description="OpenAI API key.")

    # ------------------------------------------------------------------
    # Model names
    # ------------------------------------------------------------------
    anthropic_model: str = Field(
        default="claude-3-5-haiku-20241022",
        description="Anthropic model identifier.",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model identifier.",
    )
    ollama_model: str = Field(
        default="llama3",
        description="Ollama model name (must be pulled locally).",
    )

    # ------------------------------------------------------------------
    # Embedding & reranking models (local, no API cost)
    # ------------------------------------------------------------------
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="HuggingFace model ID for sentence-transformers embeddings.",
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="HuggingFace cross-encoder model ID for reranking.",
    )

    # ------------------------------------------------------------------
    # Paths (relative to project root)
    # ------------------------------------------------------------------
    chroma_db_path: str = Field(
        default="data/chroma_db",
        description="Path to ChromaDB persistent storage directory.",
    )
    raw_data_path: str = Field(
        default="data/raw",
        description="Path to raw PDF input directory.",
    )
    processed_data_path: str = Field(
        default="data/processed",
        description="Path to processed/chunked output directory.",
    )
    logs_path: str = Field(
        default="logs",
        description="Path to local logging directory.",
    )

    # ------------------------------------------------------------------
    # Retrieval settings
    # ------------------------------------------------------------------
    top_k_vector: int = Field(
        default=10,
        description="Number of candidates retrieved from vector search.",
    )
    top_k_final: int = Field(
        default=5,
        description="Number of chunks passed to the LLM after reranking.",
    )
    chunk_size: int = Field(
        default=600,
        description="Target chunk size in tokens for text splitting.",
    )
    chunk_overlap: int = Field(
        default=100,
        description="Overlap in tokens between adjacent chunks.",
    )

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------
    @property
    def effective_llm_provider(self) -> str:
        """Returns 'ollama' if use_ollama=True, otherwise llm_provider."""
        return "ollama" if self.use_ollama else self.llm_provider

    @property
    def chroma_db_dir(self) -> Path:
        return PROJECT_ROOT / self.chroma_db_path

    @property
    def raw_data_dir(self) -> Path:
        return PROJECT_ROOT / self.raw_data_path

    @property
    def processed_data_dir(self) -> Path:
        return PROJECT_ROOT / self.processed_data_path

    @property
    def logs_dir(self) -> Path:
        return PROJECT_ROOT / self.logs_path


# ---------------------------------------------------------------------------
# Module-level singleton — import this everywhere
# ---------------------------------------------------------------------------
settings = Settings()


if __name__ == "__main__":
    # Quick sanity check
    print("=== AskMANIT Configuration ===")
    print(f"  LLM provider  : {settings.effective_llm_provider}")
    print(f"  Embedding model: {settings.embedding_model}")
    print(f"  Reranker model : {settings.reranker_model}")
    print(f"  ChromaDB path  : {settings.chroma_db_dir}")
    print(f"  Top-K vector   : {settings.top_k_vector}")
    print(f"  Top-K final    : {settings.top_k_final}")
    print(f"  Chunk size     : {settings.chunk_size} tokens")
    print(f"  Chunk overlap  : {settings.chunk_overlap} tokens")
