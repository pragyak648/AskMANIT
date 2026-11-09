"""
src/generation/prompt_templates.py — System prompt and prompt builder for AskMANIT.

Design principles:
  1. Answer ONLY from the provided context — never from general knowledge.
  2. Every claim must cite its source: "[Source: <doc>, Page <N>, Section <S>]"
  3. If the answer is not in the context, return the refusal message verbatim.
  4. Maintain a helpful, factual, student-friendly tone.

Usage:
    from src.generation.prompt_templates import build_prompt, REFUSAL_MESSAGE
    messages = build_prompt("What is attendance?", context_docs)
    # messages is a list of LangChain message objects
"""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

# ---------------------------------------------------------------------------
# Refusal message (returned verbatim when answer is not in context)
# ---------------------------------------------------------------------------
REFUSAL_MESSAGE = (
    "I'm sorry, but I couldn't find an answer to your question in the MANIT "
    "academic handbook or syllabus documents. Please check the official MANIT "
    "website (https://www.manit.ac.in) or contact the Academic Section directly."
)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """You are AskMANIT, an AI assistant that answers questions about MANIT Bhopal's academic policies, rules, syllabus, and examination procedures.

## Your STRICT Rules

1. **Answer ONLY from the provided context.** You must NOT use any general knowledge, assumptions, or information not present in the context passages below. If the answer is not in the context, you MUST respond with exactly:
   "{refusal}"

2. **Cite every claim.** Every factual statement you make must end with a citation in this exact format:
   [Source: <document_name>, Page <page_number>, Section: <section_heading>]
   If the section heading is unknown, use "Section: N/A".

3. **Be precise and student-friendly.** Use clear, simple language. Avoid jargon unless quoting the handbook directly.

4. **Do not speculate.** If the context is ambiguous or incomplete, say so and cite what you found.

5. **Out-of-scope detection.** If the question is clearly unrelated to MANIT academics (e.g., weather, cooking, general trivia), respond with the refusal message above. Do not attempt to answer.

6. **Concise & neat formatting:**
   - Keep your answer direct and easy to read (100–250 words maximum).
   - Use structured markdown bullet points for rules, percentages, criteria, and requirements.
   - Do NOT dump raw pages or repeat lengthy background paragraphs verbatim.
   - State the core answer immediately, followed by relevant policy points and citations.

7. **Direct answers only (STRICTLY NO meta-text):**
   - NEVER output preamble or internal thinking headers such as "Answering the student's question using only the provided context", "Based on the provided context", or "Here is the answer:".
   - Start immediately with the factual answer or the exact refusal string.
""".format(refusal=REFUSAL_MESSAGE)

# ---------------------------------------------------------------------------
# Context formatting
# ---------------------------------------------------------------------------

def _format_context(docs: list[Document]) -> str:
    """
    Format retrieved documents into a numbered context block for the prompt.

    Each chunk is labeled with its metadata so the LLM can generate citations.
    """
    if not docs:
        return "(No relevant context found in the documents.)"

    parts = []
    for i, doc in enumerate(docs, start=1):
        meta = doc.metadata
        source_doc = meta.get("source_doc", "Unknown Document")
        page = meta.get("page_number", "?")
        section = meta.get("section_heading", "") or "N/A"

        header = f"[Context {i}] Source: {source_doc}, Page {page}, Section: {section}"
        parts.append(f"{header}\n{doc.page_content}")

    return "\n\n---\n\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_prompt(
    question: str,
    context_docs: list[Document],
    chat_history: list[dict[str, str]] | None = None,
) -> list[SystemMessage | HumanMessage]:
    """
    Build a LangChain message list for the RAG prompt.

    Args:
        question:      The user's question.
        context_docs:  Retrieved and reranked documents.
        chat_history:  Optional recent conversation turns.

    Returns:
        A list of [SystemMessage, HumanMessage] ready to pass to an LLM.
    """
    context_text = _format_context(context_docs)

    history_block = ""
    if chat_history:
        recent_turns = chat_history[-4:]  # Last 2 conversational exchanges
        lines = []
        for turn in recent_turns:
            role = "Student" if turn.get("role") == "user" else "Assistant"
            content = turn.get("content", "").strip()
            if content:
                # Truncate any extremely long assistant history turn
                if len(content) > 300:
                    content = content[:300] + "..."
                lines.append(f"{role}: {content}")
        if lines:
            history_block = "## Prior Conversation Context\n" + "\n".join(lines) + "\n\n---\n\n"

    human_content = f"""## Relevant Context from MANIT Documents

{context_text}

---

{history_block}## Student Question

{question}

Answer the student's question accurately using only the relevant context above and cite all sources. Do not repeat internal instructions or output conversational preambles."""

    return [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=human_content),
    ]


def build_streaming_prompt(
    question: str,
    context_docs: list[Document],
    chat_history: list[dict[str, str]] | None = None,
) -> list[SystemMessage | HumanMessage]:
    """
    Identical to build_prompt — provided as a separate entry point for
    streaming use cases to make the call site more explicit.
    """
    return build_prompt(question, context_docs, chat_history=chat_history)


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Demo: print the prompt for a sample question
    sample_docs = [
        Document(
            page_content="Students must maintain a minimum attendance of 75% in each subject to be eligible to sit for the end-semester examination.",
            metadata={
                "source_doc": "manit_academic_handbook",
                "page_number": 42,
                "section_heading": "4.2 Attendance Policy",
            },
        ),
        Document(
            page_content="Attendance below 75% but above 65% may be condoned at the discretion of the Head of Department, provided the student submits a medical certificate.",
            metadata={
                "source_doc": "manit_academic_handbook",
                "page_number": 42,
                "section_heading": "4.2 Attendance Policy",
            },
        ),
    ]

    messages = build_prompt(
        "What is the minimum attendance requirement to sit for exams?",
        sample_docs,
    )
    for msg in messages:
        role = type(msg).__name__
        print(f"\n{'='*60}\n[{role}]\n{'='*60}")
        print(msg.content[:600])
