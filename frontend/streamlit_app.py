"""
frontend/streamlit_app.py — Premium Institutional AI Chatbot for AskMANIT.

Design System (Second Iteration Refinement):
  - Midnight Black (#030407) — Main viewport background
  - Deep Charcoal (#0B0E14)  — Sidebar & secondary containers
  - Graphite (#121720)       — Cards, panels & input surfaces
  - Electric Cobalt (#1558C9) — Primary actions, focus & accents
  - Light Silver (#C5CBD5)   — Secondary text & interface icons
  - Pure White (#F5F7FA)     — Primary headings & high-contrast text
  - Muted Grey (#737D8D)     — Metadata, placeholders & labels
  - Subtle Border (#202733)  — Clean dividers & component boundaries

Typography: Geist / Inter with JetBrains Mono for metrics and citations.
Clean, restrained layout inspired by Linear, ChatGPT, Perplexity, and Vercel.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Assets & Paths
LOGO_PATH = PROJECT_ROOT / "frontend" / "assets" / "manit_logo.png"
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
LOGS_DIR = PROJECT_ROOT / "logs"
FEEDBACK_LOG_PATH = LOGS_DIR / "feedback.jsonl"
QUERIES_LOG_PATH = LOGS_DIR / "queries.jsonl"


def get_logo_base64() -> str:
    """Encode the official MANIT emblem to base64 for HTML embedding."""
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


LOGO_B64 = get_logo_base64()

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AskMANIT — Institutional Academic Assistant",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Design System CSS (Midnight Black × Electric Cobalt × Light Silver)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-midnight: #030407;
        --surface-charcoal: #0B0E14;
        --surface-graphite: #121720;
        --surface-graphite-hover: #171E2B;
        --accent-cobalt: #1558C9;
        --accent-cobalt-hover: #1C67E3;
        --text-white: #F5F7FA;
        --text-silver: #C5CBD5;
        --text-muted: #737D8D;
        --border-subtle: #202733;
        --border-focus: #1558C9;
    }

    /* Core Application Reset */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: var(--bg-midnight) !important;
        color: var(--text-white) !important;
        font-family: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Header Bar */
    header[data-testid="stHeader"] {
        background-color: rgba(3, 4, 7, 0.85) !important;
        backdrop-filter: blur(14px) !important;
        border-bottom: 1px solid var(--border-subtle) !important;
    }

    /* Sidebar Styling — Linear / ChatGPT inspired */
    [data-testid="stSidebar"] {
        background-color: var(--surface-charcoal) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: var(--surface-charcoal) !important;
        padding: 1.25rem 1rem !important;
    }

    /* Main Container Bounds */
    .main .block-container {
        max-width: 840px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 5.5rem !important;
        margin: 0 auto !important;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-white) !important;
        font-family: 'Geist', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }

    p, span, div, li {
        color: var(--text-silver);
        font-family: 'Geist', sans-serif;
        line-height: 1.6;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Top Nav Bar */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 1.1rem;
        margin-bottom: 1.25rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .top-nav-title {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--text-silver);
    }
    .top-nav-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--surface-graphite);
        border: 1px solid var(--border-subtle);
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 0.72rem;
        color: var(--text-silver);
        font-family: 'JetBrains Mono', monospace;
    }
    .live-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #10B981;
    }
    .live-dot.offline {
        background-color: #F59E0B;
    }

    /* Welcome / Empty State Screen */
    .welcome-container {
        text-align: center;
        padding: 2.75rem 0.5rem 1.75rem 0.5rem;
    }
    .welcome-crest {
        width: 52px;
        height: 52px;
        object-fit: contain;
        margin-bottom: 1.25rem;
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.45));
    }
    .welcome-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: var(--surface-graphite);
        border: 1px solid var(--border-subtle);
        border-radius: 999px;
        padding: 3px 11px;
        font-size: 0.7rem;
        font-weight: 500;
        color: var(--text-silver);
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0.85rem;
    }
    .welcome-title {
        font-size: 2.15rem;
        font-weight: 600;
        color: var(--text-white);
        margin: 0 0 0.65rem 0;
        letter-spacing: -0.03em;
        line-height: 1.25;
    }
    .welcome-subtitle {
        font-size: 0.95rem;
        color: var(--text-muted);
        max-width: 580px;
        margin: 0 auto 2.25rem auto;
        line-height: 1.6;
    }

    /* Question Prompt Cards */
    .prompt-card {
        background: var(--surface-graphite);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 1rem 1.15rem;
        text-align: left;
        transition: all 0.18s ease;
        cursor: pointer;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .prompt-card:hover {
        border-color: var(--accent-cobalt);
        background: var(--surface-graphite-hover);
        transform: translateY(-1px);
    }
    .prompt-header {
        display: flex;
        align-items: center;
        gap: 9px;
        margin-bottom: 0.4rem;
    }
    .prompt-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 6px;
        background: rgba(21, 88, 201, 0.12);
        color: var(--accent-cobalt);
        flex-shrink: 0;
    }
    .prompt-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-white);
        letter-spacing: -0.01em;
    }
    .prompt-desc {
        font-size: 0.78rem;
        color: var(--text-muted);
        line-height: 1.45;
        margin: 0;
    }

    /* Message Bubbles */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0.9rem 0 !important;
        margin: 0 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        display: flex;
        justify-content: flex-end;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background-color: var(--surface-graphite) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.15rem !important;
        color: var(--text-white) !important;
        font-size: 0.92rem !important;
        max-width: 80% !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    }
    [data-testid="chatAvatarIcon-user"] {
        background-color: var(--surface-graphite) !important;
        color: var(--text-white) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px !important;
    }
    [data-testid="chatAvatarIcon-user"] svg {
        fill: var(--text-silver) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        padding: 0.15rem 0.25rem !important;
        color: var(--text-white) !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
    }

    /* Custom Chat Avatar styling */
    [data-testid="stChatMessage"] img {
        width: 30px !important;
        height: 30px !important;
        object-fit: contain !important;
        border-radius: 6px !important;
        background: var(--surface-graphite) !important;
        padding: 2px !important;
        border: 1px solid var(--border-subtle) !important;
    }

    /* Citations Panel */
    .citation-container {
        background: var(--surface-graphite);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-top: 0.75rem;
    }
    .citation-item {
        border-left: 2px solid var(--accent-cobalt);
        padding-left: 0.75rem;
        margin-bottom: 0.75rem;
    }
    .citation-item:last-child {
        margin-bottom: 0;
    }
    .citation-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text-white);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
    }
    .citation-meta {
        font-size: 0.7rem;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
    }
    .citation-text {
        font-size: 0.78rem;
        color: var(--text-silver);
        line-height: 1.5;
        margin: 0.25rem 0 0 0;
    }

    /* Response Action Toolbar */
    .response-actions {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 0.5rem;
        padding-top: 0.4rem;
    }
    .action-btn {
        background: transparent;
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        color: var(--text-muted);
        padding: 3px 8px;
        font-size: 0.72rem;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        transition: all 0.15s ease;
        cursor: pointer;
    }
    .action-btn:hover {
        color: var(--text-white);
        border-color: var(--accent-cobalt);
        background: var(--surface-graphite);
    }

    /* Buttons styling */
    .stButton > button {
        background-color: var(--surface-graphite) !important;
        color: var(--text-silver) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        font-family: 'Geist', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 0.85rem !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        background-color: var(--surface-graphite-hover) !important;
        color: var(--text-white) !important;
        border-color: var(--accent-cobalt) !important;
    }

    /* Primary Sidebar New Chat Button */
    .sidebar-new-chat > div > button {
        background-color: var(--accent-cobalt) !important;
        color: var(--text-white) !important;
        border: 1px solid var(--accent-cobalt) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        width: 100% !important;
        padding: 0.5rem 0.85rem !important;
        margin-bottom: 0.75rem !important;
    }
    .sidebar-new-chat > div > button:hover {
        background-color: var(--accent-cobalt-hover) !important;
        border-color: var(--accent-cobalt-hover) !important;
    }

    /* Sidebar Conversations List */
    .conv-item-btn > div > button {
        text-align: left !important;
        justify-content: flex-start !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-silver) !important;
        font-size: 0.8rem !important;
        padding: 0.38rem 0.65rem !important;
        margin-bottom: 2px !important;
        border-radius: 6px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        width: 100% !important;
    }
    .conv-item-btn > div > button:hover {
        background: var(--surface-graphite) !important;
        border-color: var(--border-subtle) !important;
        color: var(--text-white) !important;
    }
    .conv-item-active > div > button {
        background: var(--surface-graphite) !important;
        border-color: var(--accent-cobalt) !important;
        color: var(--text-white) !important;
        font-weight: 500 !important;
    }

    /* Input Composer */
    [data-testid="stChatInput"] {
        background-color: var(--surface-graphite) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 1px var(--border-focus), 0 10px 30px rgba(21, 88, 201, 0.12) !important;
    }
    [data-testid="stChatInputTextArea"] {
        color: var(--text-white) !important;
        font-family: 'Geist', sans-serif !important;
        font-size: 0.92rem !important;
    }
    [data-testid="stChatInputSubmitButton"] {
        color: var(--text-white) !important;
        background-color: var(--accent-cobalt) !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInputSubmitButton"]:hover {
        background-color: var(--accent-cobalt-hover) !important;
    }

    /* Search input in sidebar */
    [data-testid="stSidebar"] [data-testid="stTextInput"] input {
        background-color: var(--bg-midnight) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 7px !important;
        font-size: 0.78rem !important;
        color: var(--text-white) !important;
        padding: 0.4rem 0.65rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
        border-color: var(--accent-cobalt) !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background-color: var(--surface-graphite) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        margin-top: 0.5rem !important;
    }
    [data-testid="stExpander"] summary {
        color: var(--text-silver) !important;
        font-size: 0.78rem !important;
    }
    [data-testid="stExpanderDetails"] {
        padding: 0.75rem !important;
        border-top: 1px solid var(--border-subtle) !important;
    }

    .composer-hint {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 0.4rem;
        padding: 0 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Backend Integration Helpers
# ---------------------------------------------------------------------------
def fetch_health() -> dict[str, Any] | None:
    """Check FastAPI backend health."""
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=2.5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def query_backend(
    question: str,
    top_k: int = 5,
    chat_history: list[dict[str, str]] | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    """Execute RAG query against FastAPI backend with optional conversational context."""
    url = f"{API_BASE_URL}/query"
    payload = {"question": question, "top_k": top_k}
    if chat_history:
        payload["chat_history"] = [
            {"role": m["role"], "content": m["content"]}
            for m in chat_history
            if "role" in m and "content" in m
        ]
    try:
        resp = requests.post(url, json=payload, timeout=180)
        if resp.status_code == 200:
            return resp.json(), None
        try:
            err_detail = resp.json().get("detail", resp.text)
        except Exception:
            err_detail = resp.text
        return None, f"API Error ({resp.status_code}): {err_detail}"
    except requests.exceptions.ConnectionError:
        return None, (
            f"Could not connect to backend at `{API_BASE_URL}`. "
            "Ensure the FastAPI service is running."
        )
    except Exception as exc:
        return None, f"Request failed: {str(exc)}"


def log_feedback(question: str, answer: str, rating: str) -> bool:
    """Log user thumbs up/down rating."""
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "rating": rating,
            "question": question,
            "answer": answer,
        }
        with open(FEEDBACK_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False


def load_analytics() -> dict[str, Any]:
    """Aggregate query volume, latency, tokens, and feedback for diagnostics."""
    total_queries = 0
    total_latency = 0
    total_tokens = 0
    total_cost = 0.0
    recent_queries: list[dict[str, Any]] = []

    if QUERIES_LOG_PATH.exists():
        with open(QUERIES_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        q = json.loads(line)
                        total_queries += 1
                        total_latency += q.get("latency_breakdown", {}).get("total_ms", 0)
                        tc = q.get("token_counts", {})
                        total_tokens += tc.get("total_tokens", 0)
                        total_cost += tc.get("estimated_cost_usd", 0.0)
                        recent_queries.append(q)
                    except Exception:
                        pass

    thumbs_up = 0
    thumbs_down = 0
    if FEEDBACK_LOG_PATH.exists():
        with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        fb = json.loads(line)
                        if fb.get("rating") == "positive":
                            thumbs_up += 1
                        elif fb.get("rating") == "negative":
                            thumbs_down += 1
                    except Exception:
                        pass

    avg_latency = round(total_latency / total_queries) if total_queries else 0
    return {
        "queries": total_queries,
        "avg_latency_ms": avg_latency,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
        "recent_queries": recent_queries[-10:],
    }


# ---------------------------------------------------------------------------
# State Initialization (Multi-conversation session storage)
# ---------------------------------------------------------------------------
if "conversations" not in st.session_state:
    st.session_state.conversations = {
        "conv_default": {
            "title": "Current Session",
            "created_at": datetime.now().strftime("%b %d, %H:%M"),
            "messages": [],
        }
    }

if "active_conv_id" not in st.session_state:
    st.session_state.active_conv_id = "conv_default"

if "current_view" not in st.session_state:
    st.session_state.current_view = "chat"  # "chat" or "diagnostics"

if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = {}

# Ensure active conversation exists
if st.session_state.active_conv_id not in st.session_state.conversations:
    st.session_state.active_conv_id = list(st.session_state.conversations.keys())[0]

current_conv = st.session_state.conversations[st.session_state.active_conv_id]
messages = current_conv["messages"]

# Fetch backend health
health_info = fetch_health()
is_online = health_info is not None
active_provider = health_info.get("llm_provider", "local") if health_info else "offline"
doc_count = health_info.get("document_count", 31) if health_info else 31
model_name = "llama3.2" if active_provider == "ollama" else active_provider

# ---------------------------------------------------------------------------
# Sidebar (Compact, Linear / ChatGPT Inspired)
# ---------------------------------------------------------------------------
with st.sidebar:
    # 1. AskMANIT Brand & Institutional Seal
    sidebar_crest_html = (
        f'<img src="data:image/png;base64,{LOGO_B64}" width="28" height="28" style="object-fit: contain; flex-shrink: 0;" />'
        if LOGO_B64
        else '<div style="width:28px;height:28px;background:#1558C9;border-radius:6px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.8rem;color:#F5F7FA;">M</div>'
    )

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.15rem; padding-bottom: 0.25rem;">
            <div style="display: flex; align-items: center; gap: 9px;">
                {sidebar_crest_html}
                <div style="font-size: 0.98rem; font-weight: 600; color: #F5F7FA; letter-spacing: -0.01em;">
                    AskMANIT
                </div>
            </div>
            <div style="display: inline-flex; align-items: center; gap: 5px; font-size: 0.68rem; color: {'#10B981' if is_online else '#F59E0B'}; font-family: 'JetBrains Mono', monospace;">
                <span class="live-dot {'offline' if not is_online else ''}"></span>
                {'Online' if is_online else 'Standby'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Primary Action: New Conversation
    st.markdown('<div class="sidebar-new-chat">', unsafe_allow_html=True)
    if st.button("＋  New Conversation", use_container_width=True, key="new_chat_trigger"):
        new_id = f"conv_{int(time.time())}"
        st.session_state.conversations[new_id] = {
            "title": "New Conversation",
            "created_at": datetime.now().strftime("%b %d, %H:%M"),
            "messages": [],
        }
        st.session_state.active_conv_id = new_id
        st.session_state.current_view = "chat"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Search Conversations
    search_query = st.text_input(
        "Search conversations",
        placeholder="Search past inquiries...",
        label_visibility="collapsed",
        key="search_conv_input",
    )

    # 4. Recent Conversations List
    st.markdown(
        """
        <div style="font-size: 0.68rem; font-weight: 600; text-transform: uppercase; color: #737D8D; letter-spacing: 0.05em; margin: 0.9rem 0 0.4rem 0.25rem;">
            Conversations
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_conv_ids = list(st.session_state.conversations.keys())
    filtered_ids = [
        cid
        for cid in all_conv_ids
        if not search_query
        or search_query.lower() in st.session_state.conversations[cid]["title"].lower()
    ]

    for cid in filtered_ids:
        c_data = st.session_state.conversations[cid]
        c_title = c_data["title"]
        is_active = cid == st.session_state.active_conv_id
        btn_class = "conv-item-btn conv-item-active" if is_active else "conv-item-btn"

        st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
        # Truncate title nicely
        display_title = (c_title[:28] + "…") if len(c_title) > 28 else c_title
        if st.button(f"💬  {display_title}", key=f"select_{cid}", use_container_width=True):
            st.session_state.active_conv_id = cid
            st.session_state.current_view = "chat"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. Official Knowledge Sources (Compact & Verified)
    st.markdown(
        """
        <div style="font-size: 0.68rem; font-weight: 600; text-transform: uppercase; color: #737D8D; letter-spacing: 0.05em; margin: 1.4rem 0 0.45rem 0.25rem;">
            Official Grounding Sources
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="background: #121720; border: 1px solid #202733; border-radius: 8px; padding: 0.65rem 0.75rem; font-size: 0.74rem; line-height: 1.6;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #F5F7FA; font-weight: 500;">📖 Student Handbook 2026</span>
                <span style="font-size: 0.65rem; color: #10B981; font-family: 'JetBrains Mono', monospace;">✓ Active</span>
            </div>
            <div style="color: #737D8D; font-size: 0.68rem; margin-bottom: 6px;">
                22 Chapters • Attendance & Ordinances
            </div>
            <div style="border-top: 1px solid #202733; padding-top: 5px; color: #C5CBD5; font-size: 0.7rem;">
                • Academic Regulations & Rules<br/>
                • 10-Point Grading & Backlogs
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 6. User Profile & Settings / Diagnostics Switcher (Bottom)
    st.markdown(
        """
        <div style="margin-top: 2rem; border-top: 1px solid #202733; padding-top: 0.85rem;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 26px; height: 26px; border-radius: 50%; background: #1558C9; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 600; color: #F5F7FA;">
                        MS
                    </div>
                    <div>
                        <div style="font-size: 0.78rem; font-weight: 500; color: #F5F7FA; line-height: 1.2;">MANIT Scholar</div>
                        <div style="font-size: 0.66rem; color: #737D8D;">Academic Student Portal</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Secondary Navigation: Diagnostics & Reset
    st.markdown("<div style='margin-top: 0.65rem;'></div>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        if st.session_state.current_view == "diagnostics":
            if st.button("💬 Chat", use_container_width=True, key="switch_to_chat"):
                st.session_state.current_view = "chat"
                st.rerun()
        else:
            if st.button("⚙️ Admin", use_container_width=True, key="switch_to_diag"):
                st.session_state.current_view = "diagnostics"
                st.rerun()

    with col_d2:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_active_conv"):
            current_conv["messages"] = []
            st.rerun()


# ===========================================================================
# VIEW 1: ADMIN & SYSTEM DIAGNOSTICS DASHBOARD
# ===========================================================================
if st.session_state.current_view == "diagnostics":
    st.markdown(
        """
        <div class="top-nav">
            <div class="top-nav-title">
                <span style="font-weight: 600; color: #F5F7FA;">Admin Diagnostics & Telemetry</span>
                <span style="font-size: 0.75rem; color: #737D8D;">/ Internal System Performance</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("← Return to Academic Assistant", key="back_to_chat_diag"):
        st.session_state.current_view = "chat"
        st.rerun()

    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

    # 4 Key Metrics Cards
    analytics = load_analytics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div style="background: #121720; border: 1px solid #202733; border-radius: 8px; padding: 0.85rem 1rem;">
                <div style="font-size: 0.68rem; text-transform: uppercase; color: #737D8D; font-weight: 600;">System Health</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: {'#10B981' if is_online else '#F59E0B'}; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                    {'Active & Grounded' if is_online else 'Standby'}
                </div>
                <div style="font-size: 0.7rem; color: #737D8D; margin-top: 4px;">Host: 127.0.0.1:8000</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div style="background: #121720; border: 1px solid #202733; border-radius: 8px; padding: 0.85rem 1rem;">
                <div style="font-size: 0.68rem; text-transform: uppercase; color: #737D8D; font-weight: 600;">Model Engine</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #F5F7FA; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                    {model_name}
                </div>
                <div style="font-size: 0.7rem; color: #737D8D; margin-top: 4px;">Provider: {active_provider}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div style="background: #121720; border: 1px solid #202733; border-radius: 8px; padding: 0.85rem 1rem;">
                <div style="font-size: 0.68rem; text-transform: uppercase; color: #737D8D; font-weight: 600;">Total Inquiries</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #F5F7FA; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                    {analytics['queries']}
                </div>
                <div style="font-size: 0.7rem; color: #737D8D; margin-top: 4px;">Avg Latency: {analytics['avg_latency_ms']}ms</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div style="background: #121720; border: 1px solid #202733; border-radius: 8px; padding: 0.85rem 1rem;">
                <div style="font-size: 0.68rem; text-transform: uppercase; color: #737D8D; font-weight: 600;">Vector Store</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #F5F7FA; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                    {doc_count} Chunks
                </div>
                <div style="font-size: 0.7rem; color: #737D8D; margin-top: 4px;">ChromaDB Persistent</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Detailed Telemetry Table
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Telemetry & Feedback Metrics")
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.markdown(
            f"""
            <div style="background: #121720; border: 1px solid #202733; border-radius: 8px; padding: 1rem;">
                <div style="font-weight: 600; color: #F5F7FA; font-size: 0.85rem; margin-bottom: 0.75rem;">Quality & Satisfaction</div>
                <div style="display: flex; gap: 12px; margin-bottom: 0.75rem;">
                    <div style="flex: 1; background: #0B0E14; padding: 8px; border-radius: 6px; border: 1px solid #202733;">
                        <div style="font-size: 0.68rem; color: #737D8D;">Helpful (👍)</div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #10B981; font-family: 'JetBrains Mono', monospace;">{analytics['thumbs_up']}</div>
                    </div>
                    <div style="flex: 1; background: #0B0E14; padding: 8px; border-radius: 6px; border: 1px solid #202733;">
                        <div style="font-size: 0.68rem; color: #737D8D;">Flagged (👎)</div>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #F59E0B; font-family: 'JetBrains Mono', monospace;">{analytics['thumbs_down']}</div>
                    </div>
                </div>
                <div style="font-size: 0.74rem; color: #737D8D;">
                    Grounded citations ensure verified compliance with MANIT ordinances.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_t2:
        st.markdown(
            f"""
            <div style="background: #121720; border: 1px solid #202733; border-radius: 8px; padding: 1rem;">
                <div style="font-weight: 600; color: #F5F7FA; font-size: 0.85rem; margin-bottom: 0.75rem;">Pipeline Specifications</div>
                <div style="font-size: 0.75rem; color: #C5CBD5; line-height: 1.8;">
                    <div>• <strong>Embeddings:</strong> BAAI/bge-small-en-v1.5 (384-dim)</div>
                    <div>• <strong>Retrieval:</strong> Hybrid Dense Vector + BM25 Lexical</div>
                    <div>• <strong>Reranker:</strong> FlashRank ms-marco-MiniLM-L-12-v2</div>
                    <div>• <strong>Ordinance Grounding:</strong> Strict Anti-Hallucination Guardrails</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()


# ===========================================================================
# VIEW 2: STUDENT ACADEMIC ASSISTANT (CLEAN, RESTRAINED CONVERSATION)
# ===========================================================================

# Top Navigation Bar (Minimalist)
st.markdown(
    f"""
    <div class="top-nav">
        <div class="top-nav-title">
            <span style="font-weight: 600; color: #F5F7FA;">AskMANIT</span>
            <span style="font-size: 0.78rem; color: #737D8D;">/ Academic Regulations & Handbook Assistant</span>
        </div>
        <div class="top-nav-pill">
            <span class="live-dot {'offline' if not is_online else ''}"></span>
            <span>MANIT Verified</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Welcome / Empty Screen (When no messages exist in active conversation)
# ---------------------------------------------------------------------------
selected_prompt = None

if len(messages) == 0:
    crest_html = (
        f'<img src="data:image/png;base64,{LOGO_B64}" class="welcome-crest" />'
        if LOGO_B64
        else ""
    )

    st.markdown(
        f"""
        <div class="welcome-container">
            {crest_html}
            <div class="welcome-badge">✦ Institutional RAG Intelligence</div>
            <h1 class="welcome-title">Your Academic Companion.</h1>
            <p class="welcome-subtitle">
                Get clear, reliable answers about MANIT academic policies, regulations and student guidelines — grounded in official institutional documents.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Interactive Suggested Inquiries Cards (2x2 Grid)
    # Lucide-style minimal SVGs
    icon_calendar = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1558C9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>"""
    icon_award = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1558C9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>"""
    icon_file = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1558C9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>"""
    icon_refresh = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1558C9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>"""

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span class="prompt-icon">{icon_calendar}</span>
                <span style="font-size: 0.86rem; font-weight: 600; color: #F5F7FA;">Attendance Requirements</span>
            </div>
            <div style="font-size: 0.74rem; color: #737D8D; margin-bottom: 8px;">
                Minimum 75% criteria, condonation limits & medical certificates
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Verify Attendance Criteria →", use_container_width=True, key="card_btn_1"):
            selected_prompt = "What is the minimum attendance requirement to appear for exams at MANIT, and what are the condonation rules?"

        st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span class="prompt-icon">{icon_file}</span>
                <span style="font-size: 0.86rem; font-weight: 600; color: #F5F7FA;">Examination Regulations</span>
            </div>
            <div style="font-size: 0.74rem; color: #737D8D; margin-bottom: 8px;">
                Mid-term & end-term weightage, re-evaluation & exam conduct
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Check Examination Rules →", use_container_width=True, key="card_btn_3"):
            selected_prompt = "What are the key examination regulations at MANIT regarding mid-term exams, end-semester evaluation, and unfair means?"

    with col2:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span class="prompt-icon">{icon_award}</span>
                <span style="font-size: 0.86rem; font-weight: 600; color: #F5F7FA;">Grading & CGPA</span>
            </div>
            <div style="font-size: 0.74rem; color: #737D8D; margin-bottom: 8px;">
                10-point scale, SGPA calculation & honors degree eligibility
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("View Grading Framework →", use_container_width=True, key="card_btn_2"):
            selected_prompt = "Explain the MANIT 10-point grading scale, SGPA/CGPA calculation and criteria for honors degree."

        st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span class="prompt-icon">{icon_refresh}</span>
                <span style="font-size: 0.86rem; font-weight: 600; color: #F5F7FA;">Backlog & Promotion Rules</span>
            </div>
            <div style="font-size: 0.74rem; color: #737D8D; margin-bottom: 8px;">
                F-grade remediation, summer terms & semester registration limits
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Explore Promotion Directives →", use_container_width=True, key="card_btn_4"):
            selected_prompt = "What happens if a student receives an F grade, how do backlogs work and what are the promotion criteria?"


# ---------------------------------------------------------------------------
# Conversation Stream (Messages, Sources & Response Actions)
# ---------------------------------------------------------------------------
assistant_avatar = str(LOGO_PATH) if LOGO_PATH.exists() else "✦"
user_avatar = "🎓"

for i, msg in enumerate(messages):
    is_assistant = msg["role"] == "assistant"
    avatar_choice = assistant_avatar if is_assistant else user_avatar

    with st.chat_message(msg["role"], avatar=avatar_choice):
        st.markdown(msg["content"])

        # Perplexity-Style Verified Sources Presentation
        sources = msg.get("sources", [])
        if sources:
            with st.expander(f"📚 Grounded Sources & Citations ({len(sources)})", expanded=False):
                for s_idx, src in enumerate(sources, 1):
                    doc_name = src.get("source_doc", "MANIT Handbook")
                    page = src.get("page_number")
                    section = src.get("section_heading", "Policy Section")
                    score = src.get("reranker_score")
                    content = src.get("content", "")

                    score_str = f"Score: {score:.3f}" if score is not None else ""
                    page_str = f"Page {page}" if page else ""

                    st.markdown(
                        f"""
                        <div class="citation-container">
                            <div class="citation-item">
                                <div class="citation-title">
                                    <span>[{s_idx}] {doc_name}</span>
                                    <span class="citation-meta">{page_str} {('• ' + score_str) if score_str else ''}</span>
                                </div>
                                <div style="font-size: 0.72rem; color: #737D8D; margin-top: 2px;">Section: {section}</div>
                                <p class="citation-text">{content}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # Assistant Actions: Copy, Regenerate & Feedback
        if is_assistant:
            fb_key = f"fb_{st.session_state.active_conv_id}_{i}"
            has_voted = st.session_state.feedback_given.get(fb_key)

            col_act1, col_act2, col_act3, col_act4 = st.columns([0.08, 0.08, 0.14, 0.7])
            with col_act1:
                if st.button("👍", key=f"up_{i}", disabled=has_voted is not None, help="Helpful answer"):
                    prev_q = messages[i - 1]["content"] if i > 0 else ""
                    log_feedback(prev_q, msg["content"], "positive")
                    st.session_state.feedback_given[fb_key] = "up"
                    st.toast("Feedback recorded: Helpful", icon="✓")
                    st.rerun()

            with col_act2:
                if st.button("👎", key=f"down_{i}", disabled=has_voted is not None, help="Needs improvement"):
                    prev_q = messages[i - 1]["content"] if i > 0 else ""
                    log_feedback(prev_q, msg["content"], "negative")
                    st.session_state.feedback_given[fb_key] = "down"
                    st.toast("Feedback recorded for review", icon="✓")
                    st.rerun()

            with col_act3:
                # Regenerate button for the last message
                if i == len(messages) - 1:
                    if st.button("🔄 Retry", key=f"regen_{i}", help="Regenerate response"):
                        prev_q = messages[i - 1]["content"] if i > 0 else ""
                        if prev_q:
                            # Remove last assistant message and re-run
                            messages.pop()
                            selected_prompt = prev_q

            if has_voted:
                with col_act4:
                    st.caption(f"Rated: {'Helpful' if has_voted == 'up' else 'Flagged for review'}")


# ---------------------------------------------------------------------------
# Message Composer (Graphite Surface, Cobalt Accents)
# ---------------------------------------------------------------------------
st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Input Composer
user_prompt = st.chat_input("Ask any question regarding MANIT academic regulations, exams, grading...")

if selected_prompt:
    user_prompt = selected_prompt

if user_prompt:
    # Update conversation title if this is the first message
    if len(messages) == 0:
        clean_title = user_prompt.strip()
        if len(clean_title) > 30:
            clean_title = clean_title[:30] + "…"
        current_conv["title"] = clean_title

    # Append User Message
    messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(user_prompt)

    # Generate Assistant Response
    with st.chat_message("assistant", avatar=assistant_avatar):
        with st.spinner("Consulting official MANIT Handbook & Academic Ordinances..."):
            # Pass prior conversation history for conversational follow-ups
            prior_history = messages[:-1]
            data, error = query_backend(user_prompt, chat_history=prior_history)

            if error:
                st.error(error)
                messages.append(
                    {
                        "role": "assistant",
                        "content": f"⚠️ {error}",
                        "sources": [],
                        "metrics": None,
                    }
                )
            else:
                answer = data.get("answer", "No response generated.")
                sources = data.get("sources", [])
                metrics = {
                    "latency_breakdown": data.get("latency_breakdown", {}),
                    "token_counts": data.get("token_counts", {}),
                }

                st.markdown(answer)

                if sources:
                    with st.expander(f"📚 Grounded Sources & Citations ({len(sources)})", expanded=False):
                        for s_idx, src in enumerate(sources, 1):
                            doc_name = src.get("source_doc", "MANIT Handbook")
                            page = src.get("page_number")
                            section = src.get("section_heading", "Policy Section")
                            score = src.get("reranker_score")
                            content = src.get("content", "")

                            score_str = f"Score: {score:.3f}" if score is not None else ""
                            page_str = f"Page {page}" if page else ""

                            st.markdown(
                                f"""
                                <div class="citation-container">
                                    <div class="citation-item">
                                        <div class="citation-title">
                                            <span>[{s_idx}] {doc_name}</span>
                                            <span class="citation-meta">{page_str} {('• ' + score_str) if score_str else ''}</span>
                                        </div>
                                        <div style="font-size: 0.72rem; color: #737D8D; margin-top: 2px;">Section: {section}</div>
                                        <p class="citation-text">{content}</p>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "metrics": metrics,
                    }
                )
                st.rerun()

# Composer Helper Hint
st.markdown(
    """
    <div class="composer-hint">
        <span>Press <kbd style="background: #121720; border: 1px solid #202733; padding: 2px 5px; border-radius: 4px; font-size: 0.68rem; color: #C5CBD5;">Return ↵</kbd> to send • <kbd style="background: #121720; border: 1px solid #202733; padding: 2px 5px; border-radius: 4px; font-size: 0.68rem; color: #C5CBD5;">Shift + Return</kbd> for new line</span>
        <span>✦ Grounded in official MANIT Bhopal Handbook & Ordinances</span>
    </div>
    """,
    unsafe_allow_html=True,
)
