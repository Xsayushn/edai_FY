"""
app.py — Human-Crafted Editorial UI for OpinionLens.

An explainable & safety-guarded opinion intelligence dashboard that bridges
raw e-commerce customer reviews with verifiable, citation-backed executive synthesis.

Design System:
  - Inspired by modern engineering dashboards (Linear, Stripe Radar, Perplexity).
  - Clean typography, subtle hairline borders, authentic citations, zero AI tropes.
  - Multi-theme architecture:
      1. ✦ Editorial Studio Light (Default clean white & slate editorial layout)
      2. ✦ Obsidian Matte Dark (Distraction-free executive dark mode)
      3. ✦ High-Contrast (WCAG AAA certified accessibility mode)
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
    page_title="OpinionLens · Product Review Intelligence & Safety Audit",
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
# Session state initialization
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
        "high_contrast": False,
        "font_large": False,
        "user_groq_key": "",
        "exec_mode": "⚡ Groq LLM (High-Performance)",
        "selected_model": "qwen/qwen3.8-27b",
        "custom_dataset_df": None,
        "custom_dataset_name": None,
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
    margin-bottom: 1.2rem;
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
}}

.meta-pill {{
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
    background-color: {tokens["tag_bg"]};
    color: {tokens["tag_text"]};
    border: 1px solid {tokens["border_color"]};
    text-transform: uppercase;
    letter-spacing: 0.04em;
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
    cursor: pointer;
    transition: all 0.12s ease;
}}
.citation-chip:hover {{
    transform: translateY(-1px);
    border-color: {tokens["text_primary"]};
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
    font-size: 0.88rem !important;
    padding: 0.45rem 1.3rem !important;
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

/* ── Minimalist Media Player Bar ── */
.media-briefing-bar {{
    background-color: {tokens["card_bg"]};
    border: 1px solid {tokens["border_color"]};
    border-radius: 8px;
    padding: 9px 15px;
    margin-bottom: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.media-label {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: {tokens["text_primary"]};
    font-size: 0.88rem;
    font-weight: 600;
}}

.media-sublabel {{
    font-size: {small_font_size};
    color: {tokens["text_muted"]};
    font-weight: 400;
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
# Section: Evidence & Source Verifier (Right Panel)
# ---------------------------------------------------------------------------

def render_evidence_inspector():
    st.markdown(
        f"""
<div class="section-headline title-evidence">
  <span>Source Evidence &amp; Citation Verifier</span>
</div>
<div class="section-subtext">
  Inspect verified customer quotes, timestamps, and ratings anchored to summary claims.
</div>
""",
        unsafe_allow_html=True,
    )

    if not st.session_state["selected_review_ids"]:
        st.markdown(
            f"""
<div style="padding: 2.5rem 1rem; text-align: center; color: {tokens['text_muted']}; font-size: 0.88rem;">
  Select any citation chip <span class="citation-chip">Ref #</span> or click <em>Inspect Evidence</em> to trace the exact source reviews here.
</div>
""",
            unsafe_allow_html=True,
        )
        return

    active_ids = st.session_state["selected_review_ids"]
    active_quote = st.session_state.get("selected_quote", "")

    st.markdown(
        f'<div style="font-size:0.8rem; font-weight:600; color:{tokens["text_muted"]}; margin-bottom:0.75rem;">'
        f'DISPLAYING {len(active_ids)} GROUNDED SOURCE CITATION(S)</div>',
        unsafe_allow_html=True,
    )

    for rid in active_ids:
        review = _review_lookup(rid)
        if not review:
            continue

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


# ---------------------------------------------------------------------------
# Section A — Critical Product & Safety Notices
# ---------------------------------------------------------------------------

def render_safety_section(alerts):
    if not alerts:
        return

    st.markdown(
        f"""
<div class="editorial-card card-safety">
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

        if st.button(
            f"Inspect {alert.risk_term.title()} Evidence",
            key=f"safety_btn_{alert.risk_term}",
        ):
            _set_inspector(review_ids, alert.quotes[0] if alert.quotes else "")
            st.rerun()

        st.markdown(f'<hr class="subtle-line"/>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section B — Customer Consensus Summary
# ---------------------------------------------------------------------------

def render_consensus_section(summary):
    st.markdown(
        f"""
<div class="editorial-card card-consensus">
  <div class="section-headline title-consensus">
    <span>Verified Customer Consensus</span>
  </div>
  <div class="section-subtext">
    Key product dimensions where the majority of customer sentiment converges.
  </div>
""",
        unsafe_allow_html=True,
    )

    if not summary or not summary.consensus_points:
        st.markdown(
            f'<p style="color:{tokens["text_muted"]}; font-style:italic;">No consensus generated.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for i, point in enumerate(summary.consensus_points):
        ids = _extract_citation_ids(point)
        rendered = _render_cited_text(point)

        col_text, col_btn = st.columns([5, 1])
        with col_text:
            st.markdown(
                f'<div style="margin:6px 0; font-size:0.92rem; line-height:1.6; color:{tokens["text_secondary"]};">'
                f"&bull; {rendered}</div>",
                unsafe_allow_html=True,
            )
        with col_btn:
            if ids and st.button("Inspect", key=f"consensus_btn_{i}", help="Inspect source reviews"):
                quote = ""
                for rid in ids:
                    ts = _tuple_lookup(rid)
                    if ts:
                        quote = ts[0].quote
                        break
                _set_inspector(ids, quote)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section C — Contested Dimensions & Polarized Feedback
# ---------------------------------------------------------------------------

def render_contested_section(contested, stats):
    st.markdown(
        f"""
<div class="editorial-card card-contested">
  <div class="section-headline title-contested">
    <span>Contested Dimensions &amp; Polarized Feedback</span>
  </div>
  <div class="section-subtext">
    Aspects where customer opinions split into conflicting positive and negative camps.
  </div>
""",
        unsafe_allow_html=True,
    )

    if not contested:
        st.markdown(
            f'<p style="color:{tokens["text_muted"]}; font-style:italic;">No statistically polarized aspects detected for this product.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

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
    for c in contested:
        ratio_pct = int(c.ratio * 100)
        st.markdown(
            f"""
<div style="margin: 0.8rem 0 0.35rem 0; display:flex; justify-content:space-between; align-items:center;">
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

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Audio Accessibility Player Bar (Text-to-Speech)
# ---------------------------------------------------------------------------

def render_audio_briefing(alerts, summary, contested):
    """
    Renders an accessible voice briefing bar using HTML5 SpeechSynthesis.
    """
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
    """Generate Markdown and JSON reports for auditing & governance."""
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
    <span class="meta-pill">SemEval-2016 Benchmark</span>
    <span class="meta-pill">Local / Groq Dual Engine</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


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

default_brand_idx = 0
for i, lbl in enumerate(brand_labels):
    if "lenov" in lbl.lower():
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
    for i, pid in enumerate(product_options.values()):
        if pid == DEFAULT_PRODUCT_ID:
            default_prod_idx = i
            break

    selected_product_label = st.selectbox("Hardware Model", product_labels, index=default_prod_idx)

selected_product_id = product_options[selected_product_label]

with ctrl_col3:
    query = st.text_input(
        "Aspect Filter Query",
        value="",
        placeholder="Leave blank for balanced summary, or ask e.g. 'battery heating'",
    )

with ctrl_col4:
    st.markdown("<br/>", unsafe_allow_html=True)
    analyze = st.button("Run Audit", use_container_width=True)


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

if analyze:
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

    # Spoken Audio Accessibility Bar
    render_audio_briefing(alerts, summary, contested)

    # Key Performance Metrics Strip
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Analyzed Reviews", len(st.session_state["reviews"]))
    m2.metric("Extracted Opinions", len(st.session_state["tuples"]))
    m3.metric("Critical Hazards", len(alerts))
    m4.metric("Contested Dimensions", len(contested))

    st.markdown("<br/>", unsafe_allow_html=True)

    left_col, right_col = st.columns([6, 4])

    with left_col:
        render_safety_section(alerts)
        render_consensus_section(summary)
        render_contested_section(contested, stats)

    with right_col:
        st.markdown(f'<div class="editorial-card card-evidence">', unsafe_allow_html=True)
        render_evidence_inspector()
        st.markdown("</div>", unsafe_allow_html=True)

        all_ids = sorted({r["review_id"] for r in st.session_state["reviews"]})
        if all_ids:
            with st.expander("Jump to specific Review ID"):
                manual_id = st.selectbox("Select Review ID", options=all_ids, key="manual_review_select")
                if st.button("Load Review Record", key="manual_load_btn"):
                    _set_inspector([manual_id])
                    st.rerun()

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

elif not analyze:
    # Editorial Welcome State
    st.markdown(
        f"""
<div style="padding: 2.5rem 1rem 3rem 1rem; color: {tokens['text_muted']};">
  <div style="max-width: 780px; margin: 0 auto; text-align: center;">
    <h2 style="color:{tokens['text_primary']}; font-weight:700; font-size:1.6rem; margin-bottom:0.6rem;">
      Evidence-Grounded Review Intelligence
    </h2>
    <p style="color:{tokens['text_secondary']}; font-size:0.95rem; line-height:1.6; margin-bottom:2.2rem;">
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
