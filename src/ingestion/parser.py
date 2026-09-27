"""
src/ingestion/parser.py — PDF parsing for AskMANIT ingestion pipeline.

Extracts text and tables from PDFs using:
  - PyMuPDF (fitz)  for fast text extraction
  - unstructured     for table-heavy pages (detected by PyMuPDF heuristics)

Output format (per page):
  {
    "text":          str,          # full extracted text
    "page_number":   int,          # 1-indexed
    "source_doc":    str,          # stem of the PDF filename (e.g. "manit_handbook")
    "has_table":     bool,         # True if the page appears to contain a table
    "raw_html":      str | None,   # HTML from unstructured (only for table pages)
  }
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise ImportError("PyMuPDF is required: pip install pymupdf") from e


# ---------------------------------------------------------------------------
# Heuristics for table detection
# ---------------------------------------------------------------------------
_TABLE_KEYWORDS = re.compile(
    r"(S\.No\.?|Sr\.?\s*No\.?|Grade Points?|Credits?|CGPA|Marks?|Subject Code"
    r"|Course Code|Semester|Total|Pass\s*Marks?|Maximum\s*Marks?)",
    flags=re.IGNORECASE,
)


def _looks_like_table_page(page: "fitz.Page") -> bool:
    """
    Heuristic: a page is considered 'table-heavy' if it has many lines with
    tab/multiple-space separators OR contains table-related keywords.
    """
    text = page.get_text("text")
    # Check for grid-like spacing patterns (many rows of tab-separated values)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False

    tab_lines = sum(1 for ln in lines if "\t" in ln or "  " in ln)
    keyword_hit = bool(_TABLE_KEYWORDS.search(text))

    return keyword_hit or (tab_lines / max(len(lines), 1) > 0.3)


# ---------------------------------------------------------------------------
# Core parser
# ---------------------------------------------------------------------------

def parse_pdf(pdf_path: str | Path) -> list[dict[str, Any]]:
    """
    Parse a PDF and return a list of page dicts.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of dicts with keys: text, page_number, source_doc, has_table,
        raw_html (None if not a table page).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    source_doc = pdf_path.stem
    pages: list[dict[str, Any]] = []

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)

    for page_index in range(total_pages):
        page = doc[page_index]
        page_number = page_index + 1
        has_table = _looks_like_table_page(page)

        if has_table:
            text, raw_html = _extract_table_page(page)
        else:
            text = _extract_text_page(page)
            raw_html = None

        # Skip entirely blank pages
        if not text.strip():
            continue

        pages.append(
            {
                "text": text,
                "page_number": page_number,
                "source_doc": source_doc,
                "has_table": has_table,
                "raw_html": raw_html,
            }
        )

    doc.close()
    return pages


def _extract_text_page(page: "fitz.Page") -> str:
    """Extract plain text from a non-table page, preserving line structure."""
    text = page.get_text("text")
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_table_page(page: "fitz.Page") -> tuple[str, str | None]:
    """
    Extract a table-heavy page.

    Tries unstructured first for HTML-aware extraction; falls back to PyMuPDF
    text extraction with tab → space normalisation if unstructured is not
    available or fails.

    Returns:
        (text, raw_html) — raw_html is None on fallback.
    """
    # Attempt unstructured extraction
    try:
        from unstructured.partition.pdf import partition_pdf  # noqa: PLC0415

        elements = partition_pdf(
            filename=str(page.parent.name),  # type: ignore[attr-defined]
            page_number=page.number + 1,
            strategy="hi_res",
            include_page_breaks=False,
        )
        texts = [str(el) for el in elements if str(el).strip()]
        combined = "\n".join(texts)
        # Build a minimal HTML for storage
        raw_html = "<br>".join(texts)
        return combined, raw_html

    except Exception:
        # Fallback: PyMuPDF text with tab normalization
        text = page.get_text("text")
        text = text.replace("\t", "  ")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip(), None


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_pdf>")
        sys.exit(1)

    result = parse_pdf(sys.argv[1])
    print(f"Parsed {len(result)} pages from '{sys.argv[1]}'")
    for pg in result[:3]:
        print(f"\n--- Page {pg['page_number']} (table={pg['has_table']}) ---")
        print(pg["text"][:300])
