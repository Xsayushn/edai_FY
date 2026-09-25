"""
app.py — Streamlit UI for the Explainable & Safe RAG Opinion Summarizer.

Layout:
  Top bar  : Brand / Dataset selector + Product Model selector + Query bar + Analyze button
  Left 60% : Section A (Safety Warnings) · Section B (Consensus) · Section C (Contested)
  Right 40%: Interactive Evidence Inspector (citation click-through)

Accessibility Features:
  - 🔊 Web Speech API Audio Briefing (reads alerts and executive summary aloud)
  - 👁️ High-Contrast Mode (WCAG AAA compliant)
  - 🔤 Dynamic Text Scaling (Normal / Large)
  - 🛡️ Zero-API Local Mode (Works 100% offline without requiring any API keys)
  - 📥 Export Reports (Markdown and JSON download)
  - 📤 Drag & Drop Custom Dataset Uploader
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
    page_title="OpinionLens · Explainable & Safe Review Summarizer",
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
# Dynamic Styling (Standard vs. High-Contrast & Text Scaling)
# ---------------------------------------------------------------------------

high_contrast = st.session_state["high_contrast"]
font_large = st.session_state["font_large"]

base_font_size = "18px" if font_large else "15px"
small_font_size = "15px" if font_large else "13px"

if high_contrast:
    # WCAG AAA High-Contrast Mode
    bg_gradient = "#000000"
    text_color = "#ffffff"
    card_bg = "#111111"
    border_color = "#ffffff"
    safety_bg = "#450a0a"
    safety_border = "#f87171"
    consensus_bg = "#064e3b"
    consensus_border = "#34d399"
    contested_bg = "#451a03"
    contested_border = "#fbbf24"
    evidence_bg = "#1e1b4b"
    evidence_border = "#818cf8"
    chip_bg = "#312e81"
    chip_border = "#a5b4fc"
    chip_text = "#ffffff"
else:
    # Modern Sleek Dark Gradient Mode
    bg_gradient = "linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%)"
    text_color = "#e2e8f0"
    card_bg = "rgba(255,255,255,0.04)"
    border_color = "rgba(255,255,255,0.08)"
    safety_bg = "rgba(220, 38, 38, 0.15)"
    safety_border = "rgba(239, 68, 68, 0.6)"
    consensus_bg = "rgba(16, 185, 129, 0.10)"
    consensus_border = "rgba(16, 185, 129, 0.4)"
    contested_bg = "rgba(245, 158, 11, 0.10)"
    contested_border = "rgba(245, 158, 11, 0.4)"
    evidence_bg = "rgba(99, 102, 241, 0.10)"
    evidence_border = "rgba(99, 102, 241, 0.35)"
    chip_bg = "rgba(99, 102, 241, 0.3)"
    chip_border = "rgba(99, 102, 241, 0.6)"
    chip_text = "#a5b4fc"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    font-size: {base_font_size};
}}

.stApp {{
    background: {bg_gradient};
    color: {text_color};
}}

/* ── Top branding bar ── */
.brand-bar {{
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}}
.brand-title {{
    font-size: 1.8rem;
    font-weight: 700;
    color: white;
    margin: 0;
}}
.brand-subtitle {{
    font-size: 0.95rem;
    color: rgba(255,255,255,0.9);
    margin: 0;
}}

/* ── Cards ── */
.card {{
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    border: 1px solid {border_color};
}}
.card-safety {{
    background: {safety_bg};
    border: 2px solid {safety_border};
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}}
.card-consensus {{
    background: {consensus_bg};
    border: 2px solid {consensus_border};
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.15);
}}
.card-contested {{
    background: {contested_bg};
    border: 2px solid {contested_border};
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.15);
}}
.card-evidence {{
    background: {evidence_bg};
    border: 2px solid {evidence_border};
}}

/* ── Section headers ── */
.section-header {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
}}
.section-title {{
    font-size: 1.1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.safety-title {{ color: #f87171; }}
.consensus-title {{ color: #34d399; }}
.contested-title {{ color: #fbbf24; }}
.evidence-title {{ color: #a5b4fc; }}

/* ── Citation chips ── */
.citation-chip {{
    display: inline-block;
    background: {chip_bg};
    border: 1.5px solid {chip_border};
    color: {chip_text};
    font-size: {small_font_size};
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 999px;
    margin: 0 3px;
}}

/* ── Quote highlight ── */
.highlight-quote {{
    background: rgba(251, 191, 36, 0.3);
    border-left: 4px solid #fbbf24;
    padding: 6px 10px;
    border-radius: 4px;
    font-style: italic;
    color: #fef08a;
    font-weight: 600;
}}

/* ── Review card in inspector ── */
.review-card {{
    background: {card_bg};
    border-radius: 10px;
    padding: 1.1rem;
    margin-bottom: 0.8rem;
    border: 1px solid {border_color};
}}
.review-meta {{
    font-size: {small_font_size};
    color: #cbd5e1;
    margin-bottom: 0.4rem;
}}
.star-filled {{ color: #fbbf24; }}
.star-empty  {{ color: #475569; }}

/* ── Alert badge ── */
.alert-badge {{
    display: inline-block;
    background: #dc2626;
    color: white;
    font-size: 0.75rem;
    font-weight: 800;
    padding: 3px 9px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-right: 6px;
}}

.subtle-divider {{
    border: none;
    border-top: 1px solid {border_color};
    margin: 0.8rem 0;
}}

.stButton > button {{
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    padding: 0.5rem 1.8rem;
    transition: transform 0.15s, box-shadow 0.15s;
}}
.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
}}
div[data-testid="stMetricValue"] {{ color: #a5b4fc; font-weight: 800; }}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helper renderers
# ---------------------------------------------------------------------------

def _stars(rating: int) -> str:
    return (
        '<span class="star-filled">' + "★" * rating + "</span>"
        + '<span class="star-empty">' + "★" * (5 - rating) + "</span>"
    )


def _extract_citation_ids(text: str) -> list[int]:
    """Pull all integer IDs from citation patterns like [Review #12] or [#5, #8]."""
    return [int(n) for n in re.findall(r"#(\d+)", text)]


def _render_cited_text(text: str) -> str:
    """Replace [Review #N] / [#N, #M] patterns with styled chip spans."""
    def _replace(m):
        raw = m.group(0)
        ids = re.findall(r"\d+", raw)
        chips = "".join(
            f'<span class="citation-chip" title="Review #{i}">#{i}</span>'
            for i in ids
        )
        return chips

    return re.sub(r"\[(?:Review\s+)?#[\d,\s#]+\]", _replace, text)


def _highlight_quote_in_text(full_text: str, quote: str) -> str:
    """Bold-highlight the matching quote in the full review text."""
    if not quote or not full_text:
        return full_text
    escaped = re.escape(quote[:80])
    highlighted = re.sub(
        escaped,
        f'<span class="highlight-quote">{quote[:80]}</span>',
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
# Evidence Inspector (Right Panel)
# ---------------------------------------------------------------------------

def render_evidence_inspector():
    st.markdown(
        '<div class="section-header">'
        '<span style="font-size:1.4rem">🔎</span>'
        '<span class="section-title evidence-title">Evidence Inspector</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state["selected_review_ids"]:
        st.markdown(
            '<p style="color:#94a3b8;font-size:0.9rem;font-style:italic;">'
            "Click any 🔎 button or citation chip in the summary to trace the exact source reviews here."
            "</p>",
            unsafe_allow_html=True,
        )
        return

    active_ids = st.session_state["selected_review_ids"]
    active_quote = st.session_state.get("selected_quote", "")

    st.markdown(
        f'<p style="color:#a5b4fc;font-size:0.85rem;font-weight:600;">Showing {len(active_ids)} source review(s)</p>',
        unsafe_allow_html=True,
    )

    for rid in active_ids:
        review = _review_lookup(rid)
        if not review:
            continue

        tuples_for_review = _tuple_lookup(rid)
        body_html = _highlight_quote_in_text(review["review_text"], active_quote)

        st.markdown(
            f"""
<div class="review-card">
  <div class="review-meta">
    Review <strong style="color:#a5b4fc;font-size:1rem;">#{rid}</strong> &nbsp;|&nbsp;
    {_stars(review['rating'])} &nbsp;|&nbsp;
    📅 {review['date']} &nbsp;|&nbsp;
    👍 {review['helpful_votes']} helpful votes
  </div>
  <div style="font-size:0.92rem;line-height:1.6;color:#e2e8f0;">{body_html}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if tuples_for_review:
            with st.expander(f"Extracted opinions from Review #{rid}", expanded=False):
                for t in tuples_for_review:
                    sentiment_color = {
                        "positive": "#34d399",
                        "negative": "#f87171",
                        "neutral": "#94a3b8",
                    }.get(t.sentiment, "#94a3b8")
                    st.markdown(
                        f"**{t.aspect}** — "
                        f'<span style="color:{sentiment_color};font-weight:700;">{t.sentiment.upper()}</span><br/>'
                        f'<em style="color:#cbd5e1;">{t.summary_claim}</em>',
                        unsafe_allow_html=True,
                    )


# ---------------------------------------------------------------------------
# Section A — Safety Warnings
# ---------------------------------------------------------------------------

def render_safety_section(alerts):
    if not alerts:
        return

    st.markdown(
        '<div class="card card-safety">'
        '<div class="section-header">'
        '<span style="font-size:1.4rem">🚨</span>'
        '<span class="section-title safety-title">Critical Safety Warnings</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    for alert in alerts:
        review_ids = alert.matching_reviews
        id_str = ", ".join(f"#{r}" for r in review_ids[:6])
        more = f" +{len(review_ids)-6} more" if len(review_ids) > 6 else ""

        st.markdown(
            f'<span class="alert-badge">⚠ CRITICAL</span>'
            f'<strong style="color:#fca5a5;font-size:1.05rem;">'
            f'{alert.risk_term.title()}</strong> detected across '
            f'<strong>{len(review_ids)}</strong> review(s) — '
            f'<span style="color:#cbd5e1;font-size:0.85rem;">{id_str}{more}</span>',
            unsafe_allow_html=True,
        )

        for q in alert.quotes[:2]:
            st.markdown(
                f'<div class="highlight-quote" style="margin:6px 0;">'
                f'"{q[:160]}"</div>',
                unsafe_allow_html=True,
            )

        if st.button(
            f"🔎 Inspect {alert.risk_term.title()} evidence",
            key=f"safety_btn_{alert.risk_term}",
        ):
            _set_inspector(review_ids, alert.quotes[0] if alert.quotes else "")
            st.rerun()

        st.markdown('<hr class="subtle-divider"/>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section B — Consensus Summary
# ---------------------------------------------------------------------------

def render_consensus_section(summary):
    st.markdown(
        '<div class="card card-consensus">'
        '<div class="section-header">'
        '<span style="font-size:1.4rem">✅</span>'
        '<span class="section-title consensus-title">Consensus Summary</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    if not summary or not summary.consensus_points:
        st.markdown(
            '<p style="color:#94a3b8;font-style:italic;">No consensus generated.</p>',
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
                f'<div style="margin:5px 0;font-size:0.95rem;line-height:1.6;">'
                f"• {rendered}</div>",
                unsafe_allow_html=True,
            )
        with col_btn:
            if ids and st.button("🔎", key=f"consensus_btn_{i}", help="Inspect source reviews"):
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
# Section C — Contested Viewpoints
# ---------------------------------------------------------------------------

def render_contested_section(contested, stats):
    st.markdown(
        '<div class="card card-contested">'
        '<div class="section-header">'
        '<span style="font-size:1.4rem">⚖️</span>'
        '<span class="section-title contested-title">Contested Viewpoints</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    if not contested:
        st.markdown(
            '<p style="color:#94a3b8;font-style:italic;">No strongly contested aspects detected.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Aspect distribution chart
    if stats:
        aspects = [s["aspect"] for s in stats[:12]]
        pos_vals = [s["positive"] for s in stats[:12]]
        neg_vals = [s["negative"] for s in stats[:12]]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Positive",
            y=aspects,
            x=pos_vals,
            orientation="h",
            marker_color="#34d399",
            opacity=0.9,
        ))
        fig.add_trace(go.Bar(
            name="Negative",
            y=aspects,
            x=[-v for v in neg_vals],
            orientation="h",
            marker_color="#f87171",
            opacity=0.9,
        ))
        fig.update_layout(
            barmode="overlay",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1", size=12),
            xaxis=dict(
                showgrid=False,
                zeroline=True,
                zerolinecolor="rgba(255,255,255,0.3)",
                tickfont=dict(color="#94a3b8"),
                title="← Negative   |   Positive →",
            ),
            yaxis=dict(showgrid=False),
            legend=dict(
                orientation="h",
                x=0, y=1.08,
                font=dict(size=11),
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            height=max(180, len(aspects) * 30),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Contested aspect detail cards
    for c in contested:
        ratio_pct = int(c.ratio * 100)
        st.markdown(
            f'<div style="margin:10px 0 4px 0;">'
            f'<strong style="color:#fbbf24;font-size:1rem;">{c.aspect}</strong> '
            f'<span style="color:#cbd5e1;font-size:0.85rem;">'
            f'({c.pos_count} positive · {c.neg_count} negative · '
            f'contention {ratio_pct}%)</span>'
            "</div>",
            unsafe_allow_html=True,
        )

        col_pro, col_con = st.columns(2)
        with col_pro:
            st.markdown(
                '<span style="color:#34d399;font-size:0.85rem;font-weight:700;">👍 PRO</span>',
                unsafe_allow_html=True,
            )
            for t in c.pro_citations[:2]:
                rendered = _render_cited_text(f"[Review #{t.review_id}] {t.summary_claim}")
                st.markdown(
                    f'<div style="font-size:0.85rem;color:#a7f3d0;margin:3px 0;">{rendered}</div>',
                    unsafe_allow_html=True,
                )
        with col_con:
            st.markdown(
                '<span style="color:#f87171;font-size:0.85rem;font-weight:700;">👎 CON</span>',
                unsafe_allow_html=True,
            )
            for t in c.con_citations[:2]:
                rendered = _render_cited_text(f"[Review #{t.review_id}] {t.summary_claim}")
                st.markdown(
                    f'<div style="font-size:0.85rem;color:#fca5a5;margin:3px 0;">{rendered}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<hr class="subtle-divider"/>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Accessibility: Web Speech API Audio Briefing (Text-to-Speech)
# ---------------------------------------------------------------------------

def render_audio_briefing(alerts, summary, contested):
    """
    Renders an accessible voice briefing button that uses HTML5 SpeechSynthesis.
    Works natively in the browser without any extra python packages.
    """
    speech_parts = []
    if alerts:
        speech_parts.append("Attention: Critical Safety Warnings Detected.")
        for a in alerts:
            speech_parts.append(f"Risk: {a.risk_term} detected in {len(a.matching_reviews)} reviews.")

    if summary and summary.consensus_points:
        speech_parts.append("Consensus Summary:")
        for p in summary.consensus_points:
            # Strip citation tags for cleaner audio playback
            clean_p = re.sub(r"\[(?:Review\s+)?#[\d,\s#]+\]", "", p).strip()
            speech_parts.append(clean_p)

    if contested:
        speech_parts.append("Contested Viewpoints:")
        for c in contested[:3]:
            speech_parts.append(f"{c.aspect}: polarized feedback with {c.pos_count} positive and {c.neg_count} negative reviews.")

    full_text = " ".join(speech_parts).replace('"', '\\"').replace("\n", " ")

    audio_html = f"""
    <div style="background: rgba(99, 102, 241, 0.15); border: 1.5px solid rgba(99, 102, 241, 0.4); border-radius: 8px; padding: 10px 14px; margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between;">
        <div style="color: #c7d2fe; font-size: 0.9rem; font-weight: 600;">
            🔊 <strong>Voice Accessibility Briefing</strong> (Audio Read-Aloud)
        </div>
        <div>
            <button onclick="playAudioBriefing()" style="background: #4f46e5; color: white; border: none; border-radius: 6px; padding: 6px 14px; font-size: 0.85rem; font-weight: 700; cursor: pointer; margin-right: 6px;">
                ▶ Play Briefing
            </button>
            <button onclick="stopAudioBriefing()" style="background: #334155; color: white; border: none; border-radius: 6px; padding: 6px 14px; font-size: 0.85rem; font-weight: 700; cursor: pointer;">
                ⏹ Stop
            </button>
        </div>
    </div>

    <script>
    function playAudioBriefing() {{
        if (!('speechSynthesis' in window)) {{
            alert('Text-to-speech is not supported by your browser.');
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
    components.html(audio_html, height=60)


# ---------------------------------------------------------------------------
# Report Exporter (Markdown & JSON)
# ---------------------------------------------------------------------------

def generate_export_payloads(product_id: str, brand_name: str, alerts, summary, contested, stats):
    """Generate Markdown and JSON reports for auditing & accessibility."""
    # Markdown
    md_lines = [
        f"# 🔍 OpinionLens Executive Summary Report",
        f"- **Product Model:** {product_id}",
        f"- **Brand/Source:** {brand_name}",
        f"- **Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 🚨 1. Critical Safety Warnings",
    ]
    if alerts:
        for a in alerts:
            md_lines.append(f"- **RISK:** {a.risk_term.upper()} (Found in {len(a.matching_reviews)} reviews: {a.matching_reviews})")
            for q in a.quotes[:2]:
                md_lines.append(f"  - Quote: *\"{q}\"*")
    else:
        md_lines.append("No critical safety warnings detected.")

    md_lines.extend(["", "## ✅ 2. Consensus Summary"])
    if summary and summary.consensus_points:
        for p in summary.consensus_points:
            md_lines.append(f"- {p}")

    md_lines.extend(["", "## ⚖️ 3. Contested Viewpoints"])
    if contested:
        for c in contested:
            md_lines.append(f"- **{c.aspect}:** {c.pos_count} Positive vs {c.neg_count} Negative (Ratio: {c.ratio:.2f})")
    else:
        md_lines.append("No polarized aspects detected.")

    md_content = "\n".join(md_lines)

    # JSON schema
    json_data = {
        "product_id": product_id,
        "brand_name": brand_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
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
# Main pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(csv_source, product_id: str, query: str):
    """Execute the full RAG pipeline and store results in session_state."""
    progress_bar = st.progress(0, text="Starting pipeline…")

    user_api_key = st.session_state.get("user_groq_key", "").strip()
    is_offline = (st.session_state.get("exec_mode") == "🛡️ Zero-API Local Mode (Offline / Free)")
    selected_model = st.session_state.get("selected_model", GROQ_MODEL)

    try:
        # Step 1: Ingest (idempotent)
        progress_bar.progress(0.05, text="Checking vector index in ChromaDB…")
        if not is_already_ingested(product_id):
            progress_bar.progress(0.08, text="Indexing product reviews into ChromaDB…")
            ingest_product(
                csv_source,
                product_id,
                progress_callback=lambda p, m: progress_bar.progress(
                    0.08 + p * 0.32, text=m
                ),
            )

        # Step 2: Retrieval
        progress_bar.progress(0.42, text="Retrieving relevant reviews…")
        is_general = query.strip().lower() in {
            "", "summarize", "summarize entire product", "overall", "general"
        }
        mode = "balanced" if is_general else "aspect"
        reviews = retrieve_opinions(product_id, query, mode=mode)

        if not reviews:
            st.error("No reviews retrieved. Make sure ingestion completed successfully.")
            return

        st.session_state["reviews"] = reviews

        # Step 3: Aspect Extraction
        progress_bar.progress(0.52, text=f"Extracting opinions from {len(reviews)} reviews…")
        extraction = extract_aspects(
            reviews,
            api_key=user_api_key,
            model=selected_model,
            use_offline=is_offline,
        )
        tuples = extraction.extracted_tuples
        st.session_state["tuples"] = tuples

        # Step 4: Safety guard
        progress_bar.progress(0.72, text="Running Critical-Minority Safety Guard…")
        alerts = detect_critical_risks(tuples)
        st.session_state["alerts"] = alerts

        # Step 5: Aggregation
        progress_bar.progress(0.80, text="Computing aspect clusters & contention ratios…")
        clusters = build_aspect_clusters(tuples)
        contested = compute_contention(clusters)
        stats = summarize_aspect_stats(clusters)
        st.session_state["clusters"] = clusters
        st.session_state["contested"] = contested
        st.session_state["stats"] = stats

        # Step 6: Summary generation
        progress_bar.progress(0.88, text="Generating cited summary…")
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
        time.sleep(0.3)
        progress_bar.empty()

    except Exception as e:
        progress_bar.empty()
        st.error(f"Pipeline error: {e}")
        raise


# ---------------------------------------------------------------------------
# UI — Branding Header
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="brand-bar">
  <span style="font-size:2.2rem;">🔍</span>
  <div>
    <p class="brand-title">OpinionLens</p>
    <p class="brand-subtitle">Explainable &amp; Safe RAG · Universal Opinion Summarizer with Evidence Attribution</p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# UI — Controls Row (Dataset, Product, Query, Analyze)
# ---------------------------------------------------------------------------

ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2.5, 3, 3.5, 1.2])

brands = list_all_brands()
brand_labels = list(brands.keys())

# If user uploaded a custom dataset, add it to options
if st.session_state.get("custom_dataset_df") is not None:
    custom_name = st.session_state.get("custom_dataset_name", "Uploaded Dataset")
    brand_labels.insert(0, f"📤 {custom_name}")

default_brand_idx = 0
for i, lbl in enumerate(brand_labels):
    if "lenov" in lbl.lower():
        default_brand_idx = i
        break

with ctrl_col1:
    selected_brand = st.selectbox("📁 Brand / Dataset", brand_labels, index=default_brand_idx)

# Determine active dataset source
if selected_brand.startswith("📤"):
    active_dataset_source = st.session_state["custom_dataset_df"]
else:
    active_dataset_source = brands[selected_brand]

with ctrl_col2:
    with st.spinner("Loading products…"):
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

    selected_product_label = st.selectbox("📱 Product Model", product_labels, index=default_prod_idx)

selected_product_id = product_options[selected_product_label]

with ctrl_col3:
    query = st.text_input(
        "🔍 Query",
        value="",
        placeholder="Leave blank for balanced summary, or ask e.g. 'battery heating issues'",
    )

with ctrl_col4:
    st.markdown("<br/>", unsafe_allow_html=True)
    analyze = st.button("⚡ Analyze", use_container_width=True)


# ---------------------------------------------------------------------------
# Sidebar — Accessibility, AI Engine, & Custom Uploads
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ♿ Accessibility & Display")
    contrast_toggle = st.toggle("👁️ High Contrast Mode (WCAG AAA)", value=st.session_state["high_contrast"])
    if contrast_toggle != st.session_state["high_contrast"]:
        st.session_state["high_contrast"] = contrast_toggle
        st.rerun()

    font_toggle = st.toggle("🔤 Large Readable Text (120%)", value=st.session_state["font_large"])
    if font_toggle != st.session_state["font_large"]:
        st.session_state["font_large"] = font_toggle
        st.rerun()

    st.markdown("---")
    st.markdown("## 🤖 AI Execution Engine")
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
    st.markdown("## 📤 Connect / Upload Dataset")
    with st.expander("Upload CSV or JSON reviews"):
        uploaded_file = st.file_uploader("Upload review file", type=["csv", "json"])
        if uploaded_file is not None:
            try:
                uploaded_df = load_universal_dataset(uploaded_file)
                st.session_state["custom_dataset_df"] = uploaded_df
                st.session_state["custom_dataset_name"] = uploaded_file.name
                st.success(f"Loaded {len(uploaded_df)} reviews from {uploaded_file.name}!")
                if st.button("Use Uploaded Dataset Now"):
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to parse file: {e}")

    st.markdown("---")
    st.markdown("## ⚙️ Vector Index Status")
    st.markdown(f"**Active ID:** `{selected_product_id}`")
    already = is_already_ingested(selected_product_id)
    st.markdown(f"**Status:** {'✅ Vector Index Ready' if already else '⏳ Ingestion required'}")

    if already and st.button("🔄 Force Re-Index"):
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
# Main Results View
# ---------------------------------------------------------------------------

if st.session_state["analysis_done"]:
    alerts = st.session_state["alerts"]
    summary = st.session_state["summary"]
    contested = st.session_state["contested"]
    stats = st.session_state["stats"]

    # Voice Audio Accessibility Bar
    render_audio_briefing(alerts, summary, contested)

    # Metrics Strip
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Reviews analysed", len(st.session_state["reviews"]))
    m2.metric("Opinions extracted", len(st.session_state["tuples"]))
    m3.metric("⚠️ Safety alerts", len(alerts))
    m4.metric("⚖️ Contested aspects", len(contested))

    st.markdown("<br/>", unsafe_allow_html=True)

    left_col, right_col = st.columns([6, 4])

    with left_col:
        render_safety_section(alerts)
        render_consensus_section(summary)
        render_contested_section(contested, stats)

    with right_col:
        st.markdown('<div class="card card-evidence">', unsafe_allow_html=True)
        render_evidence_inspector()
        st.markdown("</div>", unsafe_allow_html=True)

        all_ids = sorted({r["review_id"] for r in st.session_state["reviews"]})
        if all_ids:
            with st.expander("🔢 Jump to specific Review ID"):
                manual_id = st.selectbox("Select Review ID", options=all_ids, key="manual_review_select")
                if st.button("Load Review", key="manual_load_btn"):
                    _set_inspector([manual_id])
                    st.rerun()

    # Export Section
    st.markdown("---")
    st.markdown("### 📥 Export Audit Report")
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
            "📄 Download Report (.md)",
            data=md_report,
            file_name=f"opinionlens_{selected_product_id}.md",
            mime="text/markdown",
        )
    with exp_col2:
        st.download_button(
            "📊 Download Schema (.json)",
            data=json_report,
            file_name=f"opinionlens_{selected_product_id}.json",
            mime="application/json",
        )

elif not analyze:
    # Welcome hero
    st.markdown(
        """
<div style="text-align:center;padding:3.5rem 2rem;color:#94a3b8;">
  <div style="font-size:3.5rem;margin-bottom:0.8rem;">🔍</div>
  <h2 style="color:#cbd5e1;font-weight:700;">Select a dataset & product model, then click ⚡ Analyze</h2>
  <p style="color:#94a3b8;max-width:560px;margin:0 auto;line-height:1.7;">
    OpinionLens retrieves evidence, intercepts critical safety hazards before majority ratings bury them,
    surfaces polarized opinions, and cites every claim with exact review highlights.
  </p>
  <div style="margin-top:2rem;display:flex;gap:1.5rem;justify-content:center;flex-wrap:wrap;">
    <div style="background:rgba(239,68,68,0.15);border:1.5px solid rgba(239,68,68,0.4);border-radius:10px;padding:1rem 1.4rem;min-width:160px;">
      <div style="font-size:1.6rem;">🚨</div>
      <div style="font-weight:700;color:#f87171;margin-top:4px;">Safety Guard</div>
      <div style="font-size:0.8rem;color:#cbd5e1;">Catches critical minority hazards</div>
    </div>
    <div style="background:rgba(16,185,129,0.15);border:1.5px solid rgba(16,185,129,0.4);border-radius:10px;padding:1rem 1.4rem;min-width:160px;">
      <div style="font-size:1.6rem;">✅</div>
      <div style="font-weight:700;color:#34d399;margin-top:4px;">Cited Summary</div>
      <div style="font-size:0.8rem;color:#cbd5e1;">Traceable claims with exact quote chips</div>
    </div>
    <div style="background:rgba(245,158,11,0.15);border:1.5px solid rgba(245,158,11,0.4);border-radius:10px;padding:1rem 1.4rem;min-width:160px;">
      <div style="font-size:1.6rem;">⚖️</div>
      <div style="font-weight:700;color:#fbbf24;margin-top:4px;">Contested Views</div>
      <div style="font-size:0.8rem;color:#cbd5e1;">Surfaces polarized user opinions</div>
    </div>
    <div style="background:rgba(99,102,241,0.15);border:1.5px solid rgba(99,102,241,0.4);border-radius:10px;padding:1rem 1.4rem;min-width:160px;">
      <div style="font-size:1.6rem;">🔊</div>
      <div style="font-weight:700;color:#a5b4fc;margin-top:4px;">Audio Accessibility</div>
      <div style="font-size:0.8rem;color:#cbd5e1;">Hands-free voice read-aloud briefing</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
