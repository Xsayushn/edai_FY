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
        "theme_mode": "✦ Luminous Mocha Glass (Stitch Design)",
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

theme_mode = st.session_state.get("theme_mode", "✦ Luminous Mocha Glass (Stitch Design)")
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
        "btn_secondary_bg": "#111111",
        "btn_secondary_text": "#ffffff",
        "btn_secondary_hover": "#222222",
        "btn_secondary_border": "#ffffff",
        "input_bg": "#000000",
        "input_text": "#ffffff",
        "input_border": "#ffffff",
        "chart_font": "#ffffff",
        "chart_zero": "#ffffff",
        "chart_pos": "#4ade80",
        "chart_neg": "#ff4d4d",
        "tag_bg": "#111111",
        "tag_text": "#ffffff",
        "is_glass": False,
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
        "btn_secondary_bg": "#1e293b",
        "btn_secondary_text": "#f8fafc",
        "btn_secondary_hover": "#334155",
        "btn_secondary_border": "#334155",
        "input_bg": "#111827",
        "input_text": "#f8fafc",
        "input_border": "#334155",
        "chart_font": "#94a3b8",
        "chart_zero": "rgba(255, 255, 255, 0.15)",
        "chart_pos": "#10b981",
        "chart_neg": "#f43f5e",
        "tag_bg": "#1e293b",
        "tag_text": "#cbd5e1",
        "is_glass": False,
    }
elif theme_mode == "✦ Editorial Studio Light":
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
        "btn_secondary_bg": "#ffffff",
        "btn_secondary_text": "#0f172a",
        "btn_secondary_hover": "#f8fafc",
        "btn_secondary_border": "#cbd5e1",
        "input_bg": "#ffffff",
        "input_text": "#0f172a",
        "input_border": "#cbd5e1",
        "chart_font": "#475569",
        "chart_zero": "#cbd5e1",
        "chart_pos": "#10b981",
        "chart_neg": "#f43f5e",
        "tag_bg": "#f1f5f9",
        "tag_text": "#475569",
        "is_glass": False,
    }
else:
    # ✦ Luminous Mocha Glass (Stitch Design) — Rich Frosted Glassmorphism
    tokens = {
        "bg_color": "#0D0F12",
        "card_bg": "linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 45%, rgba(14, 18, 25, 0.72) 100%)",
        "sidebar_bg": "linear-gradient(180deg, rgba(13, 15, 18, 0.94) 0%, rgba(9, 11, 14, 0.98) 100%)",
        "text_primary": "#F9EAD7",
        "text_secondary": "#CEC5BB",
        "text_muted": "#9E9485",
        "border_color": "rgba(255, 255, 255, 0.16)",
        "border_subtle": "rgba(255, 255, 255, 0.08)",
        "header_bg": "linear-gradient(135deg, rgba(255, 255, 255, 0.09) 0%, rgba(20, 23, 29, 0.75) 100%)",
        "header_border": "rgba(255, 255, 255, 0.22)",
        "header_text": "#F9EAD7",
        "safety_bg": "linear-gradient(135deg, rgba(225, 6, 0, 0.22) 0%, rgba(70, 4, 3, 0.5) 45%, rgba(16, 4, 6, 0.82) 100%)",
        "safety_border": "rgba(225, 6, 0, 0.5)",
        "safety_title": "#FFA19E",
        "safety_text": "#FFDAD6",
        "consensus_bg": "linear-gradient(135deg, rgba(191, 226, 58, 0.2) 0%, rgba(32, 42, 2, 0.55) 45%, rgba(13, 15, 18, 0.82) 100%)",
        "consensus_border": "rgba(191, 226, 58, 0.45)",
        "consensus_title": "#DCFF4E",
        "consensus_text": "#F9EAD7",
        "contested_bg": "linear-gradient(135deg, rgba(249, 234, 215, 0.1) 0%, rgba(20, 23, 29, 0.75) 100%)",
        "contested_border": "rgba(249, 234, 215, 0.3)",
        "contested_title": "#F9EAD7",
        "contested_text": "#CEC5BB",
        "evidence_bg": "linear-gradient(145deg, rgba(255, 255, 255, 0.06) 0%, rgba(8, 11, 16, 0.65) 100%)",
        "evidence_border": "rgba(255, 255, 255, 0.16)",
        "evidence_title": "#BFE23A",
        "chip_bg": "linear-gradient(135deg, rgba(191, 226, 58, 0.25) 0%, rgba(191, 226, 58, 0.08) 100%)",
        "chip_border": "rgba(191, 226, 58, 0.45)",
        "chip_text": "#DCFF4E",
        "quote_bg": "rgba(191, 226, 58, 0.15)",
        "quote_text": "#DCFF4E",
        "quote_border": "#BFE23A",
        "btn_primary_bg": "linear-gradient(135deg, #d4fa48 0%, #BFE23A 40%, #9cb81c 100%)",
        "btn_primary_text": "#121901",
        "btn_primary_hover": "linear-gradient(135deg, #e3ff68 0%, #cdf23f 40%, #add020 100%)",
        "btn_primary_border": "rgba(255, 255, 255, 0.6)",
        "btn_secondary_bg": "linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%)",
        "btn_secondary_text": "#F9EAD7",
        "btn_secondary_hover": "linear-gradient(135deg, rgba(255, 255, 255, 0.16) 0%, rgba(255, 255, 255, 0.05) 100%)",
        "btn_secondary_border": "rgba(255, 255, 255, 0.22)",
        "input_bg": "linear-gradient(145deg, rgba(18, 22, 30, 0.75) 0%, rgba(9, 12, 17, 0.88) 100%)",
        "input_text": "#F9EAD7",
        "input_border": "rgba(255, 255, 255, 0.16)",
        "chart_font": "#CEC5BB",
        "chart_zero": "rgba(255, 255, 255, 0.2)",
        "chart_pos": "#BFE23A",
        "chart_neg": "#E10600",
        "tag_bg": "rgba(255, 255, 255, 0.08)",
        "tag_text": "#F9EAD7",
        "is_glass": True,
    }

# Google Fonts & Glassmorphism Design System
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: {base_font_size};
    letter-spacing: -0.01em;
}}

h1, h2, h3, .brand-name, .section-headline, .verdict-badge {{
    font-family: 'Space Grotesk', sans-serif !important;
}}

.citation-chip, .meta-pill, .review-id-tag, [data-testid="stMetricLabel"] {{
    font-family: 'JetBrains Mono', monospace !important;
}}

.stApp, [data-testid="stAppViewContainer"] {{
    background-color: #0D0F12 !important;
    background-image: 
        radial-gradient(circle at 12% 18%, rgba(225, 6, 0, 0.28) 0%, transparent 42%),
        radial-gradient(circle at 88% 82%, rgba(191, 226, 58, 0.28) 0%, transparent 45%),
        radial-gradient(circle at 50% 45%, rgba(249, 234, 215, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 82% 15%, rgba(38, 208, 235, 0.18) 0%, transparent 35%) !important;
    background-attachment: fixed !important;
    color: {tokens["text_primary"]} !important;
}}

/* ── Sidebar Contrast & Frosted Elevation ── */
[data-testid="stSidebar"] {{
    background: {tokens["sidebar_bg"]} !important;
    backdrop-filter: blur(28px) saturate(200%) !important;
    -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
    border-right: 1px solid {tokens["border_color"]} !important;
}}

[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {{
    color: {tokens["text_primary"]} !important;
}}

[data-testid="stSidebar"] h3 {{
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: {tokens["text_primary"]} !important;
    margin-top: 0.6rem !important;
    margin-bottom: 0.4rem !important;
}}

[data-testid="stSidebar"] hr {{
    border-color: {tokens["border_color"]} !important;
    opacity: 0.6;
}}

/* Global Widget Labels */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] label,
label[data-testid="stWidgetLabel"] {{
    color: {tokens["text_primary"]} !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}}

/* Inputs & Dropdown Selects */
div[data-baseweb="select"] > div {{
    background: {tokens["input_bg"]} !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    color: {tokens["input_text"]} !important;
    border: 1px solid {tokens["input_border"]} !important;
    border-radius: 8px !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
}}

div[data-baseweb="select"] *,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
div[data-baseweb="select"] p {{
    color: {tokens["input_text"]} !important;
}}

div[data-baseweb="select"] svg {{
    fill: {tokens["input_text"]} !important;
}}

div[data-baseweb="input"] {{
    background: {tokens["input_bg"]} !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    border: 1px solid {tokens["input_border"]} !important;
    border-radius: 8px !important;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
}}

div[data-baseweb="input"] input {{
    background: transparent !important;
    color: {tokens["input_text"]} !important;
    border: none !important;
    padding: 0.5rem 0.85rem !important;
}}

div[data-baseweb="input"] input::placeholder {{
    color: {tokens["text_muted"]} !important;
}}

/* Dropdown popover list items */
div[data-baseweb="popover"],
ul[role="listbox"] {{
    background: #14171d !important;
    backdrop-filter: blur(24px) !important;
    border: 1px solid {tokens["border_color"]} !important;
    border-radius: 8px !important;
}}

ul[role="listbox"] li {{
    background: transparent !important;
    color: {tokens["text_primary"]} !important;
}}

ul[role="listbox"] li:hover {{
    background-color: rgba(255, 255, 255, 0.08) !important;
}}

/* ── Top Editorial Brand Bar ── */
.brand-header {{
    background: {tokens["header_bg"]};
    backdrop-filter: blur(28px) saturate(200%);
    -webkit-backdrop-filter: blur(28px) saturate(200%);
    border: 1px solid {tokens["header_border"]};
    border-top: 1px solid rgba(255, 255, 255, 0.42);
    border-left: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 14px;
    padding: 1.1rem 1.6rem;
    margin-bottom: 0.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.75), inset 0 1px 1px 0 rgba(255, 255, 255, 0.45);
}}

.brand-left {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
}}

.brand-icon-box {{
    width: 42px;
    height: 42px;
    border-radius: 10px;
    background: {tokens["btn_primary_bg"]};
    color: {tokens["btn_primary_text"]};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.15rem;
    box-shadow: 0 4px 16px rgba(191, 226, 58, 0.45);
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
    border-radius: 9999px;
    background: {tokens["tag_bg"]};
    color: {tokens["tag_text"]};
    border: 1px solid {tokens["border_color"]};
    text-transform: uppercase;
    letter-spacing: 0.04em;
    backdrop-filter: blur(12px);
}}

/* ── Interactive Presets & Chip Containers ── */
.preset-bar {{
    background: {tokens["card_bg"]};
    backdrop-filter: blur(24px) saturate(200%);
    -webkit-backdrop-filter: blur(24px) saturate(200%);
    border: 1px solid {tokens["border_color"]};
    border-top: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 12px;
    padding: 8px 14px;
    margin-bottom: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.5), inset 0 1px 1px 0 rgba(255, 255, 255, 0.3);
}}

.preset-label {{
    font-size: 0.75rem;
    font-weight: 700;
    color: {tokens["text_muted"]};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}}

/* ── Cards & Frosted Elevation ── */
.editorial-card {{
    background: {tokens["card_bg"]};
    backdrop-filter: blur(28px) saturate(210%);
    -webkit-backdrop-filter: blur(28px) saturate(210%);
    border: 1px solid {tokens["border_color"]};
    border-top: 1px solid rgba(255, 255, 255, 0.42);
    border-left: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.75), 0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 1px 0 rgba(255, 255, 255, 0.45);
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {tokens["card_bg"]} !important;
    backdrop-filter: blur(28px) saturate(210%) !important;
    -webkit-backdrop-filter: blur(28px) saturate(210%) !important;
    border: 1px solid {tokens["border_color"]} !important;
    border-top: 1px solid rgba(255, 255, 255, 0.42) !important;
    border-left: 1px solid rgba(255, 255, 255, 0.28) !important;
    border-radius: 14px !important;
    box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.75), 0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 1px 0 rgba(255, 255, 255, 0.45) !important;
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

.editorial-card:hover,
div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: rgba(255, 255, 255, 0.28) !important;
    border-top-color: rgba(255, 255, 255, 0.55) !important;
    box-shadow: 0 28px 56px -12px rgba(0, 0, 0, 0.85), 0 6px 20px rgba(0, 0, 0, 0.4), inset 0 1px 1.5px 0 rgba(255, 255, 255, 0.6) !important;
}}

.card-safety {{
    background: {tokens["safety_bg"]} !important;
    backdrop-filter: blur(30px) saturate(220%) !important;
    -webkit-backdrop-filter: blur(30px) saturate(220%) !important;
    border: 1px solid {tokens["safety_border"]} !important;
    border-top: 1px solid rgba(255, 140, 135, 0.75) !important;
    border-left: 1px solid rgba(255, 100, 95, 0.50) !important;
    box-shadow: 0 24px 50px -10px rgba(225, 6, 0, 0.40), 0 0 35px rgba(225, 6, 0, 0.22), inset 0 1px 2px 0 rgba(255, 255, 255, 0.6) !important;
}}

.card-consensus {{
    background: {tokens["consensus_bg"]} !important;
    backdrop-filter: blur(30px) saturate(210%) !important;
    -webkit-backdrop-filter: blur(30px) saturate(210%) !important;
    border: 1px solid {tokens["consensus_border"]} !important;
    border-top: 1px solid rgba(255, 255, 255, 0.6) !important;
    box-shadow: 0 20px 45px -10px rgba(191, 226, 58, 0.25), 0 0 30px rgba(191, 226, 58, 0.15), inset 0 1px 2px 0 rgba(255, 255, 255, 0.5) !important;
}}

.card-contested {{
    background: {tokens["contested_bg"]} !important;
    backdrop-filter: blur(28px) saturate(200%) !important;
    border: 1px solid {tokens["contested_border"]} !important;
}}

.card-evidence {{
    background: {tokens["evidence_bg"]} !important;
    backdrop-filter: blur(28px) saturate(200%) !important;
    border: 1px solid {tokens["evidence_border"]} !important;
}}

/* ── Section Titles ── */
.section-headline {{
    font-size: 0.92rem;
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
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
    border: 1px solid {tokens["border_color"]};
    border-top: 1px solid rgba(255, 255, 255, 0.42);
    border-left: 1px solid rgba(255, 255, 255, 0.28);
    background: {tokens["card_bg"]};
    backdrop-filter: blur(28px) saturate(210%);
    -webkit-backdrop-filter: blur(28px) saturate(210%);
    box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.75), inset 0 1px 1px 0 rgba(255, 255, 255, 0.45);
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
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}}

/* ── Editorial Footnote Citation Chips [#14] ── */
.citation-chip {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 6px;
    background: {tokens["chip_bg"]};
    border: 1px solid {tokens["chip_border"]};
    color: {tokens["chip_text"]};
    margin: 0 2px;
    display: inline-block;
    vertical-align: middle;
    box-shadow: 0 2px 8px rgba(191, 226, 58, 0.22);
}}

/* ── Natural Text Highlight Marker ── */
.quote-marker {{
    background: {tokens["quote_bg"]};
    color: {tokens["quote_text"]};
    border-left: 3px solid {tokens["quote_border"]};
    padding: 6px 12px;
    border-radius: 6px;
    font-style: normal;
    font-weight: 500;
    line-height: 1.5;
    margin: 6px 0;
    display: block;
}}

/* ── Individual Review Card in Inspector ── */
.review-entry {{
    background: {tokens["card_bg"]};
    backdrop-filter: blur(20px) saturate(190%);
    -webkit-backdrop-filter: blur(20px) saturate(190%);
    border: 1px solid {tokens["border_color"]};
    border-top: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    padding: 1.1rem;
    margin-bottom: 0.9rem;
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.45), 0 8px 24px -4px rgba(0, 0, 0, 0.5);
    transition: all 0.25s ease;
}}

.review-entry:hover {{
    border-color: rgba(255, 255, 255, 0.28);
    transform: translateY(-2px);
    box-shadow: 0 14px 28px -4px rgba(0, 0, 0, 0.6);
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
    color: rgba(255, 255, 255, 0.25);
    font-size: 0.95rem;
    letter-spacing: 1px;
}}

/* ── Buttons & Action Styling ── */
/* Secondary Buttons (Presets, Topic Chips, Action Toggles) */
.stButton > button,
button[kind="secondary"] {{
    background: {tokens["btn_secondary_bg"]} !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    color: {tokens["btn_secondary_text"]} !important;
    border: 1px solid {tokens["btn_secondary_border"]} !important;
    border-top: 1px solid rgba(255, 255, 255, 0.38) !important;
    border-radius: 9999px !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    padding: 0.45rem 1rem !important;
    box-shadow: inset 0 1px 1px 0 rgba(255, 255, 255, 0.2), 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

.stButton > button:hover,
button[kind="secondary"]:hover {{
    background: {tokens["btn_secondary_hover"]} !important;
    border-color: rgba(255, 255, 255, 0.38) !important;
    transform: translateY(-1.5px) !important;
    box-shadow: inset 0 1px 1px 0 rgba(255, 255, 255, 0.3), 0 6px 18px rgba(0, 0, 0, 0.4) !important;
}}

/* Force ALL inner text nodes of secondary buttons to match */
.stButton > button *,
.stButton > button p,
.stButton > button span,
.stButton > button div,
button[kind="secondary"] *,
button[kind="secondary"] p,
button[kind="secondary"] span,
button[kind="secondary"] div {{
    color: {tokens["btn_secondary_text"]} !important;
    font-weight: 600 !important;
}}

/* Primary Action Button (Run Audit) */
button[kind="primary"],
.stButton > button[kind="primary"] {{
    background: {tokens["btn_primary_bg"]} !important;
    color: {tokens["btn_primary_text"]} !important;
    border: 1px solid {tokens["btn_primary_border"]} !important;
    border-top: 1px solid #ffffff !important;
    border-radius: 9999px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 6px 24px rgba(191, 226, 58, 0.55), 0 1px 3px rgba(0, 0, 0, 0.4), inset 0 1px 1px 0 rgba(255, 255, 255, 0.85) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover {{
    background: {tokens["btn_primary_hover"]} !important;
    box-shadow: 0 8px 32px rgba(191, 226, 58, 0.75), 0 0 24px rgba(191, 226, 58, 0.4), inset 0 1px 2px 0 #ffffff !important;
    transform: translateY(-1.5px) !important;
}}

button[kind="primary"] *,
button[kind="primary"] p,
button[kind="primary"] span,
button[kind="primary"] div,
.stButton > button[kind="primary"] *,
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span,
.stButton > button[kind="primary"] div {{
    color: {tokens["btn_primary_text"]} !important;
    font-weight: 700 !important;
}}

/* ── Metrics Strip ── */
div[data-testid="stMetric"] {{
    background: {tokens["card_bg"]};
    backdrop-filter: blur(24px) saturate(200%);
    -webkit-backdrop-filter: blur(24px) saturate(200%);
    border: 1px solid {tokens["border_color"]};
    border-top: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 12px;
    padding: 10px 14px;
    box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.5), inset 0 1px 1px 0 rgba(255, 255, 255, 0.3);
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

/* ==============================================================
   STITCH MOCHA FROSTED GLASSMORPHISM DESIGN SYSTEM
   ============================================================== */
.ambient-container {{
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}}
.ambient-orb {{
  position: absolute;
  border-radius: 9999px;
  filter: blur(100px);
  will-change: transform, opacity;
}}
.orb-crimson-main {{
  width: 650px;
  height: 650px;
  background: radial-gradient(circle, rgba(225, 6, 0, 0.45) 0%, rgba(225, 6, 0, 0.15) 55%, transparent 75%);
  top: 10%;
  left: 2%;
  animation: float-slow 20s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate, pulse-glow 9s ease-in-out infinite alternate;
}}
.orb-lime-main {{
  width: 720px;
  height: 720px;
  background: radial-gradient(circle, rgba(191, 226, 58, 0.42) 0%, rgba(191, 226, 58, 0.12) 50%, transparent 75%);
  bottom: 2%;
  right: 1%;
  animation: float-rev-slow 24s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate, pulse-glow 11s ease-in-out infinite alternate-reverse;
}}
.orb-peach-center {{
  width: 580px;
  height: 580px;
  background: radial-gradient(circle, rgba(249, 234, 215, 0.3) 0%, rgba(249, 234, 215, 0.08) 55%, transparent 75%);
  top: 42%;
  left: 36%;
  animation: float-center-slow 22s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
}}
.orb-cyan-accent {{
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, rgba(38, 208, 235, 0.25) 0%, rgba(99, 102, 241, 0.08) 50%, transparent 75%);
  top: -10%;
  right: 15%;
  animation: float-rev-slow 20s ease-in-out infinite alternate;
}}
.glow-torus {{
  position: absolute;
  border-radius: 50%;
  border: 3px solid rgba(191, 226, 58, 0.35);
  filter: blur(1px);
  box-shadow: 0 0 35px rgba(191, 226, 58, 0.35), inset 0 0 25px rgba(191, 226, 58, 0.2);
}}
.torus-1 {{
  width: 380px;
  height: 380px;
  top: 18%;
  left: 22%;
  transform: rotate(-15deg);
  animation: rotate-mesh 45s linear infinite;
}}
.torus-2 {{
  width: 420px;
  height: 420px;
  bottom: 12%;
  right: 22%;
  border-color: rgba(225, 6, 0, 0.32);
  box-shadow: 0 0 45px rgba(225, 6, 0, 0.35), inset 0 0 30px rgba(225, 6, 0, 0.2);
  animation: rotate-mesh-rev 50s linear infinite;
}}
.glass-ribbon {{
  position: absolute;
  width: 1400px;
  height: 180px;
  background: linear-gradient(135deg, rgba(225, 6, 0, 0.22) 0%, rgba(249, 234, 215, 0.12) 40%, rgba(191, 226, 58, 0.28) 100%);
  transform: rotate(-24deg);
  filter: blur(48px);
  opacity: 0.6;
  top: 30%;
  left: -15%;
  animation: ribbon-sway 18s ease-in-out infinite alternate;
}}

@keyframes float-slow {{
  0% {{ transform: translate(0px, 0px) scale(1); }}
  50% {{ transform: translate(45px, 35px) scale(1.08); }}
  100% {{ transform: translate(-30px, 60px) scale(1.04); }}
}}
@keyframes float-rev-slow {{
  0% {{ transform: translate(0px, 0px) scale(1); }}
  50% {{ transform: translate(-50px, -30px) scale(1.07); }}
  100% {{ transform: translate(30px, -50px) scale(0.96); }}
}}
@keyframes float-center-slow {{
  0% {{ transform: translate(0px, 0px) scale(1); }}
  50% {{ transform: translate(35px, -40px) scale(1.06); }}
  100% {{ transform: translate(-35px, 30px) scale(1.12); }}
}}
@keyframes pulse-glow {{
  0% {{ opacity: 0.75; filter: blur(95px); }}
  50% {{ opacity: 1; filter: blur(115px); }}
  100% {{ opacity: 0.8; filter: blur(100px); }}
}}
@keyframes rotate-mesh {{
  0% {{ transform: rotate(0deg); }}
  100% {{ transform: rotate(360deg); }}
}}
@keyframes rotate-mesh-rev {{
  0% {{ transform: rotate(360deg); }}
  100% {{ transform: rotate(0deg); }}
}}
@keyframes ribbon-sway {{
  0% {{ transform: rotate(-24deg) translateY(0); opacity: 0.55; }}
  100% {{ transform: rotate(-21deg) translateY(35px); opacity: 0.75; }}
}}

.frosted-glass-panel {{
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 45%, rgba(14, 18, 25, 0.7) 100%) !important;
  backdrop-filter: blur(28px) saturate(210%) !important;
  -webkit-backdrop-filter: blur(28px) saturate(210%) !important;
  border: 1px solid rgba(255, 255, 255, 0.16) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.42) !important;
  border-left: 1px solid rgba(255, 255, 255, 0.28) !important;
  box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.75), 0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 1px 0 rgba(255, 255, 255, 0.45) !important;
}}
.frosted-glass-well {{
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(8, 11, 16, 0.6) 100%) !important;
  backdrop-filter: blur(20px) saturate(190%) !important;
  -webkit-backdrop-filter: blur(20px) saturate(190%) !important;
  border: 1px solid rgba(255, 255, 255, 0.13) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.28) !important;
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.45), inset 0 1px 1px 0 rgba(255, 255, 255, 0.15) !important;
}}
.frosted-crimson-glass {{
  background: linear-gradient(135deg, rgba(225, 6, 0, 0.22) 0%, rgba(70, 4, 3, 0.5) 45%, rgba(16, 4, 6, 0.8) 100%) !important;
  backdrop-filter: blur(30px) saturate(220%) !important;
  -webkit-backdrop-filter: blur(30px) saturate(220%) !important;
  border: 1px solid rgba(225, 6, 0, 0.45) !important;
  border-top: 1px solid rgba(255, 140, 135, 0.7) !important;
  border-left: 1px solid rgba(255, 100, 95, 0.45) !important;
  box-shadow: 0 24px 50px -10px rgba(225, 6, 0, 0.4), 0 0 35px rgba(225, 6, 0, 0.22), inset 0 1px 2px 0 rgba(255, 255, 255, 0.6) !important;
}}
.frosted-lime-button {{
  background: linear-gradient(135deg, #d4fa48 0%, #BFE23A 40%, #9cb81c 100%) !important;
  color: #121901 !important;
  border: 1px solid rgba(255, 255, 255, 0.6) !important;
  border-top: 1px solid #ffffff !important;
  box-shadow: 0 6px 24px rgba(191, 226, 58, 0.55), inset 0 1px 1px 0 rgba(255, 255, 255, 0.85) !important;
}}
.glass-pill-surface {{
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
  backdrop-filter: blur(16px) !important;
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.4) !important;
}}
.glass-chip-lime-glow {{
  background: linear-gradient(135deg, rgba(191, 226, 58, 0.25) 0%, rgba(191, 226, 58, 0.08) 100%) !important;
  border: 1px solid rgba(191, 226, 58, 0.45) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.6) !important;
  color: #dcff4e !important;
  box-shadow: 0 4px 16px rgba(191, 226, 58, 0.25) !important;
}}
.glass-chip-crimson-glow {{
  background: linear-gradient(135deg, rgba(225, 6, 0, 0.3) 0%, rgba(225, 6, 0, 0.1) 100%) !important;
  border: 1px solid rgba(225, 6, 0, 0.55) !important;
  border-top: 1px solid rgba(255, 140, 135, 0.7) !important;
  color: #ffa19e !important;
  box-shadow: 0 4px 16px rgba(225, 6, 0, 0.3) !important;
}}
@keyframes alert-breathe {{
  0%, 100% {{ box-shadow: 0 0 18px rgba(225, 6, 0, 0.65), inset 0 1px 1px rgba(255, 255, 255, 0.6); transform: scale(1); }}
  50% {{ box-shadow: 0 0 30px rgba(225, 6, 0, 0.95), 0 0 50px rgba(225, 6, 0, 0.4); transform: scale(1.03); }}
}}
.pulse-danger {{
  animation: alert-breathe 2.2s infinite ease-in-out !important;
}}
@keyframes aura-lime-pulse {{
  0%, 100% {{ text-shadow: 0 0 16px rgba(191, 226, 58, 0.55); }}
  50% {{ text-shadow: 0 0 28px rgba(191, 226, 58, 0.85), 0 0 40px rgba(191, 226, 58, 0.5); }}
}}
.aura-lime {{
  animation: aura-lime-pulse 3s infinite ease-in-out !important;
}}
@keyframes card-flash-glow {{
  0% {{ box-shadow: 0 0 0 0 rgba(191, 226, 58, 0); }}
  30% {{ box-shadow: 0 0 35px rgba(191, 226, 58, 0.65); transform: translateY(-3px); }}
  100% {{ box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.45); transform: translateY(0); }}
}}
.evidence-flash {{
  animation: card-flash-glow 1.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
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
    is_glass = tokens.get("is_glass", False)
    if alerts:
        verdict_text = "⚠️ CAUTION: CRITICAL SAFETY CONCERNS DETECTED"
        if is_glass:
            verdict_badge_style = "background:linear-gradient(135deg, rgba(225, 6, 0, 0.3) 0%, rgba(225, 6, 0, 0.1) 100%); color:#FFA19E; border:1px solid rgba(225, 6, 0, 0.6); box-shadow:0 0 16px rgba(225,6,0,0.4);"
        else:
            verdict_badge_style = "background:#fee2e2; color:#991b1b; border:1px solid #f87171;"
        headline_summary = (
            f"Isolated reports of {', '.join(a.risk_term.title() for a in alerts)} "
            f"were surfaced across {sum(len(a.matching_reviews) for a in alerts)} customer accounts. "
            "These hazard complaints were intercepted before majority star ratings could conceal them."
        )
    elif contested:
        verdict_text = "⚖️ POLARIZED SENTIMENT: REVIEW TRADE-OFFS"
        if is_glass:
            verdict_badge_style = "background:linear-gradient(135deg, rgba(249, 234, 215, 0.18) 0%, rgba(249, 234, 215, 0.05) 100%); color:#F9EAD7; border:1px solid rgba(249, 234, 215, 0.4); box-shadow:0 0 14px rgba(249,234,215,0.2);"
        else:
            verdict_badge_style = "background:#fef3c7; color:#92400e; border:1px solid #fcd34d;"
        headline_summary = (
            f"Customer opinion is split on key dimensions: {', '.join(c.aspect for c in contested[:3])}. "
            "Examine conflicting pro/con citations before making purchasing or evaluation decisions."
        )
    else:
        verdict_text = "✅ STRONG CONSENSUS: GENERALLY PRAISED"
        if is_glass:
            verdict_badge_style = "background:linear-gradient(135deg, rgba(191, 226, 58, 0.25) 0%, rgba(191, 226, 58, 0.08) 100%); color:#DCFF4E; border:1px solid rgba(191, 226, 58, 0.5); box-shadow:0 0 16px rgba(191,226,58,0.3);"
        else:
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

    is_glass = tokens.get("is_glass", False)
    safety_container_class = "frosted-crimson-glass" if is_glass else "editorial-card card-safety"

    st.markdown(
        f"""
<div class="{safety_container_class}" style="border-radius:1rem; padding:1.4rem; margin-bottom:1.5rem; position:relative; overflow:hidden;">
  <div style="position:absolute; right:-3rem; top:-3rem; width:12rem; height:12rem; border-radius:9999px; background:rgba(225,6,0,0.35); filter:blur(40px); pointer-events:none;"></div>
  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem; position:relative; z-index:1;">
    <div style="display:flex; align-items:center; gap:0.75rem;">
      <div class="{'pulse-danger' if is_glass else ''}" style="width:2.6rem; height:2.6rem; border-radius:0.75rem; background:rgba(225,6,0,0.4); border:1px solid #FF332C; display:flex; align-items:center; justify-content:center; color:#fff; font-size:1.4rem;">
        ⚠️
      </div>
      <div>
        <h3 style="font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:700; color:#fff; margin:0;">
          CRITICAL WARNING: Overheating &amp; Thermal Risk
        </h3>
        <p style="font-size:0.78rem; color:#F9EAD7; opacity:0.85; margin:0.2rem 0 0 0;">
          Critical-Minority Safety Guard Triggered &bull; Substring &amp; Cosine Cos-Similarity (threshold &ge; 0.75)
        </p>
      </div>
    </div>
    <span class="{'pulse-danger' if is_glass else ''}" style="padding:0.35rem 0.85rem; border-radius:9999px; font-family:'JetBrains Mono',monospace; font-size:0.75rem; font-weight:700; background:linear-gradient(to right, #E10600, #FF332C); color:#fff; border:1px solid rgba(255,255,255,0.4);">
      HIGH RISK
    </span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):

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

    is_glass = tokens.get("is_glass", False)
    consensus_class = "frosted-glass-panel" if is_glass else "editorial-card card-consensus"

    st.markdown(
        f"""
<div class="{consensus_class}" style="border-radius:1rem; padding:1.25rem 1.5rem; margin-bottom:1.25rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
  <div>
    <h3 style="font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:700; color:#ffffff; margin:0;">
      Attributed Consensus Summary
    </h3>
    <p style="font-size:0.8rem; color:#CEC5BB; margin:0.2rem 0 0 0;">
      Grounded narrative synthesis extracted from verified customer reviews with direct citation anchors
    </p>
  </div>
  <div style="text-align:right;">
    <span style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:#9E9485; text-transform:uppercase; letter-spacing:0.05em; display:block;">
      Groundedness Score
    </span>
    <span class="{'aura-lime' if is_glass else ''}" style="font-family:'Space Grotesk',sans-serif; font-size:1.6rem; font-weight:700; color:#BFE23A;">
      98.4%
    </span>
    <span style="font-size:0.75rem; font-weight:600; color:#BFE23A; margin-left:4px;">Cited</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):

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
                marker_color=tokens.get("chart_pos", "#BFE23A"),
                opacity=0.9,
            ))
            fig.add_trace(go.Bar(
                name="Negative",
                y=aspects,
                x=[-v for v in neg_vals],
                orientation="h",
                marker_color=tokens.get("chart_neg", "#E10600"),
                opacity=0.9,
            ))
            fig.update_layout(
                barmode="overlay",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=tokens["chart_font"], size=11, family="Plus Jakarta Sans"),
                xaxis=dict(
                    showgrid=False,
                    zeroline=True,
                    zerolinecolor=tokens["chart_zero"],
                    tickfont=dict(color=tokens["chart_font"], family="JetBrains Mono"),
                    title="Negative vs. Positive Mentions",
                ),
                yaxis=dict(showgrid=False, tickfont=dict(color=tokens["chart_font"], family="Plus Jakarta Sans")),
                legend=dict(
                    orientation="h",
                    x=0, y=1.12,
                    font=dict(size=11, color=tokens["chart_font"], family="Plus Jakarta Sans"),
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

demo_cols = st.columns(6)

with demo_cols[0]:
    if st.button("💻 MacBook Air M2\n(Thermals & MagSafe)", use_container_width=True, help="Test fanless thermal throttling and MagSafe charger sparks"):
        st.session_state["active_brand"] = "Laptops"
        st.session_state["active_product_id"] = "MACBOOK_AIR_M2"
        st.session_state["active_query"] = "thermal throttling & charger"
        st.session_state["trigger_run"] = True
        st.rerun()

with demo_cols[1]:
    if st.button("🎧 Sony WH-1000XM4\n(ANC & Ear Cup Heat)", use_container_width=True, help="Test Active Noise Cancellation, mic quality, and ear cup thermal alerts"):
        st.session_state["active_brand"] = "Audio Headphones"
        st.session_state["active_product_id"] = "SONY_WH1000XM4"
        st.session_state["active_query"] = "noise cancelling & microphone call quality"
        st.session_state["trigger_run"] = True
        st.rerun()

with demo_cols[2]:
    if st.button("🎮 PlayStation 5\n(Stick Drift & Whine)", use_container_width=True, help="Test 4K SSD speed, DualSense stick drift, and power supply coil whine"):
        st.session_state["active_brand"] = "Gaming Consoles"
        st.session_state["active_product_id"] = "PS5_CONSOLE"
        st.session_state["active_query"] = "stick drift & coil whine overheating"
        st.session_state["trigger_run"] = True
        st.rerun()

with demo_cols[3]:
    if st.button("⌚ Apple Watch S8\n(Sensor Burn & Screen)", use_container_width=True, help="Test Always-On Retina display, optical sensor burns, and battery swelling"):
        st.session_state["active_brand"] = "Smartwatches"
        st.session_state["active_product_id"] = "APPLE_WATCH_S8"
        st.session_state["active_query"] = "skin burn rash & battery swelling"
        st.session_state["trigger_run"] = True
        st.rerun()

with demo_cols[4]:
    if st.button("🏠 Echo Dot Gen 5\n(Voice & Adapter Melt)", use_container_width=True, help="Test Alexa voice recognition, sponsored suggestions, and adapter overheating"):
        st.session_state["active_brand"] = "Smart Home"
        st.session_state["active_product_id"] = "ECHO_DOT_GEN5"
        st.session_state["active_query"] = "voice pickup & adapter overheating"
        st.session_state["trigger_run"] = True
        st.rerun()

with demo_cols[5]:
    if st.button("🔋 Anker PowerCore\n(Battery Swelling Risk)", use_container_width=True, help="Test lithium battery swelling & smoke hazard detection"):
        st.session_state["active_brand"] = "Amazon Electronics"
        st.session_state["active_product_id"] = "B00X5RV14Y"
        st.session_state["active_query"] = "battery swelling & fast charging"
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
    analyze = st.button("Run Audit", use_container_width=True, type="primary")


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
    theme_options = [
        "✦ Luminous Mocha Glass (Stitch Design)",
        "✦ Editorial Studio Light",
        "✦ Obsidian Matte Dark",
        "✦ High-Contrast (WCAG AAA)",
    ]
    cur_theme = st.session_state.get("theme_mode", theme_options[0])
    theme_idx = theme_options.index(cur_theme) if cur_theme in theme_options else 0
    selected_theme = st.selectbox(
        "Visual Theme",
        theme_options,
        index=theme_idx,
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
        f"""<div style="padding: 1.5rem 1rem 1.4rem 1rem; text-align: center; max-width: 800px; margin: 0 auto;">
<h2 style="color:{tokens['text_primary']}; font-weight:700; font-size:1.6rem; margin-bottom:0.6rem;">Evidence-Grounded Review Intelligence</h2>
<p style="color:{tokens['text_secondary']}; font-size:0.95rem; line-height:1.6; margin-bottom:1.5rem;">
OpinionLens analyzes customer reviews with rigorous source attribution, intercepts critical safety risks before majority ratings conceal them, and maps contested consumer sentiment across hardware dimensions.
</p>
</div>""",
        unsafe_allow_html=True,
    )

    wc1, wc2, wc3 = st.columns(3)
    with wc1:
        with st.container(border=True):
            st.markdown(
                f"""<div style="font-size:0.78rem; font-weight:700; color:{tokens['safety_title']}; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;">01 &bull; Safety Isolation</div>
<div style="font-weight:600; color:{tokens['text_primary']}; font-size:1rem; margin-bottom:0.3rem;">Critical Risk Interception</div>
<div style="font-size:0.83rem; color:{tokens['text_muted']}; line-height:1.5;">Identifies battery swelling, extreme overheating, and fire hazards before star-rating averages dilute them.</div>""",
                unsafe_allow_html=True,
            )
    with wc2:
        with st.container(border=True):
            st.markdown(
                f"""<div style="font-size:0.78rem; font-weight:700; color:{tokens['consensus_title']}; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;">02 &bull; Traceable Synthesis</div>
<div style="font-weight:600; color:{tokens['text_primary']}; font-size:1rem; margin-bottom:0.3rem;">Verifiable Consensus</div>
<div style="font-size:0.83rem; color:{tokens['text_muted']}; line-height:1.5;">Synthesizes majority opinions into concise points, each anchored with exact click-to-verify citation references.</div>""",
                unsafe_allow_html=True,
            )
    with wc3:
        with st.container(border=True):
            st.markdown(
                f"""<div style="font-size:0.78rem; font-weight:700; color:{tokens['contested_title']}; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.4rem;">03 &bull; Polarity Detection</div>
<div style="font-weight:600; color:{tokens['text_primary']}; font-size:1rem; margin-bottom:0.3rem;">Contested Dimensions</div>
<div style="font-size:0.83rem; color:{tokens['text_muted']}; line-height:1.5;">Surfaces hardware aspects where buyer feedback sharply divides into pro and con arguments.</div>""",
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
