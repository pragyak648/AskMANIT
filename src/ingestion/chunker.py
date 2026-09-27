"""
src/ingestion/chunker.py — Text chunking for AskMANIT ingestion pipeline.

Splits page-level text into smaller overlapping chunks using LangChain's
RecursiveCharacterTextSplitter. Each chunk is a LangChain Document with
metadata: source_doc, page_number, section_heading, chunk_id.

Chunk size target: 600 tokens ≈ ~2400 chars (assuming ~4 chars/token).
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings

# ---------------------------------------------------------------------------
# Section heading detection heuristics
# ---------------------------------------------------------------------------
_HEADING_PATTERN = re.compile(
    r"^(?:"
    r"(?:\d+[\.\d]*\s+[A-Z][^\n]{3,60})"       # e.g. "4.2 Attendance Policy"
    r"|(?:[A-Z][A-Z\s]{4,50})"                   # e.g. "GRADING SCALE"
    r"|(?:Section\s+\d+[^\n]{0,40})"             # e.g. "Section 3 Credits"
    r"|(?:Chapter\s+\d+[^\n]{0,40})"             # e.g. "Chapter 2 Examinations"
    r")",
    flags=re.MULTILINE,
)


def _extract_section_heading(text: str) -> str:
    """
    Best-effort extraction of the first heading-like line in a chunk.
    Returns empty string if none found.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if _HEADING_PATTERN.match(stripped):
            return stripped[:120]  # cap length
    return ""


def _make_chunk_id(source_doc: str, page_number: int, chunk_index: int) -> str:
    """Create a deterministic chunk ID used as the ChromaDB document ID."""
    raw = f"{source_doc}::p{page_number}::c{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Main chunker
# ---------------------------------------------------------------------------

def chunk_pages(
    pages: list[dict[str, Any]],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """
    Split a list of page dicts (from parser.py) into LangChain Documents.

    Args:
        pages:         Output of parser.parse_pdf().
        chunk_size:    Token-approximate size (defaults to settings.chunk_size).
        chunk_overlap: Token-approximate overlap (defaults to settings.chunk_overlap).

    Returns:
        List of LangChain Document objects, each with metadata:
          - source_doc
          - page_number
          - section_heading
          - chunk_id
          - has_table
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    # LangChain splitter operates on characters; 1 token ≈ 4 chars.
    char_size = chunk_size * 4
    char_overlap = chunk_overlap * 4

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=char_size,
        chunk_overlap=char_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len,
        is_separator_regex=False,
    )

    all_docs: list[Document] = []

    for page in pages:
        text: str = page["text"]
        page_number: int = page["page_number"]
        source_doc: str = page["source_doc"]
        has_table: bool = page.get("has_table", False)

        if not text.strip():
            continue

        # Split the page text into chunks
        raw_chunks = splitter.split_text(text)

        for i, chunk_text in enumerate(raw_chunks):
            if not chunk_text.strip():
                continue

            section_heading = _extract_section_heading(chunk_text)
            chunk_id = _make_chunk_id(source_doc, page_number, i)

            doc = Document(
                page_content=chunk_text,
                metadata={
                    "source_doc": source_doc,
                    "page_number": page_number,
                    "section_heading": section_heading,
                    "chunk_id": chunk_id,
                    "has_table": has_table,
                },
            )
            all_docs.append(doc)

    return all_docs


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from src.ingestion.parser import parse_pdf

    if len(sys.argv) < 2:
        print("Usage: python chunker.py <path_to_pdf>")
        sys.exit(1)

    pages = parse_pdf(sys.argv[1])
    docs = chunk_pages(pages)

    print(f"Total chunks: {len(docs)}")
    for doc in docs[:3]:
        print(f"\n--- Chunk ({doc.metadata['chunk_id'][:8]}…) ---")
        print(f"  source_doc     : {doc.metadata['source_doc']}")
        print(f"  page_number    : {doc.metadata['page_number']}")
        print(f"  section_heading: {doc.metadata['section_heading'] or '(none)'}")
        print(f"  text preview   : {doc.page_content[:200]}")
