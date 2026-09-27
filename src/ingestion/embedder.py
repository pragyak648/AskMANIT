"""
src/ingestion/embedder.py — Embedding wrapper for AskMANIT.

Wraps BAAI/bge-small-en-v1.5 via sentence-transformers.
Implements the LangChain Embeddings interface so it can be dropped directly
into ChromaDB's langchain integration.

Usage:
    from src.ingestion.embedder import BGEEmbedder
    embedder = BGEEmbedder()
    vec = embedder.embed_query("What is attendance policy?")
    vecs = embedder.embed_documents(["text 1", "text 2"])
"""

from __future__ import annotations

from typing import List

from langchain_core.embeddings import Embeddings

from src.config import settings


class BGEEmbedder(Embeddings):
    """
    LangChain-compatible embeddings using BAAI/bge-small-en-v1.5.

    BGE models benefit from a query prefix for retrieval tasks.
    - Documents are embedded WITHOUT any prefix.
    - Queries are embedded WITH the prefix "Represent this sentence: ".
    """

    _QUERY_PREFIX = "Represent this sentence: "

    def __init__(self, model_name: str | None = None):
        """
        Args:
            model_name: Override the HuggingFace model ID. Defaults to
                        settings.embedding_model ("BAAI/bge-small-en-v1.5").
        """
        self.model_name = model_name or settings.embedding_model
        self._model = None  # lazy-loaded on first use

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # noqa: PLC0415
            except ImportError as e:
                raise ImportError(
                    "sentence-transformers is required: pip install sentence-transformers"
                ) from e
            self._model = SentenceTransformer(self.model_name)
        return self._model

    # ------------------------------------------------------------------
    # LangChain Embeddings interface
    # ------------------------------------------------------------------

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents (no prefix added).

        Args:
            texts: List of document strings.

        Returns:
            List of embedding vectors (each a list of floats).
        """
        model = self._load_model()
        embeddings = model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
            batch_size=32,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single search query (with BGE query prefix).

        Args:
            text: The query string.

        Returns:
            Embedding vector as a list of floats.
        """
        model = self._load_model()
        prefixed = self._QUERY_PREFIX + text
        embedding = model.encode(
            prefixed,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    @property
    def embedding_dimension(self) -> int:
        """Return the embedding dimensionality (384 for bge-small-en-v1.5)."""
        model = self._load_model()
        return model.get_sentence_embedding_dimension()


# ---------------------------------------------------------------------------
# Module-level singleton — reuse to avoid repeated model loading
# ---------------------------------------------------------------------------
_embedder_instance: BGEEmbedder | None = None


def get_embedder() -> BGEEmbedder:
    """Return (or create) the shared BGEEmbedder singleton."""
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = BGEEmbedder()
    return _embedder_instance


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    emb = BGEEmbedder()
    test_query = "What is the attendance requirement?"
    vec = emb.embed_query(test_query)
    print(f"Model          : {emb.model_name}")
    print(f"Dimension      : {len(vec)}")
    print(f"Query vector[0]: {vec[0]:.6f}  (first element)")

    docs = emb.embed_documents(["doc one", "doc two"])
    print(f"Docs embedded  : {len(docs)} vectors, dim={len(docs[0])}")
