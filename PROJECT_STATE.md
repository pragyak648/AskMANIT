# AskMANIT — Project State

**Last updated:** 2026-09-24T00:00:00+05:30
**Current phase:** Phase 0 — Bootstrap
**Current task:** T0.3
**Overall status:** In progress

## How to resume
1. Read `tasks/tasks.json`.
2. Find the first task with `"status": "in_progress"`. If none, find the
   first task with `"status": "todo"` whose `depends_on` are all `"done"`.
3. That is your next task. Work on ONLY that task.
4. On completion: set its status to `"done"`, fill `completed_at`, add a
   one-line `notes` entry, then update the "Current task" line above to the
   next task's ID.
5. Commit with message: `feat(<task_id>): <short description>`

## Decisions log
- 2026-09-24 — Chose LangChain over LlamaIndex: see Section 2 of spec.
- 2026-09-24 — ChromaDB for local persistent vector store (no cloud dependency).
- 2026-09-24 — BAAI/bge-small-en-v1.5 embeddings for zero-cost local inference.

## Blockers
- (none yet)

## Eval results (filled in during Phase 4)
- Baseline faithfulness: TBD
- Baseline context precision: TBD
- Post-hybrid-search faithfulness: TBD
