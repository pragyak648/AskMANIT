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

from src.config import settings, PROJECT_ROOT
from src.ingestion.parser import parse_pdf
from src.ingestion.chunker import chunk_pages
from src.retrieval.vector_store import get_vector_store


def ingest_file(pdf_path: Path, vs) -> int:
    """Parse, chunk, and embed a single PDF. Returns chunk count."""
    print(f"\n  📄 Parsing: {pdf_path.name} …")
    t0 = time.time()

    pages = parse_pdf(pdf_path)
    print(f"     → {len(pages)} pages parsed ({(time.time()-t0)*1000:.0f}ms)")

    t1 = time.time()
    docs = chunk_pages(pages)
    print(f"     → {len(docs)} chunks created ({(time.time()-t1)*1000:.0f}ms)")

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
