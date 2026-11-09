"""
scripts/eval.py — CLI evaluation runner for AskMANIT.

Usage:
    # Run evaluation on all cases in data/eval/eval_set.json
    python scripts/eval.py

    # Run on a quick sample of 5 cases
    python scripts/eval.py --sample 5

    # Use a custom evaluation dataset
    python scripts/eval.py --file path/to/eval.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.eval.run_eval import run_evaluation


def main():
    parser = argparse.ArgumentParser(description="AskMANIT RAG Evaluation Runner")
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to custom eval_set.json file",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Limit execution to first N test cases",
    )
    args = parser.parse_args()

    eval_path = Path(args.file) if args.file else None
    run_evaluation(eval_set_path=eval_path, sample_limit=args.sample)


if __name__ == "__main__":
    main()

