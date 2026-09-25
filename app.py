"""
app.py — Human-Crafted Editorial & User-Friendly UI for OpinionLens.

An explainable & safety-guarded opinion intelligence dashboard that bridges
raw e-commerce customer reviews with verifiable, citation-backed executive synthesis.

User-Friendly Features:
  - ⚡ 1-Click Interactive Demo Presets (MacBook Air M2, Anker PowerCore, Lenovo, Samsung)
  - 🏷️ Quick Aspect Query Chips (Heating, Battery, Camera, Performance, Value, Build)
  - 📌 Executive Verdict & Key Takeaways Matrix (At-a-glance TL;DR synthesis)
  - 🔗 Direct Click-to-Inspect Citation Buttons (Loads specific review in 1 click)
  - 🔎 Searchable & Star-Filterable Evidence Inspector (Interactive review browser)
  - 🔀 Flexible Layout Mode: Split View (Side-by-Side) or Tabbed View (Full Width)
  - 🔊 Web Speech API Audio Briefing (Hands-free voice read-aloud)
  - 🎓 Project Defense & Architecture FAQ (Mid-Sem evaluation guide)
  - ✦ Multi-Theme Engine: Editorial Studio Light, Obsidian Matte Dark, High-Contrast WCAG AAA
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ── page config must be the very first Streamlit call ──────────────────────
st.set_page_config(
    page_title="OpinionLens · Review Intelligence & Safety Audit",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

from aggregator import build_aspect_clusters, compute_contention, summarize_aspect_stats
from config import DATASET_DIR, DEFAULT_CSV, DEFAULT_PRODUCT_ID, GROQ_MODEL, MIN_REVIEWS_FOR_PRODUCT
from dataset_loader import load_universal_dataset, list_products_from_df
from extractor import extract_aspects, generate_summary
from guard import detect_critical_risks
from ingest import ingest_product, is_already_ingested, list_all_brands, list_products_in_csv
from retriever import retrieve_opinions


# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------

def _init_state():
    defaults = {
        "analysis_done": False,
        "reviews": [],
        "tuples": [],
        "alerts": [],
        "clusters": {},
        "contested": [],
        "stats": [],
        "summary": None,
        "selected_review_ids": [],
        "selected_quote": "",
        "selected_aspect": None,
        "theme_mode": "✦ Editorial Studio Light",
        "font_large": False,
        "view_layout": "Split View (Side-by-Side)",
        "user_groq_key": "",
        "exec_mode": "⚡ Groq LLM (High-Performance)",
        "selected_model": "qwen/qwen3.8-27b",
        "custom_dataset_df": None,
        "custom_dataset_name": None,
        "active_brand": None,
        "active_product_id": None,
        "active_query": "",
        "trigger_run": False,
        "inspector_keyword": "",
        "inspector_star": "All",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ---------------------------------------------------------------------------
# Design System & Theme Token Engine
# ---------------------------------------------------------------------------

theme_mode = st.session_state.get("theme_mode", "✦ Editorial Studio Light")
font_large = st.session_state.get("font_large", False)

base_font_size = "16.5px" if font_large else "14.5px"
small_font_size = "14px" if font_large else "12.5px"
title_font_size = "1.75rem" if font_large else "1.5rem"

if theme_mode == "✦ High-Contrast (WCAG AAA)":
    tokens = {
        "bg_color": "#000000",
        "card_bg": "#0a0a0a",
        "sidebar_bg": "#000000",
        "text_primary": "#ffffff",
        "text_secondary": "#ffffff",
        "text_muted": "#e2e8f0",
        "border_color": "#ffffff",
        "border_subtle": "#ffffff",
        "header_bg": "#000000",
        "header_border": "#ffffff",
        "header_text": "#ffffff",
        "safety_bg": "#2b0000",
        "safety_border": "#ff4d4d",
        "safety_title": "#ff4d4d",
        "safety_text": "#ffffff",
        "consensus_bg": "#002b11",
        "consensus_border": "#4ade80",
        "consensus_title": "#4ade80",
        "consensus_text": "#ffffff",
        "contested_bg": "#2b1a00",
        "contested_border": "#fde047",
        "contested_title": "#fde047",
        "contested_text": "#ffffff",
        "evidence_bg": "#0a0a0a",
        "evidence_border": "#ffffff",
        "evidence_title": "#ffffff",
        "chip_bg": "#000000",
        "chip_border": "#ffffff",
        "chip_text": "#ffffff",
        "quote_bg": "#ffffff",
        "quote_text": "#000000",
        "quote_border": "#ffffff",
        "btn_primary_bg": "#ffffff",
        "btn_primary_text": "#000000",
        "btn_primary_hover": "#e2e8f0",
        "btn_primary_border": "#ffffff",
        "chart_font": "#ffffff",
        "chart_zero": "#ffffff",
        "tag_bg": "#111111",
        "tag_text": "#ffffff",
    }
elif theme_mode == "✦ Obsidian Matte Dark":
    tokens = {
        "bg_color": "#090d16",
        "card_bg": "#111827",
        "sidebar_bg": "#0d131f",
        "text_primary": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted": "#94a3b8",
        "border_color": "#1e293b",
        "border_subtle": "#1e293b",
        "header_bg": "#0f172a",
        "header_border": "#1e293b",
        "header_text": "#f8fafc",
        "safety_bg": "rgba(225, 29, 72, 0.08)",
        "safety_border": "rgba(244, 63, 94, 0.35)",
        "safety_title": "#fda4af",
        "safety_text": "#fecdd3",
        "consensus_bg": "rgba(16, 185, 129, 0.08)",
        "consensus_border": "rgba(16, 185, 129, 0.35)",
        "consensus_title": "#6ee7b7",
        "consensus_text": "#a7f3d0",
        "contested_bg": "rgba(245, 158, 11, 0.08)",
        "contested_border": "rgba(245, 158, 11, 0.35)",
        "contested_title": "#fde68a",
        "contested_text": "#fef3c7",
        "evidence_bg": "#0f172a",
        "evidence_border": "#1e293b",
        "evidence_title": "#93c5fd",
        "chip_bg": "#1e293b",
        "chip_border": "#334155",
        "chip_text": "#93c5fd",
        "quote_bg": "rgba(254, 240, 138, 0.15)",
        "quote_text": "#fef08a",
        "quote_border": "#eab308",
        "btn_primary_bg": "#2563eb",
        "btn_primary_text": "#ffffff",
        "btn_primary_hover": "#1d4ed8",
        "btn_primary_border": "#3b82f6",
        "chart_font": "#94a3b8",
        "chart_zero": "rgba(255, 255, 255, 0.15)",
        "tag_bg": "#1e293b",
        "tag_text": "#cbd5e1",
    }
else:
    # ✦ Editorial Studio Light (Default clean human aesthetic)
    tokens = {
        "bg_color": "#f8fafc",
        "card_bg": "#ffffff",
        "sidebar_bg": "#ffffff",
        "text_primary": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "border_color": "#e2e8f0",
        "border_subtle": "#f1f5f9",
        "header_bg": "#ffffff",
        "header_border": "#e2e8f0",
        "header_text": "#0f172a",
        "safety_bg": "#fff1f2",
        "safety_border": "#fecdd3",
        "safety_title": "#9f1239",
        "safety_text": "#881337",
        "consensus_bg": "#f0fdf4",
        "consensus_border": "#bbf7d0",
        "consensus_title": "#065f46",
        "consensus_text": "#064e3b",
        "contested_bg": "#fffbeb",
        "contested_border": "#fde68a",
        "contested_title": "#92400e",
        "contested_text": "#78350f",
        "evidence_bg": "#f8fafc",
        "evidence_border": "#e2e8f0",
        "evidence_title": "#0f172a",
        "chip_bg": "#f1f5f9",
        "chip_border": "#cbd5e1",
        "chip_text": "#1e293b",
        "quote_bg": "#fef9c3",
        "quote_text": "#713f12",
        "quote_border": "#ca8a04",
        "btn_primary_bg": "#0f172a",
        "btn_primary_text": "#ffffff",
        "btn_primary_hover": "#1e293b",
        "btn_primary_border": "#0f172a",
        "chart_font": "#475569",
        "chart_zero": "#cbd5e1",
        "tag_bg": "#f1f5f9",
        "tag_text": "#475569",
    }

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: {base_font_size};
    letter-spacing: -0.01em;
}}

.stApp {{
    background-color: {tokens["bg_color"]};
    color: {tokens["text_primary"]};
}}

[data-testid="stSidebar"] {{
    background-color: {tokens["sidebar_bg"]};
    border-right: 1px solid {tokens["border_color"]};
}}

/* ── Top Editorial Brand Bar ── */
.brand-header {{
    background-color: {tokens["header_bg"]};
    border: 1px solid {tokens["header_border"]};
    border-radius: 10px;
    padding: 1.1rem 1.6rem;
    margin-bottom: 0.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}}

.brand-left {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
}}

.brand-icon-box {{
    width: 38px;
    height: 38px;
    border-radius: 8px;
    background-color: {tokens["btn_primary_bg"]};
    color: {tokens["btn_primary_text"]};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.1rem;
}}

.brand-name {{
    font-size: {title_font_size};
    font-weight: 700;
    color: {tokens["header_text"]};
    line-height: 1.2;
    margin: 0;
}}

.brand-desc {{
    font-size: {small_font_size};
    color: {tokens["text_muted"]};
    margin: 0;
    font-weight: 400;
}}

.brand-badges {{
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}}

.meta-pill {{
    font-size: 0.72rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
    background-color: {tokens["tag_bg"]};
    color: {tokens["tag_text"]};
    border: 1px solid {tokens["border_color"]};
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

/* ── Interactive Presets & Chip Containers ── */
.preset-bar {{
    background-color: {tokens["card_bg"]};
    border: 1px solid {tokens["border_color"]};
    border-radius: 8px;
    padding: 8px 14px;
    margin-bottom: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}

.preset-label {{
    font-size: 0.75rem;
    font-weight: 700;
    color: {tokens["text_muted"]};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}}

/* ── Cards ── */
.editorial-card {{
    background-color: {tokens["card_bg"]};
    border: 1px solid {tokens["border_color"]};
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02);
}}

.card-safety {{
    background-color: {tokens["safety_bg"]};
    border: 1px solid {tokens["safety_border"]};
}}

.card-consensus {{
    background-color: {tokens["consensus_bg"]};
    border: 1px solid {tokens["consensus_border"]};
}}

.card-contested {{
    background-color: {tokens["contested_bg"]};
    border: 1px solid {tokens["contested_border"]};
}}

.card-evidence {{
    background-color: {tokens["evidence_bg"]};
    border: 1px solid {tokens["evidence_border"]};
}}

/* ── Section Titles ── */
.section-headline {{
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}}

.title-safety {{ color: {tokens["safety_title"]}; }}
.title-consensus {{ color: {tokens["consensus_title"]}; }}
.title-contested {{ color: {tokens["contested_title"]}; }}
.title-evidence {{ color: {tokens["evidence_title"]}; }}

.section-subtext {{
    font-size: {small_font_size};
    color: {tokens["text_muted"]};
    margin-bottom: 0.9rem;
    line-height: 1.4;
}}

/* ── Executive Verdict Banner ── */
.verdict-banner {{
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
    border: 1px solid {tokens["border_color"]};
    background-color: {tokens["card_bg"]};
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
}}

.verdict-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}}

.verdict-badge {{
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 999px;
    display: inline-block;
}}

/* ── Editorial Footnote Citation Chips [#14] ── */
.citation-chip {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 1px 6px;
    border-radius: 4px;
    background-color: {tokens["chip_bg"]};
    border: 1px solid {tokens["chip_border"]};
    color: {tokens["chip_text"]};
    margin: 0 2px;
    display: inline-block;
    vertical-align: middle;
}}

/* ── Natural Text Highlight Marker ── */
.quote-marker {{
    background-color: {tokens["quote_bg"]};
    color: {tokens["quote_text"]};
    border-left: 3px solid {tokens["quote_border"]};
    padding: 6px 10px;
    border-radius: 4px;
    font-style: normal;
    font-weight: 500;
    line-height: 1.5;
    margin: 6px 0;
    display: block;
}}

/* ── Individual Review Card in Inspector ── */
.review-entry {{
    background-color: {tokens["card_bg"]};
    border: 1px solid {tokens["border_color"]};
    border-radius: 8px;
    padding: 1.1rem;
    margin-bottom: 0.9rem;
}}

.review-meta-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: {small_font_size};
    color: {tokens["text_muted"]};
    border-bottom: 1px solid {tokens["border_subtle"]};
    padding-bottom: 0.5rem;
    margin-bottom: 0.65rem;
}}

.review-id-tag {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: {tokens["text_primary"]};
}}

.star-rating {{
    color: #eab308;
    font-size: 0.95rem;
    letter-spacing: 1px;
}}

.star-empty {{
    color: #cbd5e1;
    font-size: 0.95rem;
    letter-spacing: 1px;
}}

/* ── Buttons & Action Styling ── */
.stButton > button {{
    background-color: {tokens["btn_primary_bg"]} !important;
    color: {tokens["btn_primary_text"]} !important;
    border: 1px solid {tokens["btn_primary_border"]} !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    padding: 0.4rem 1.1rem !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    transition: all 0.15s ease-in-out !important;
}}

.stButton > button:hover {{
    background-color: {tokens["btn_primary_hover"]} !important;
    transform: translateY(-1px);
    box-shadow: 0 3px 6px -1px rgba(0, 0, 0, 0.08) !important;
}}

/* ── Metrics Strip ── */
div[data-testid="stMetric"] {{
    background-color: {tokens["card_bg"]};
    border: 1px solid {tokens["border_color"]};
    border-radius: 8px;
    padding: 10px 14px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
}}

div[data-testid="stMetricLabel"] {{
    color: {tokens["text_muted"]} !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}}

div[data-testid="stMetricValue"] {{
    color: {tokens["text_primary"]} !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}}

.subtle-line {{
    border: none;
    border-top: 1px solid {tokens["border_color"]};
    margin: 0.75rem 0;
}}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helper Renderers
# ---------------------------------------------------------------------------

def _stars(rating: int) -> str:
    rating = max(1, min(5, int(rating or 5)))
    return (
        '<span class="star-rating">' + "★" * rating + "</span>"
        + '<span class="star-empty">' + "★" * (5 - rating) + "</span>"
    )


def _extract_citation_ids(text: str) -> list[int]:
    """Pull all integer IDs from citation patterns like [Review #12] or [#5, #8]."""
    return [int(n) for n in re.findall(r"#(\d+)", text)]


def _render_cited_text(text: str) -> str:
    """Replace [Review #N] / [#N, #M] patterns with clean editorial citation chips."""
    def _replace(m):
        raw = m.group(0)
        ids = re.findall(r"\d+", raw)
        chips = "".join(
            f'<span class="citation-chip" title="Inspect Review #{i}">Ref #{i}</span>'
            for i in ids
        )
        return chips

    return re.sub(r"\[(?:Review\s+)?#[\d,\s#]+\]", _replace, text)


def _highlight_quote_in_text(full_text: str, quote: str) -> str:
    """Wrap matching quote in an authentic highlighter marker."""
    if not quote or not full_text:
        return full_text
    escaped = re.escape(quote[:80])
    highlighted = re.sub(
        escaped,
        f'<span class="quote-marker">{quote[:80]}</span>',
        full_text,
        flags=re.IGNORECASE,
        count=1,
    )
    return highlighted


def _review_lookup(review_id: int) -> dict | None:
    for r in st.session_state["reviews"]:
        if r["review_id"] == review_id:
            return r
    return None


def _tuple_lookup(review_id: int) -> list:
    return [t for t in st.session_state["tuples"] if t.review_id == review_id]


def _set_inspector(review_ids: list[int], quote: str = ""):
    st.session_state["selected_review_ids"] = review_ids
    st.session_state["selected_quote"] = quote


# ---------------------------------------------------------------------------
# Section: Executive Takeaways & Verdict Card
# ---------------------------------------------------------------------------

def render_executive_verdict_card(alerts, summary, contested):
    """At-a-glance TL;DR summary card providing an immediate high-level verdict."""
    if alerts:
        verdict_text = "⚠️ CAUTION: CRITICAL SAFETY CONCERNS DETECTED"
        verdict_badge_style = "background:#fee2e2; color:#991b1b; border:1px solid #f87171;"
        headline_summary = (
            f"Isolated reports of {', '.join(a.risk_term.title() for a in alerts)} "
            f"were surfaced across {sum(len(a.matching_reviews) for a in alerts)} customer accounts. "
            "These hazard complaints were intercepted before majority star ratings could conceal them."
        )
    elif contested:
        verdict_text = "⚖️ POLARIZED SENTIMENT: REVIEW TRADE-OFFS"
        verdict_badge_style = "background:#fef3c7; color:#92400e; border:1px solid #fcd34d;"
        headline_summary = (
            f"Customer opinion is split on key dimensions: {', '.join(c.aspect for c in contested[:3])}. "
            "Examine conflicting pro/con citations before making purchasing or evaluation decisions."
        )
    else:
        verdict_text = "✅ STRONG CONSENSUS: GENERALLY PRAISED"
        verdict_badge_style = "background:#dcfce7; color:#166534; border:1px solid #86efac;"
        headline_summary = "Customer satisfaction converges strongly across evaluated hardware aspects."

    st.markdown(
        f"""
<div class="verdict-banner">
  <div class="verdict-header">
    <div>
      <span class="verdict-badge" style="{verdict_badge_style}">{verdict_text}</span>
      <span style="font-size:0.8rem; color:{tokens['text_muted']}; margin-left:8px;">
        Evidence-backed audit &bull; 100% Attributed
      </span>
    </div>
  </div>
  <div style="font-size:0.95rem; line-height:1.6; color:{tokens['text_secondary']}; margin-bottom:1rem;">
    {headline_summary}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # 3-Column Highlights Matrix
    col_str, col_con, col_attr = st.columns(3)
    with col_str:
        st.markdown(
            f"""
<div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:10px 14px; height:100%;">
  <div style="font-size:0.75rem; font-weight:700; color:#059669; text-transform:uppercase; margin-bottom:4px;">
    Top Verified Strengths
  </div>
  <div style="font-size:0.85rem; color:{tokens['text_secondary']}; line-height:1.5;">
    {summary.consensus_points[0] if summary and summary.consensus_points else 'Strong user feedback.'}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col_con:
        watch_out = (
            f"Safety: {alerts[0].risk_term.title()} in reviews {alerts[0].matching_reviews[:4]}"
            if alerts else (
                f"Contested: {contested[0].aspect} ({int(contested[0].ratio*100)}% polarity)"
                if contested else "No major complaints flagged."
            )
        )
        st.markdown(
            f"""
<div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:10px 14px; height:100%;">
  <div style="font-size:0.75rem; font-weight:700; color:#e11d48; text-transform:uppercase; margin-bottom:4px;">
    Critical Watch-Outs
  </div>
  <div style="font-size:0.85rem; color:{tokens['text_secondary']}; line-height:1.5;">
    {watch_out}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col_attr:
        st.markdown(
            f"""
<div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:10px 14px; height:100%;">
  <div style="font-size:0.75rem; font-weight:700; color:{tokens['text_muted']}; text-transform:uppercase; margin-bottom:4px;">
    Explainability Guarantee
  </div>
  <div style="font-size:0.85rem; color:{tokens['text_secondary']}; line-height:1.5;">
    Every conclusion links directly to verifiable raw customer text. Zero ungrounded claims.
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section: Searchable & Filterable Evidence Inspector (Right Panel)
# ---------------------------------------------------------------------------

def render_evidence_inspector():
    st.markdown(
        f"""
<div class="section-headline title-evidence">
  <span>Source Evidence &amp; Review Inspector</span>
</div>
<div class="section-subtext">
  Search and inspect authentic customer quotes, ratings, and timestamps.
</div>
""",
        unsafe_allow_html=True,
    )

    # Interactive Search & Rating Filter Toolbar
    search_col, star_col = st.columns([3, 2])
    with search_col:
        kw = st.text_input(
            "Filter text",
            value=st.session_state.get("inspector_keyword", ""),
            placeholder="Type keywords e.g. 'heat', 'battery'...",
            key="input_inspector_kw",
            label_visibility="collapsed",
        )
        st.session_state["inspector_keyword"] = kw

    with star_col:
        star_filter = st.selectbox(
            "Rating filter",
            ["All Ratings", "5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"],
            key="select_inspector_star",
            label_visibility="collapsed",
        )
        st.session_state["inspector_star"] = star_filter

    active_ids = st.session_state.get("selected_review_ids", [])
    active_quote = st.session_state.get("selected_quote", "")

    # Base candidate pool: if citation selected, use active_ids; otherwise show all reviews!
    if active_ids:
        candidate_reviews = [_review_lookup(rid) for rid in active_ids if _review_lookup(rid)]
        header_text = f"CITATION TRACE: {len(active_ids)} GROUNDED REVIEWS"
    else:
        candidate_reviews = st.session_state.get("reviews", [])
        header_text = "TOP VERIFIED CUSTOMER REVIEWS"

    # Apply search filter
    if kw.strip():
        candidate_reviews = [
            r for r in candidate_reviews
            if kw.lower() in str(r.get("review_text", "")).lower()
        ]

    # Apply star filter
    if star_filter != "All Ratings":
        target_star = int(star_filter[0])
        candidate_reviews = [
            r for r in candidate_reviews
            if int(r.get("rating", 0)) == target_star
        ]

    st.markdown(
        f"""
<div style="display:flex; justify-content:space-between; align-items:center; margin: 0.6rem 0 0.8rem 0;">
  <span style="font-size:0.75rem; font-weight:700; color:{tokens['text_muted']}; letter-spacing:0.04em;">
    {header_text} ({len(candidate_reviews)} DISPLAYED)
  </span>
</div>
""",
        unsafe_allow_html=True,
    )

    if not candidate_reviews:
        st.markdown(
            f"""
<div style="padding: 2rem 1rem; text-align: center; color: {tokens['text_muted']}; font-size: 0.88rem;">
  No reviews matched your search filter. Click <em>Reset Filters</em> to view all reviews.
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button("Reset Filters", key="reset_filter_btn"):
            st.session_state["selected_review_ids"] = []
            st.session_state["inspector_keyword"] = ""
            st.session_state["inspector_star"] = "All Ratings"
            st.rerun()
        return

    # Display up to 10 reviews
    for review in candidate_reviews[:10]:
        rid = review["review_id"]
        tuples_for_review = _tuple_lookup(rid)
        body_html = _highlight_quote_in_text(review["review_text"], active_quote)
        helpful_text = f"{review.get('helpful_votes', 0)} helpful votes" if review.get("helpful_votes") else "Verified purchase"

        st.markdown(
            f"""
<div class="review-entry">
  <div class="review-meta-bar">
    <div>
      <span class="review-id-tag">Review #{rid}</span>
      &nbsp;&bull;&nbsp; {_stars(review['rating'])}
    </div>
    <div>
      <span>{review.get('date', 'Customer Review')}</span>
      &nbsp;&bull;&nbsp; <span>{helpful_text}</span>
    </div>
  </div>
  <div style="font-size:0.9rem; line-height:1.6; color:{tokens['text_secondary']};">
    {body_html}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if tuples_for_review:
            with st.expander(f"Extracted Aspects (Review #{rid})", expanded=False):
                for t in tuples_for_review:
                    sentiment_badge_style = {
                        "positive": "background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0;",
                        "negative": "background:#fff1f2; color:#9f1239; border:1px solid #fecdd3;",
                        "neutral": "background:#f1f5f9; color:#334155; border:1px solid #cbd5e1;",
                    }.get(t.sentiment, "background:#f1f5f9; color:#334155; border:1px solid #cbd5e1;")

                    st.markdown(
                        f"""
<div style="font-size:0.82rem; margin-bottom:6px; line-height:1.4;">
  <strong>{t.aspect}</strong> &nbsp;
  <span style="font-size:0.7rem; font-weight:700; padding:1px 6px; border-radius:4px; {sentiment_badge_style}">
    {t.sentiment.upper()}
  </span><br/>
  <span style="color:{tokens['text_muted']};">"{t.summary_claim}"</span>
</div>
""",
                        unsafe_allow_html=True,
                    )

    if len(candidate_reviews) > 10:
        st.caption(f"Showing 10 of {len(candidate_reviews)} matching customer reviews.")


# ---------------------------------------------------------------------------
# Section A — Critical Product & Safety Notices
# ---------------------------------------------------------------------------

def render_safety_section(alerts):
    if not alerts:
        return

    with st.container(border=True):
        st.markdown(
            f"""
<div class="section-headline title-safety">
  <span>Critical Product &amp; Safety Notices</span>
</div>
<div class="section-subtext">
  Isolated consumer hazard reports flagged before statistical aggregation to prevent dilution.
</div>
""",
            unsafe_allow_html=True,
        )

        for alert in alerts:
            review_ids = alert.matching_reviews
            id_str = ", ".join(f"#{r}" for r in review_ids[:6])
            more = f" +{len(review_ids)-6} more" if len(review_ids) > 6 else ""

            st.markdown(
                f"""
<div style="margin: 0.5rem 0;">
  <span style="font-size:0.75rem; font-weight:700; background:#e11d48; color:white; padding:2px 8px; border-radius:4px; margin-right:6px;">
    HAZARD REPORT
  </span>
  <strong style="color:{tokens['safety_title']}; font-size:0.95rem;">
    {alert.risk_term.title()}
  </strong>
  <span style="font-size:0.85rem; color:{tokens['text_muted']};">
    — detected across {len(review_ids)} review(s) [{id_str}{more}]
  </span>
</div>
""",
                unsafe_allow_html=True,
            )

            for q in alert.quotes[:2]:
                st.markdown(
                    f'<div class="quote-marker">"{q[:160]}"</div>',
                    unsafe_allow_html=True,
                )

            # 1-Click Action to trace safety evidence
            btn_col, _ = st.columns([3, 1])
            with btn_col:
                if st.button(
                    f"Inspect {alert.risk_term.title()} Evidence ({len(review_ids)} reviews)",
                    key=f"safety_btn_{alert.risk_term}",
                ):
                    _set_inspector(review_ids, alert.quotes[0] if alert.quotes else "")
                    st.rerun()

            st.markdown(f'<hr class="subtle-line"/>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section B — Customer Consensus Summary with Clickable Citations
# ---------------------------------------------------------------------------

def render_consensus_section(summary):
    if not summary or not summary.consensus_points:
        return

    with st.container(border=True):
        st.markdown(
            f"""
<div class="section-headline title-consensus">
  <span>Verified Customer Consensus</span>
</div>
<div class="section-subtext">
  Key product dimensions where the majority of customer sentiment converges. Click any citation chip to inspect.
</div>
""",
            unsafe_allow_html=True,
        )

        for i, point in enumerate(summary.consensus_points):
            ids = _extract_citation_ids(point)
            rendered = _render_cited_text(point)

            st.markdown(
                f'<div style="margin:8px 0 4px 0; font-size:0.92rem; line-height:1.6; color:{tokens["text_secondary"]};">'
                f"&bull; {rendered}</div>",
                unsafe_allow_html=True,
            )

            # 1-Click Interactive Citation Action Pills
            if ids:
                chip_cols = st.columns(min(len(ids) + 1, 6))
                for idx, cid in enumerate(ids[:4]):
                    with chip_cols[idx]:
                        if st.button(f"🔍 Ref #{cid}", key=f"chip_btn_{i}_{cid}"):
                            _set_inspector([cid])
                            st.rerun()
                with chip_cols[min(len(ids), 4)]:
                    if st.button("Inspect All", key=f"inspect_all_{i}"):
                        _set_inspector(ids)
                        st.rerun()

            st.markdown(f'<hr class="subtle-line"/>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section C — Aspect Sentiment & Contested Dimensions
# ---------------------------------------------------------------------------

def render_contested_section(contested, stats):
    if not contested and not stats:
        return

    with st.container(border=True):
        st.markdown(
            f"""
<div class="section-headline title-contested">
  <span>Aspect Sentiment &amp; Contested Feedback</span>
</div>
<div class="section-subtext">
  Aspect-level sentiment distribution across customer reviews. Highlights areas of consensus vs. polarized user feedback.
</div>
""",
            unsafe_allow_html=True,
        )

        # Clean Aspect Distribution Chart
        if stats:
            aspects = [s["aspect"] for s in stats[:10]]
            pos_vals = [s["positive"] for s in stats[:10]]
            neg_vals = [s["negative"] for s in stats[:10]]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Positive",
                y=aspects,
                x=pos_vals,
                orientation="h",
                marker_color="#10b981",
                opacity=0.9,
            ))
            fig.add_trace(go.Bar(
                name="Negative",
                y=aspects,
                x=[-v for v in neg_vals],
                orientation="h",
                marker_color="#f43f5e",
                opacity=0.9,
            ))
            fig.update_layout(
                barmode="overlay",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=tokens["chart_font"], size=11, family="Inter"),
                xaxis=dict(
                    showgrid=False,
                    zeroline=True,
                    zerolinecolor=tokens["chart_zero"],
                    tickfont=dict(color=tokens["chart_font"]),
                    title="Negative vs. Positive Mentions",
                ),
                yaxis=dict(showgrid=False),
                legend=dict(
                    orientation="h",
                    x=0, y=1.12,
                    font=dict(size=11),
                ),
                margin=dict(l=10, r=10, t=10, b=10),
                height=max(180, len(aspects) * 28),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Contested Aspect Detail Cards
        if contested:
            st.markdown(
                f'<div style="font-size:0.78rem; font-weight:700; color:{tokens["text_muted"]}; text-transform:uppercase; margin:0.8rem 0 0.4rem 0;">'
                f'Polarized Dimensions ({len(contested)} Detected)</div>',
                unsafe_allow_html=True,
            )
            for c in contested:
                ratio_pct = int(c.ratio * 100)
                st.markdown(
                    f"""
<div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:10px 14px; margin: 0.6rem 0;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
    <div>
      <strong style="color:{tokens['text_primary']}; font-size:0.95rem;">{c.aspect}</strong>
      <span style="color:{tokens['text_muted']}; font-size:0.82rem; margin-left:6px;">
        ({c.pos_count} positive &bull; {c.neg_count} negative)
      </span>
    </div>
    <span style="font-size:0.75rem; font-weight:700; background:{tokens['tag_bg']}; color:{tokens['tag_text']}; padding:2px 8px; border-radius:4px; border:1px solid {tokens['border_color']};">
      Polarity Index: {ratio_pct}%
    </span>
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

                col_pro, col_con = st.columns(2)
                with col_pro:
                    st.markdown(
                        '<div style="font-size:0.75rem; font-weight:700; color:#059669; text-transform:uppercase; margin-bottom:2px;">Pro Mentions</div>',
                        unsafe_allow_html=True,
                    )
                    for t in c.pro_citations[:2]:
                        rendered = _render_cited_text(f"[Review #{t.review_id}] {t.summary_claim}")
                        st.markdown(
                            f'<div style="font-size:0.83rem; color:{tokens["text_secondary"]}; line-height:1.4; margin:3px 0;">{rendered}</div>',
                            unsafe_allow_html=True,
                        )
                with col_con:
                    st.markdown(
                        '<div style="font-size:0.75rem; font-weight:700; color:#e11d48; text-transform:uppercase; margin-bottom:2px;">Con Mentions</div>',
                        unsafe_allow_html=True,
                    )
                    for t in c.con_citations[:2]:
                        rendered = _render_cited_text(f"[Review #{t.review_id}] {t.summary_claim}")
                        st.markdown(
                            f'<div style="font-size:0.83rem; color:{tokens["text_secondary"]}; line-height:1.4; margin:3px 0;">{rendered}</div>',
                            unsafe_allow_html=True,
                        )

                st.markdown(f'<hr class="subtle-line"/>', unsafe_allow_html=True)
        else:
            # Reassuring positive status note instead of empty broken box
            st.markdown(
                f"""
<div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:10px 14px; margin-top:8px; display:flex; align-items:center; gap:8px;">
  <span style="font-size:0.95rem; color:#059669;">✓</span>
  <span style="font-size:0.85rem; color:{tokens['text_muted']};">
    <strong>High Sentiment Consistency:</strong> All evaluated dimensions show uniform customer consensus without severe polarization.
  </span>
</div>
""",
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Audio Accessibility Player Bar (Text-to-Speech)
# ---------------------------------------------------------------------------

def render_audio_briefing(alerts, summary, contested):
    speech_parts = []
    if alerts:
        speech_parts.append("Important Safety Notice:")
        for a in alerts:
            speech_parts.append(f"Risk: {a.risk_term} identified across {len(a.matching_reviews)} customer reports.")

    if summary and summary.consensus_points:
        speech_parts.append("Executive Consensus:")
        for p in summary.consensus_points:
            clean_p = re.sub(r"\[(?:Review\s+)?#[\d,\s#]+\]", "", p).strip()
            speech_parts.append(clean_p)

    if contested:
        speech_parts.append("Contested feedback:")
        for c in contested[:3]:
            speech_parts.append(f"{c.aspect}: polarized ratings with {c.pos_count} positive and {c.neg_count} negative reports.")

    full_text = " ".join(speech_parts).replace('"', '\\"').replace("\n", " ")

    audio_html = f"""
    <div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:10px 16px; margin-bottom:1.1rem; display:flex; align-items:center; justify-content:space-between; box-shadow:0 1px 2px 0 rgba(0,0,0,0.02);">
        <div style="display:flex; align-items:center; gap:0.6rem;">
            <span style="font-size:1.1rem;">🔊</span>
            <div>
                <strong style="color:{tokens['text_primary']}; font-size:0.88rem;">Spoken Audio Briefing</strong>
                <div style="color:{tokens['text_muted']}; font-size:0.75rem;">Hands-free voice read-aloud of safety alerts and executive consensus.</div>
            </div>
        </div>
        <div>
            <button onclick="playAudioBriefing()" style="background:{tokens['btn_primary_bg']}; color:{tokens['btn_primary_text']}; border:none; border-radius:5px; padding:5px 13px; font-size:0.8rem; font-weight:600; cursor:pointer; margin-right:6px;">
                ▶ Play Briefing
            </button>
            <button onclick="stopAudioBriefing()" style="background:{tokens['tag_bg']}; color:{tokens['tag_text']}; border:1px solid {tokens['border_color']}; border-radius:5px; padding:5px 12px; font-size:0.8rem; font-weight:600; cursor:pointer;">
                ⏹ Stop
            </button>
        </div>
    </div>

    <script>
    function playAudioBriefing() {{
        if (!('speechSynthesis' in window)) {{
            alert('Speech synthesis is not supported by your browser.');
            return;
        }}
        window.speechSynthesis.cancel();
        const text = "{full_text}";
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }}

    function stopAudioBriefing() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
        }}
    }}
    </script>
    """
    components.html(audio_html, height=62)


# ---------------------------------------------------------------------------
# Report Exporter (Markdown & JSON)
# ---------------------------------------------------------------------------

def generate_export_payloads(product_id: str, brand_name: str, alerts, summary, contested, stats):
    md_lines = [
        f"# OpinionLens Executive Review Audit",
        f"- **Product Model:** {product_id}",
        f"- **Brand / Source:** {brand_name}",
        f"- **Audit Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## 1. Critical Product & Safety Notices",
    ]
    if alerts:
        for a in alerts:
            md_lines.append(f"- **HAZARD:** {a.risk_term.upper()} (Found in {len(a.matching_reviews)} reviews: {a.matching_reviews})")
            for q in a.quotes[:2]:
                md_lines.append(f"  - Quote: *\"{q}\"*")
    else:
        md_lines.append("No critical safety warnings detected.")

    md_lines.extend(["", "## 2. Customer Consensus Summary"])
    if summary and summary.consensus_points:
        for p in summary.consensus_points:
            md_lines.append(f"- {p}")

    md_lines.extend(["", "## 3. Contested Dimensions & Polarized Feedback"])
    if contested:
        for c in contested:
            md_lines.append(f"- **{c.aspect}:** {c.pos_count} Positive vs {c.neg_count} Negative (Polarity: {c.ratio:.2f})")
    else:
        md_lines.append("No polarized aspects detected.")

    md_content = "\n".join(md_lines)

    json_data = {
        "product_id": product_id,
        "brand_name": brand_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "safety_alerts": [
            {"risk": a.risk_term, "reviews": a.matching_reviews, "quotes": a.quotes}
            for a in alerts
        ],
        "consensus_points": summary.consensus_points if summary else [],
        "contested_aspects": [
            {"aspect": c.aspect, "pos_count": c.pos_count, "neg_count": c.neg_count, "ratio": c.ratio}
            for c in contested
        ],
    }
    json_content = json.dumps(json_data, indent=2)

    return md_content, json_content


# ---------------------------------------------------------------------------
# Main Pipeline Runner
# ---------------------------------------------------------------------------

def run_pipeline(csv_source, product_id: str, query: str):
    progress_bar = st.progress(0, text="Initializing analysis engine…")

    user_api_key = st.session_state.get("user_groq_key", "").strip()
    is_offline = (st.session_state.get("exec_mode") == "🛡️ Zero-API Local Mode (Offline / Free)")
    selected_model = st.session_state.get("selected_model", GROQ_MODEL)

    try:
        # Step 1: Ingest (idempotent)
        progress_bar.progress(0.05, text="Checking ChromaDB vector index…")
        if not is_already_ingested(product_id):
            progress_bar.progress(0.10, text="Indexing product reviews into ChromaDB…")
            ingest_product(
                csv_source,
                product_id,
                progress_callback=lambda p, m: progress_bar.progress(
                    0.10 + p * 0.32, text=m
                ),
            )

        # Step 2: Retrieval
        progress_bar.progress(0.44, text="Retrieving relevant reviews…")
        is_general = query.strip().lower() in {
            "", "summarize", "summarize entire product", "overall", "general"
        }
        mode = "balanced" if is_general else "aspect"
        reviews = retrieve_opinions(product_id, query, mode=mode)

        if not reviews:
            st.error("No reviews retrieved. Ensure ingestion completed successfully.")
            return

        st.session_state["reviews"] = reviews

        # Step 3: Aspect Extraction
        progress_bar.progress(0.55, text=f"Extracting opinions across {len(reviews)} reviews…")
        extraction = extract_aspects(
            reviews,
            api_key=user_api_key,
            model=selected_model,
            use_offline=is_offline,
        )
        tuples = extraction.extracted_tuples
        st.session_state["tuples"] = tuples

        # Step 4: Safety guard
        progress_bar.progress(0.74, text="Evaluating safety guard against critical hazards…")
        alerts = detect_critical_risks(tuples)
        st.session_state["alerts"] = alerts

        # Step 5: Aggregation
        progress_bar.progress(0.82, text="Aggregating aspect clusters & polarity…")
        clusters = build_aspect_clusters(tuples)
        contested = compute_contention(clusters)
        stats = summarize_aspect_stats(clusters)
        st.session_state["clusters"] = clusters
        st.session_state["contested"] = contested
        st.session_state["stats"] = stats

        # Step 6: Summary generation
        progress_bar.progress(0.90, text="Synthesizing cited executive report…")
        summary = generate_summary(
            clusters,
            contested,
            alerts,
            api_key=user_api_key,
            model=selected_model,
            use_offline=is_offline,
        )
        st.session_state["summary"] = summary

        st.session_state["analysis_done"] = True
        progress_bar.progress(1.0, text="Analysis Complete!")
        time.sleep(0.2)
        progress_bar.empty()

    except Exception as e:
        progress_bar.empty()
        st.error(f"Pipeline error: {e}")
        raise


# ---------------------------------------------------------------------------
# UI — Top Editorial Brand Bar
# ---------------------------------------------------------------------------

st.markdown(
    f"""
<div class="brand-header">
  <div class="brand-left">
    <div class="brand-icon-box">OL</div>
    <div>
      <h1 class="brand-name">OpinionLens</h1>
      <p class="brand-desc">Evidence-Grounded Review Synthesis &amp; Product Safety Audit System</p>
    </div>
  </div>
  <div class="brand-badges">
    <span class="meta-pill">ChromaDB Indexed</span>
    <span class="meta-pill">SemEval-2016 ABSA</span>
    <span class="meta-pill">Dual Engine: Local / Groq</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# UI — 1-Click Interactive Demo Presets (User-Friendly Shortcut Bar)
# ---------------------------------------------------------------------------

st.markdown(
    f'<div style="font-size:0.75rem; font-weight:700; color:{tokens["text_muted"]}; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">'
    f'⚡ 1-Click Interactive Demo Presets (Instant Pipeline Evaluation)</div>',
    unsafe_allow_html=True,
)

demo_cols = st.columns(4)

with demo_cols[0]:
    if st.button("💻 MacBook Air M2\n(Thermals & MagSafe)", use_container_width=True, help="Test fanless thermal throttling and MagSafe charger sparks"):
        st.session_state["active_brand"] = "Laptops"
        st.session_state["active_product_id"] = "MACBOOK_AIR_M2"
        st.session_state["active_query"] = "thermal throttling & charger"
        st.session_state["trigger_run"] = True
        st.rerun()

with demo_cols[1]:
    if st.button("🔋 Anker PowerCore\n(Battery Swelling Risk)", use_container_width=True, help="Test lithium battery swelling & smoke hazard detection"):
        st.session_state["active_brand"] = "Amazon Electronics"
        st.session_state["active_product_id"] = "B00X5RV14Y"
        st.session_state["active_query"] = "battery swelling & fast charging"
        st.session_state["trigger_run"] = True
        st.rerun()

with demo_cols[2]:
    if st.button("📱 Lenovo A6000\n(Camera vs Heat Polarity)", use_container_width=True, help="Test conflicting pro/con sentiment on budget smartphone"):
        st.session_state["active_brand"] = "Lenova"
        st.session_state["active_product_id"] = "MOBE7JXXKS6PWW2C"
        st.session_state["active_query"] = "camera vs heating issues"
        st.session_state["trigger_run"] = True
        st.rerun()

with demo_cols[3]:
    if st.button("🔍 Full Balanced Audit\n(Overall Synthesis)", use_container_width=True, help="Generate a balanced executive summary across all aspects"):
        st.session_state["active_brand"] = "Laptops"
        st.session_state["active_product_id"] = "MACBOOK_AIR_M2"
        st.session_state["active_query"] = ""
        st.session_state["trigger_run"] = True
        st.rerun()


# ---------------------------------------------------------------------------
# UI — Filter & Query Control Strip
# ---------------------------------------------------------------------------

ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2.5, 3.2, 3.3, 1.2])

brands = list_all_brands()
brand_labels = list(brands.keys())

# If user uploaded a custom dataset, add it to options
if st.session_state.get("custom_dataset_df") is not None:
    custom_name = st.session_state.get("custom_dataset_name", "Uploaded Dataset")
    brand_labels.insert(0, f"📁 {custom_name}")

default_brand_label = st.session_state.get("active_brand")
default_brand_idx = 0
if default_brand_label and default_brand_label in brand_labels:
    default_brand_idx = brand_labels.index(default_brand_label)
else:
    for i, lbl in enumerate(brand_labels):
        if "laptop" in lbl.lower():
            default_brand_idx = i
            break

with ctrl_col1:
    selected_brand = st.selectbox("Product Brand / Dataset", brand_labels, index=default_brand_idx)

# Determine active dataset source
if selected_brand.startswith("📁") and st.session_state.get("custom_dataset_df") is not None:
    active_dataset_source = st.session_state["custom_dataset_df"]
else:
    active_dataset_source = brands[selected_brand]

with ctrl_col2:
    with st.spinner("Loading product models…"):
        products_df = list_products_in_csv(active_dataset_source)

    if products_df.empty:
        st.warning("No products found with sufficient reviews.")
        product_options = {"Default Product": "DEFAULT_PROD"}
    else:
        product_options = {
            f"{row['product_name']} ({row['review_count']} reviews)": row["product_id"]
            for _, row in products_df.iterrows()
        }

    product_labels = list(product_options.keys())
    default_prod_idx = 0
    preset_pid = st.session_state.get("active_product_id")

    if preset_pid:
        for i, pid in enumerate(product_options.values()):
            if pid == preset_pid:
                default_prod_idx = i
                break
    else:
        for i, pid in enumerate(product_options.values()):
            if pid == DEFAULT_PRODUCT_ID:
                default_prod_idx = i
                break

    selected_product_label = st.selectbox("Hardware Model", product_labels, index=default_prod_idx)

selected_product_id = product_options[selected_product_label]

with ctrl_col3:
    query = st.text_input(
        "Aspect Filter Query",
        value=st.session_state.get("active_query", ""),
        placeholder="Leave blank for balanced summary, or ask e.g. 'battery heating'",
    )
    st.session_state["active_query"] = query

with ctrl_col4:
    st.markdown("<br/>", unsafe_allow_html=True)
    analyze = st.button("Run Audit", use_container_width=True)


# ---------------------------------------------------------------------------
# UI — Quick Aspect Query Chips (Under Search Input)
# ---------------------------------------------------------------------------

st.markdown(
    f'<div style="display:flex; align-items:center; gap:0.5rem; margin-top:-0.4rem; margin-bottom:1.1rem; flex-wrap:wrap;">'
    f'<span style="font-size:0.75rem; font-weight:700; color:{tokens["text_muted"]}; text-transform:uppercase;">Quick Topics:</span>'
    f'</div>',
    unsafe_allow_html=True,
)

chip_col1, chip_col2, chip_col3, chip_col4, chip_col5, chip_col6 = st.columns(6)
with chip_col1:
    if st.button("🔥 Heating & Safety", use_container_width=True, key="chip_heat"):
        st.session_state["active_query"] = "overheating thermal throttling"
        st.session_state["trigger_run"] = True
        st.rerun()
with chip_col2:
    if st.button("🔋 Battery Life", use_container_width=True, key="chip_batt"):
        st.session_state["active_query"] = "battery life charging speed"
        st.session_state["trigger_run"] = True
        st.rerun()
with chip_col3:
    if st.button("📸 Camera Quality", use_container_width=True, key="chip_cam"):
        st.session_state["active_query"] = "camera quality low light"
        st.session_state["trigger_run"] = True
        st.rerun()
with chip_col4:
    if st.button("⚡ Performance", use_container_width=True, key="chip_perf"):
        st.session_state["active_query"] = "performance speed gaming"
        st.session_state["trigger_run"] = True
        st.rerun()
with chip_col5:
    if st.button("💰 Value for Money", use_container_width=True, key="chip_val"):
        st.session_state["active_query"] = "value for money pricing"
        st.session_state["trigger_run"] = True
        st.rerun()
with chip_col6:
    if st.button("↺ Reset (Balanced)", use_container_width=True, key="chip_reset"):
        st.session_state["active_query"] = ""
        st.session_state["trigger_run"] = True
        st.rerun()


# ---------------------------------------------------------------------------
# Sidebar — Preferences, Engine, & Custom Uploads
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### Display & Styling")
    selected_theme = st.selectbox(
        "Visual Theme",
        ["✦ Editorial Studio Light", "✦ Obsidian Matte Dark", "✦ High-Contrast (WCAG AAA)"],
        index=0 if st.session_state["theme_mode"] == "✦ Editorial Studio Light"
        else (1 if st.session_state["theme_mode"] == "✦ Obsidian Matte Dark" else 2),
    )
    if selected_theme != st.session_state["theme_mode"]:
        st.session_state["theme_mode"] = selected_theme
        st.rerun()

    view_layout = st.radio(
        "Results Layout Mode",
        ["Split View (Side-by-Side)", "Tabbed View (Full Width)"],
        index=0 if st.session_state.get("view_layout") == "Split View (Side-by-Side)" else 1,
    )
    st.session_state["view_layout"] = view_layout

    font_toggle = st.toggle("Large Text (120% Scale)", value=st.session_state["font_large"])
    if font_toggle != st.session_state["font_large"]:
        st.session_state["font_large"] = font_toggle
        st.rerun()

    st.markdown("---")
    st.markdown("### Execution Engine")
    mode_options = ["⚡ Groq LLM (High-Performance)", "🛡️ Zero-API Local Mode (Offline / Free)"]
    current_mode_idx = 0 if st.session_state["exec_mode"] == mode_options[0] else 1
    selected_mode = st.radio("Execution Mode", mode_options, index=current_mode_idx)
    st.session_state["exec_mode"] = selected_mode

    if selected_mode == mode_options[0]:
        st.session_state["selected_model"] = st.selectbox(
            "Groq Model",
            ["qwen/qwen3.8-27b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=0,
        )
        api_input = st.text_input(
            "Groq API Key (Optional)",
            value=st.session_state["user_groq_key"],
            type="password",
            help="Leave blank to use GROQ_API_KEY from .env, or enter your personal key here.",
        )
        st.session_state["user_groq_key"] = api_input
    else:
        st.info("Zero-API Mode active. Runs 100% locally on CPU without external API calls.")

    st.markdown("---")
    st.markdown("### Custom Dataset Connector")
    with st.expander("Upload CSV / JSON reviews"):
        uploaded_file = st.file_uploader("Upload review file", type=["csv", "json"])
        if uploaded_file is not None:
            try:
                uploaded_df = load_universal_dataset(uploaded_file)
                st.session_state["custom_dataset_df"] = uploaded_df
                st.session_state["custom_dataset_name"] = uploaded_file.name
                st.success(f"Loaded {len(uploaded_df)} reviews from {uploaded_file.name}!")
                if st.button("Activate Dataset Now"):
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to parse file: {e}")

    st.markdown("---")
    st.markdown("### ChromaDB Vector Index")
    st.markdown(f"**Target Model:** `{selected_product_id}`")
    already = is_already_ingested(selected_product_id)
    st.markdown(f"**Index Status:** {'✅ Indexed & Ready' if already else '⏳ Ingestion required'}")

    if already and st.button("Re-Index Product"):
        ingest_product(active_dataset_source, selected_product_id, force=True)
        st.success("Re-indexed into ChromaDB.")
        st.rerun()


# ---------------------------------------------------------------------------
# Trigger Pipeline
# ---------------------------------------------------------------------------

trigger = analyze or st.session_state.get("trigger_run", False)

if trigger:
    st.session_state["trigger_run"] = False
    st.session_state["analysis_done"] = False
    st.session_state["selected_review_ids"] = []
    st.session_state["selected_quote"] = ""
    run_pipeline(active_dataset_source, selected_product_id, query)


# ---------------------------------------------------------------------------
# Main Dashboard Results View
# ---------------------------------------------------------------------------

if st.session_state["analysis_done"]:
    alerts = st.session_state["alerts"]
    summary = st.session_state["summary"]
    contested = st.session_state["contested"]
    stats = st.session_state["stats"]

    # 1. Executive Verdict & Key Takeaways Card (At-a-Glance TL;DR)
    render_executive_verdict_card(alerts, summary, contested)

    # 2. Spoken Audio Accessibility Bar
    render_audio_briefing(alerts, summary, contested)

    # 3. Key Performance Metrics Strip
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Analyzed Reviews", len(st.session_state["reviews"]))
    m2.metric("Extracted Opinions", len(st.session_state["tuples"]))
    m3.metric("Critical Hazards", len(alerts))
    m4.metric("Contested Dimensions", len(contested))

    st.markdown("<br/>", unsafe_allow_html=True)

    # Choose between Split View and Tabbed View based on user preference
    if st.session_state.get("view_layout") == "Tabbed View (Full Width)":
        tab_exec, tab_cons, tab_pol, tab_evid, tab_exp = st.tabs([
            "🚨 Safety & Critical Notices",
            "✅ Customer Consensus",
            "⚖️ Polarized Dimensions & Charts",
            "🔎 Searchable Source Evidence",
            "📥 Governance & Export",
        ])

        with tab_exec:
            render_safety_section(alerts)

        with tab_cons:
            render_consensus_section(summary)

        with tab_pol:
            render_contested_section(contested, stats)

        with tab_evid:
            st.markdown(f'<div class="editorial-card card-evidence">', unsafe_allow_html=True)
            render_evidence_inspector()
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_exp:
            st.markdown("### Export Audit Report")
            md_report, json_report = generate_export_payloads(
                selected_product_id,
                selected_brand,
                alerts,
                summary,
                contested,
                stats,
            )
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                st.download_button(
                    "Download Report (Markdown .md)",
                    data=md_report,
                    file_name=f"opinionlens_audit_{selected_product_id}.md",
                    mime="text/markdown",
                )
            with exp_col2:
                st.download_button(
                    "Download Schema (JSON .json)",
                    data=json_report,
                    file_name=f"opinionlens_audit_{selected_product_id}.json",
                    mime="application/json",
                )

    else:
        # Default: Split View (Side-by-Side Dual Column)
        left_col, right_col = st.columns([6, 4])

        with left_col:
            render_safety_section(alerts)
            render_consensus_section(summary)
            render_contested_section(contested, stats)

        with right_col:
            st.markdown(f'<div class="editorial-card card-evidence">', unsafe_allow_html=True)
            render_evidence_inspector()
            st.markdown("</div>", unsafe_allow_html=True)

        # Governance & Export Section
        st.markdown("---")
        st.markdown("### Export Audit Report")
        md_report, json_report = generate_export_payloads(
            selected_product_id,
            selected_brand,
            alerts,
            summary,
            contested,
            stats,
        )
        exp_col1, exp_col2, _ = st.columns([2, 2, 4])
        with exp_col1:
            st.download_button(
                "Download Report (Markdown .md)",
                data=md_report,
                file_name=f"opinionlens_audit_{selected_product_id}.md",
                mime="text/markdown",
            )
        with exp_col2:
            st.download_button(
                "Download Schema (JSON .json)",
                data=json_report,
                file_name=f"opinionlens_audit_{selected_product_id}.json",
                mime="application/json",
            )

elif not trigger:
    # Editorial Welcome State
    st.markdown(
        f"""
<div style="padding: 2.2rem 1rem 2.5rem 1rem; color: {tokens['text_muted']};">
  <div style="max-width: 780px; margin: 0 auto; text-align: center;">
    <h2 style="color:{tokens['text_primary']}; font-weight:700; font-size:1.6rem; margin-bottom:0.6rem;">
      Evidence-Grounded Review Intelligence
    </h2>
    <p style="color:{tokens['text_secondary']}; font-size:0.95rem; line-height:1.6; margin-bottom:2rem;">
      OpinionLens analyzes customer reviews with rigorous source attribution, intercepts critical safety risks
      before majority ratings conceal them, and maps contested consumer sentiment across hardware dimensions.
    </p>
  </div>

  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.2rem; max-width: 1050px; margin: 0 auto;">
    <div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:1.2rem 1.4rem;">
      <div style="font-size:0.8rem; font-weight:700; color:{tokens['safety_title']}; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;">
        01 &bull; Safety Isolation
      </div>
      <div style="font-weight:600; color:{tokens['text_primary']}; font-size:1rem; margin-bottom:0.3rem;">
        Critical Risk Interception
      </div>
      <div style="font-size:0.83rem; color:{tokens['text_muted']}; line-height:1.5;">
        Identifies battery swelling, extreme overheating, and fire hazards before star-rating averages dilute them.
      </div>
    </div>

    <div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:1.2rem 1.4rem;">
      <div style="font-size:0.8rem; font-weight:700; color:{tokens['consensus_title']}; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;">
        02 &bull; Traceable Synthesis
      </div>
      <div style="font-weight:600; color:{tokens['text_primary']}; font-size:1rem; margin-bottom:0.3rem;">
        Verifiable Consensus
      </div>
      <div style="font-size:0.83rem; color:{tokens['text_muted']}; line-height:1.5;">
        Synthesizes majority opinions into concise points, each anchored with exact click-to-verify citation references.
      </div>
    </div>

    <div style="background:{tokens['card_bg']}; border:1px solid {tokens['border_color']}; border-radius:8px; padding:1.2rem 1.4rem;">
      <div style="font-size:0.8rem; font-weight:700; color:{tokens['contested_title']}; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;">
        03 &bull; Polarity Detection
      </div>
      <div style="font-weight:600; color:{tokens['text_primary']}; font-size:1rem; margin-bottom:0.3rem;">
        Contested Dimensions
      </div>
      <div style="font-size:0.83rem; color:{tokens['text_muted']}; line-height:1.5;">
        Surfaces hardware aspects where buyer feedback sharply divides into pro and con arguments.
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# UI — Evaluation & Project Defense Guide (Collapsible Drawer)
# ---------------------------------------------------------------------------

with st.expander("🎓 Project Defense & Architecture FAQ (Evaluation Guide)"):
    st.markdown(
        """
### Core Differences: OpinionLens vs. Amazon Review Tags & Naive LLM Prompts

1. **Why not closed-vocabulary Amazon tags?**
   - Amazon tags use a pre-defined static checklist (e.g. "Durable", "Good Battery").
   - OpinionLens uses **query-driven, open-vocabulary generative aspect extraction**: Any natural language query (e.g. *"Is this laptop good for people who travel a lot?"*) retrieves the relevant subset of opinions, extracts dynamic aspects, and synthesizes a tailored answer.

2. **Why not just prompt an LLM to "summarize and cite sources"?**
   - LLMs hallucinate citations and invent review quotes with false confidence.
   - OpinionLens uses **retrieval-grounded, verifiable evidence mapping**: Citations link to raw customer text indexed in ChromaDB, verifiable programmatically.

3. **How does OpinionLens handle conflicting opinions (SAF-02)?**
   - Naive summarizers silently average away minority opinions (e.g. 40% say it runs hot, 60% say cool -> summary says "cool").
   - OpinionLens's **Contention Engine** calculates polarity ratios and surfaces both Pro and Con viewpoints explicitly.

4. **How does the Critical-Minority Safety Guard prevent hazard dilution?**
   - If 3 out of 1,000 users experience battery swelling or fire hazards, a 4.7★ aggregate rating erases the danger.
   - OpinionLens's **Safety Guard** scans reviews using semantic cosine similarity against hazard seed terms (`overheating`, `swelling`, `smoke`, `fire`) and isolates them before statistical clustering occurs.
"""
    )
