"""
src/eval/run_eval.py — Evaluation runner for AskMANIT RAG pipeline.

Loads Q&A test cases from data/eval/eval_set.json, runs each through the pipeline,
evaluates retrieval precision, refusal adherence, and latency, and saves
a timestamped report to logs/.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import settings, PROJECT_ROOT
from src.generation.prompt_templates import REFUSAL_MESSAGE
from src.generation.rag_pipeline import get_pipeline


def run_evaluation(
    eval_set_path: Path | None = None,
    sample_limit: int | None = None,
) -> dict[str, Any]:
    """
    Run evaluation on the test set.

    Args:
        eval_set_path: Path to eval JSON file (defaults to data/eval/eval_set.json).
        sample_limit: Optional maximum number of test cases to run.

    Returns:
        Structured evaluation report dict.
    """
    path = eval_set_path or (PROJECT_ROOT / "data" / "eval" / "eval_set.json")
    if not path.exists():
        raise FileNotFoundError(f"Eval set not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    if sample_limit:
        cases = cases[:sample_limit]

    pipeline = get_pipeline()
    results = []

    retrieval_hits = 0
    refusal_correct = 0
    total_in_scope = 0
    total_out_of_scope = 0

    total_latency_ms = 0

    print(f"\n🧪 Running AskMANIT Evaluation ({len(cases)} test cases)...")

    for idx, case in enumerate(cases, start=1):
        q = case["question"]
        cat = case.get("category", "general")
        exp_doc = case.get("relevant_source_doc")
        exp_page = case.get("relevant_page_number")

        t0 = time.time()
        res = pipeline.run_query(q)
        elapsed_ms = round((time.time() - t0) * 1000)
        total_latency_ms += elapsed_ms

        answer = res.get("answer", "")
        sources = res.get("sources", [])

        # Check retrieval hit
        hit = False
        if exp_doc:
            total_in_scope += 1
            for s in sources:
                src_doc = s.get("source_doc")
                src_page = s.get("page_number")
                if src_doc == exp_doc and (exp_page is None or src_page == exp_page):
                    hit = True
                    break
            if hit:
                retrieval_hits += 1

        # Check out-of-scope refusal
        is_refusal = (
            "couldn't find an answer to your question in the MANIT" in answer
            or REFUSAL_MESSAGE in answer
            or "(No relevant context found" in answer
        )
        refusal_ok = None
        if cat == "out_of_scope":
            total_out_of_scope += 1
            refusal_ok = is_refusal
            if is_refusal:
                refusal_correct += 1

        case_result = {
            "id": case.get("id", f"case_{idx}"),
            "question": q,
            "category": cat,
            "expected_doc": exp_doc,
            "expected_page": exp_page,
            "retrieval_hit": hit if exp_doc else None,
            "is_refusal": is_refusal,
            "refusal_accurate": refusal_ok,
            "latency_ms": elapsed_ms,
            "top_source": sources[0] if sources else None,
        }
        results.append(case_result)

        status_icon = "✅" if (hit or (cat == "out_of_scope" and is_refusal)) else "⚠️"
        print(f"  [{idx}/{len(cases)}] {status_icon} [{cat.upper()}] {q[:60]}... ({elapsed_ms}ms)")

    # Aggregate metrics
    hit_rate = (retrieval_hits / max(1, total_in_scope)) if total_in_scope else 1.0
    refusal_accuracy = (refusal_correct / max(1, total_out_of_scope)) if total_out_of_scope else 1.0
    avg_latency = round(total_latency_ms / max(1, len(cases)))

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_cases": len(cases),
        "in_scope_cases": total_in_scope,
        "out_of_scope_cases": total_out_of_scope,
        "metrics": {
            "retrieval_hit_rate": round(hit_rate, 4),
            "refusal_accuracy": round(refusal_accuracy, 4),
            "average_latency_ms": avg_latency,
        },
        "results": results,
    }

    # Save report to logs/
    logs_dir = settings.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    report_filename = f"eval_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = logs_dir / report_filename

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📊 Evaluation Summary:")
    print(f"   • In-Scope Retrieval Hit Rate: {hit_rate * 100:.1f}% ({retrieval_hits}/{total_in_scope})")
    print(f"   • Out-Of-Scope Refusal Rate:   {refusal_accuracy * 100:.1f}% ({refusal_correct}/{total_out_of_scope})")
    print(f"   • Average Query Latency:       {avg_latency} ms")
    print(f"   • Saved full report:           {report_path}")

    return report

