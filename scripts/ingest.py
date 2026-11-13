"""
scripts/ingest.py — Full ingestion pipeline runner for AskMANIT.

Orchestrates: PDF parse → chunk → embed → write to ChromaDB.

Usage:
    # Ingest all PDFs in data/raw/
    python scripts/ingest.py

    # Ingest a specific file
    python scripts/ingest.py --source data/raw/manit_handbook.pdf

    # Reset the collection and re-ingest everything
    python scripts/ingest.py --reset

The script is idempotent: re-running with the same PDFs will upsert (not
duplicate) chunks because each chunk uses a deterministic chunk_id.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure src/ is on the import path when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Ensure utf-8 encoding for console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
from src.config import settings, PROJECT_ROOT
from src.ingestion.parser import parse_pdf
from src.ingestion.chunker import chunk_pages
from langchain_core.documents import Document
from src.retrieval.vector_store import get_vector_store


def _save_processed_data(pdf_stem: str, pages: list[dict], docs: list[Document]) -> None:
    """Save extracted pages, chunk JSON, and readable Markdown to data/processed/."""
    processed_dir = settings.processed_data_dir
    processed_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save extracted pages
    pages_file = processed_dir / f"{pdf_stem}_pages.json"
    with open(pages_file, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)

    # 2. Save chunks in JSON format
    chunks_data = [
        {
            "chunk_id": doc.metadata.get("chunk_id"),
            "page_number": doc.metadata.get("page_number"),
            "section_heading": doc.metadata.get("section_heading", ""),
            "has_table": doc.metadata.get("has_table", False),
            "source_doc": doc.metadata.get("source_doc", pdf_stem),
            "content": doc.page_content,
        }
        for doc in docs
    ]
    chunks_file = processed_dir / f"{pdf_stem}_chunks.json"
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(chunks_data, f, indent=2, ensure_ascii=False)

    # 3. Save a human-readable Markdown view of the chunks
    md_file = processed_dir / f"{pdf_stem}_chunks.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# Processed Chunks: {pdf_stem}\n\n")
        f.write(f"- **Total Pages:** {len(pages)}\n")
        f.write(f"- **Total Chunks:** {len(docs)}\n\n---\n\n")
        for i, chunk in enumerate(chunks_data, 1):
            f.write(f"## Chunk {i} (Page {chunk['page_number']})\n\n")
            if chunk["section_heading"]:
                f.write(f"**Section:** {chunk['section_heading']}\n\n")
            f.write(f"**Chunk ID:** `{chunk['chunk_id']}`\n\n")
            f.write("```text\n")
            f.write(chunk["content"].strip())
            f.write("\n```\n\n---\n\n")


def ingest_file(pdf_path: Path, vs) -> int:
    """Parse, chunk, and embed a single PDF. Returns chunk count."""
    print(f"\n  📄 Parsing: {pdf_path.name} …")
    t0 = time.time()

    pages = parse_pdf(pdf_path)
    print(f"     → {len(pages)} pages parsed ({(time.time()-t0)*1000:.0f}ms)")

    t1 = time.time()
    docs = chunk_pages(pages)
    print(f"     → {len(docs)} chunks created ({(time.time()-t1)*1000:.0f}ms)")

    _save_processed_data(pdf_path.stem, pages, docs)
    print(f"     → Processed data saved to {settings.processed_data_path}/")

    t2 = time.time()
    count = vs.add_documents(docs)
    print(f"     → {count} chunks upserted to ChromaDB ({(time.time()-t2)*1000:.0f}ms)")

    return count


def main():
    parser = argparse.ArgumentParser(
        description="AskMANIT ingestion pipeline — parse PDFs and index into ChromaDB."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Path to a specific PDF to ingest. Defaults to all PDFs in data/raw/.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the ChromaDB collection before ingesting.",
    )
    args = parser.parse_args()

    vs = get_vector_store()

    if args.reset:
        print("⚠️  Resetting ChromaDB collection …")
        vs.reset_collection()
        print("   Collection reset.")

    # Determine which files to process
    if args.source:
        pdf_files = [Path(args.source)]
    else:
        raw_dir = PROJECT_ROOT / settings.raw_data_path
        pdf_files = sorted(raw_dir.glob("*.pdf"))

    if not pdf_files:
        print("\n  No PDF files found.")
        if not args.source:
            print(f"   Add PDFs to {PROJECT_ROOT / settings.raw_data_path}")
            print("   See data/raw/SOURCES.md for download instructions.")
        sys.exit(0)

    print(f"\n🚀 AskMANIT Ingestion Pipeline")
    print(f"   Files to process: {len(pdf_files)}")
    print(f"   ChromaDB path:    {vs._persist_dir}")

    total_start = time.time()
    total_chunks = 0

    for pdf_path in pdf_files:
        if not pdf_path.exists():
            print(f"\n  File not found: {pdf_path}")
            continue
        try:
            total_chunks += ingest_file(pdf_path, vs)
        except Exception as exc:
            print(f"\n   Error processing {pdf_path.name}: {exc}")

    total_elapsed = time.time() - total_start
    stats = vs.get_collection_stats()

    print(f"\n✅ Ingestion complete!")
    print(f"   Total chunks upserted : {total_chunks}")
    print(f"   Total in ChromaDB     : {stats['document_count']}")
    print(f"   Total time            : {total_elapsed:.1f}s")


if __name__ == "__main__":
    main()
