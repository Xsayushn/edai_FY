# 🔍 OpinionLens — Explainable & Safe RAG for Opinion Summarization

> A production-quality Retrieval-Augmented Generation (RAG) pipeline over e-commerce product reviews with two core novelty features: a **Critical-Minority Safety Guard** and **Attributed Evidence Mapping**.

---

## 📌 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Novelty Features](#2-novelty-features)
3. [Tech Stack](#3-tech-stack)
4. [Models Used](#4-models-used)
5. [System Architecture](#5-system-architecture)
6. [Pipeline Workflow](#6-pipeline-workflow)
7. [File Structure](#7-file-structure)
8. [Dataset](#8-dataset)
9. [Setup & Installation](#9-setup--installation)
10. [How to Run](#10-how-to-run)
11. [UI Walkthrough](#11-ui-walkthrough)
12. [Sample Output](#12-sample-output)
13. [Configuration Reference](#13-configuration-reference)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Project Overview

OpinionLens is an **Explainable AI** system that summarizes product reviews using a Retrieval-Augmented Generation (RAG) pipeline. Unlike conventional summarizers that simply average sentiment, it:

- **Forces safety-critical minority opinions** (e.g., 3 users reporting "overheating") to the top — preventing 500 five-star ratings from burying a dangerous complaint.
- **Cites every factual claim** with the exact source review and verbatim quote — enabling full traceability of any generated statement.
- **Detects polarized aspects** where users are genuinely split and presents them as contested rather than smoothing them over.

**Target use case:** Product teams, consumers, and auditors who need trustworthy, evidence-backed review summaries rather than black-box sentiment scores.

---

## 2. Novelty Features

### 🚨 Feature 1 — Critical-Minority Safety Guard

Standard RAG averages all reviews. OpinionLens intercepts before summarization:

```
Standard RAG:  [★★★★★ × 400] + [★ × 3 "battery exploded"] → "Users love this product"
OpinionLens:   Same input → 🚨 CRITICAL ALERT: "Battery explosion" (3 reviews) + normal summary
```

**How it works:**
1. Every extracted opinion tuple is scanned against a `RISK_TAXONOMY` (9 terms: overheating, burn, battery explosion, swelling, electric shock, fire, smoke, counterfeit, fraud).
2. Two detection stages: **substring match** (fast, exact) then **semantic cosine similarity** (catches paraphrases, threshold 0.75).
3. Guard rule: if ≥ 2 distinct reviews mention the same risk term → emit a `CRITICAL_ALERT` that is **always shown first**, bypassing standard frequency thresholds.

### 🔎 Feature 2 — Attributed Evidence Mapping

Every sentence in the generated summary ends with `[Review #ID]` citation tags. Clicking any tag in the UI loads the full source review with the **exact matching quote highlighted in amber**. Every claim is:
- Traceable to a real review
- Verifiable with the verbatim text
- Inspectable without leaving the app

---

## 3. Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.10+ |
| Frontend / UI | Streamlit | >= 1.35 |
| Vector Database | ChromaDB (local persistent) | >= 0.5.0 |
| LLM Provider | Groq API | >= 0.9.0 |
| Data Validation | Pydantic v2 | >= 2.7.0 |
| Charting | Plotly | >= 5.20.0 |
| Data Loading | Pandas | >= 2.0.0 |
| Environment | python-dotenv | >= 1.0.0 |

---

## 4. Models Used

### Embedding Model — `BAAI/bge-small-en-v1.5`
- **Purpose:** Convert review text into 384-dimensional dense vectors for semantic search.
- **Why this model:** State-of-the-art retrieval performance at a small footprint (33M parameters, ~130MB download). Runs on CPU in 30-90 seconds for 500 reviews. Hosted on HuggingFace, downloaded automatically on first use.
- **Used in:** `ingest.py` (indexing), `retriever.py` (query embedding), `guard.py` (semantic risk detection).

### LLM — `qwen/qwen3.8-27b` via Groq API
- **Purpose:** (1) Extract structured aspect-sentiment tuples from review text. (2) Generate a cited narrative summary from evidence clusters.
- **Why Groq:** Ultra-low latency inference (typically < 3s per call) via their LPU hardware. Free tier available.
- **Why Qwen 3.8-27b:** Available on the Groq free tier with strong instruction-following for JSON schema output.
- **Used in:** `extractor.py` — both extraction and summary generation steps.

---

## 5. System Architecture

```
+-----------------------------------------------------------------------+
|                         STREAMLIT UI (app.py)                         |
|  [Brand v] [Product v] [Query Input] [Analyze]                        |
|  +------------------------------+  +--------------------------------+  |
|  |  LEFT PANEL (60%)            |  |  RIGHT PANEL (40%)             |  |
|  |  Safety Warnings             |  |  Evidence Inspector            |  |
|  |  Consensus Summary           |  |  (click citation to see review)|  |
|  |  Contested Viewpoints        |  |                                |  |
|  +------------------------------+  +--------------------------------+  |
+-----------------------------------+-----------------------------------+
                                    | triggers
+-----------------------------------v-----------------------------------+
|                          PIPELINE ENGINE                              |
|                                                                       |
|  CSV Files --> ingest.py --> ChromaDB (chroma_db/)                   |
|                                   |                                   |
|                             retriever.py <-- Query                   |
|                                   |                                   |
|                             extractor.py <-- Groq LLM               |
|                           (AspectTuples)                              |
|                                   |                                   |
|              +--------------------+--------------------+             |
|              v                    v                    v             |
|         guard.py          aggregator.py         extractor.py        |
|       (Safety Guard)      (Contention)        (Summary Gen.)        |
+-----------------------------------------------------------------------+
```

---

## 6. Pipeline Workflow

The pipeline runs in 6 sequential steps when you click **Analyze**:

**Step 1 — INGESTION** *(first-time only, ~30-90s)*
```
CSV file --> filter by product_id --> clean text (strip "READ MORE" boilerplate)
--> embed with bge-small-en-v1.5 --> upsert into ChromaDB
Idempotent: skipped automatically if collection already exists.
```

**Step 2 — RETRIEVAL**
```
Mode A (blank query, "balanced"):
  Fetch top-15 reviews rated 4-5 stars + top-15 rated 1-2 stars from ChromaDB

Mode B (typed query, "aspect"):
  Embed the query --> cosine similarity search --> top-25 closest reviews
```

**Step 3 — ASPECT-SENTIMENT EXTRACTION** *(LLM)*
```
Retrieved reviews --> Groq LLM (batches of 10 reviews)
--> JSON output parsed by Pydantic into AspectTuple objects:
  { aspect, sentiment, summary_claim, quote, review_id }
```

**Step 4 — SAFETY GUARD**
```
All tuples --> substring scan vs RISK_TAXONOMY
           --> (if no match) semantic similarity with bge embeddings
If risk appears in >= 2 reviews --> CriticalAlert emitted
```

**Step 5 — AGGREGATION**
```
Tuples grouped by normalized aspect name
For each group: count pos/neg, compute contention ratio:
  ratio = min(N_pos, N_neg) / max(N_pos, N_neg)
If N_total >= 4 AND ratio >= 0.4 --> tagged CONTESTED
```

**Step 6 — ATTRIBUTED SUMMARY GENERATION** *(LLM)*
```
Evidence payload (capped at 5,000 chars) --> Groq LLM
--> JSON output: { consensus_points, contested_aspects, safety_alerts }
Every claim must cite [Review #ID]. Falls back to rule-based summary on API failure.
```

---

## 7. File Structure

```
project/
|
+-- app.py              # Streamlit UI — all rendering and user interaction
+-- ingest.py           # CSV loading, embedding, ChromaDB ingestion
+-- retriever.py        # ChromaDB query layer (aspect & balanced modes)
+-- extractor.py        # Groq LLM client, extraction, summary generation
+-- guard.py            # Critical-Minority Safety Guard
+-- aggregator.py       # Aspect clustering + contention ratio detection
+-- config.py           # All constants: paths, thresholds, model names
|
+-- requirements.txt    # Python dependencies with compatible version bounds
+-- .env.example        # Template for environment variables
+-- .env                # Your actual secrets (DO NOT commit to git)
|
+-- dataset/            # Raw CSV files (one per brand)
|   +-- lenova.csv
|   +-- iphone.csv
|   +-- moto.csv
|   +-- ... (9 CSVs total)
|
+-- chroma_db/          # Auto-created on first ingestion; persistent vector store
```

---

## 8. Dataset

**Source:** Mendeley Mobile Phone Reviews dataset — product reviews scraped from Flipkart.

| File | Brand | ~Reviews |
|---|---|---|
| `lenova.csv` | Lenovo | 26,600 |
| `moto.csv` | Motorola | ~36,000 |
| `iphone.csv` | Apple | ~9,000 |
| `nokia.csv` | Nokia | ~20,000 |
| `redmi.csv` | Redmi/Xiaomi | ~16,000 |
| `micromax.csv` | Micromax | ~14,000 |
| `panasonic.csv` | Panasonic | ~12,000 |
| `oppo.csv` | OPPO | ~5,700 |
| `vivo.csv` | Vivo | ~4,200 |

**CSV Format (no header row — columns assigned by position):**

| Col | Field | Notes |
|---|---|---|
| 0 | reviewer_name | |
| 1 | reviewer_id | MD5 hash |
| 2 | product_name | e.g., "Lenovo A6000 Plus (Red, 16 GB)" |
| 3 | product_id | e.g., "MOBE7JXXKS6PWW2C" |
| 4 | rating | 1-5 integer |
| 5 | review_title | Short title |
| 6 | review_text | Full review body |
| 7 | helpful_votes | Integer |
| 8 | total_votes | Integer |
| 9 | date | e.g., "18-Sep-16" |

**Default product for demo:** Lenovo A6000 Plus (`MOBE7JXXKS6PWW2C`) — 970 reviews.

---

## 9. Setup & Installation

### Prerequisites
- Python **3.10 or higher**
- A **Groq API key** (free at https://console.groq.com)
- ~500MB disk space (embedding model cache + ChromaDB)

### Step 1 — Navigate to the project folder
```bash
cd c:\sem7\EDI\project
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

> On first run, sentence-transformers will download BAAI/bge-small-en-v1.5 (~130MB) automatically.

### Step 3 — Configure your API key
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and add your key:
```
GROQ_API_KEY=gsk_your_key_here
```

Get a free Groq key at: **https://console.groq.com/keys**

### Step 4 — (Optional) Pre-ingest a product via CLI
```bash
python ingest.py --csv lenova.csv --product_id MOBE7JXXKS6PWW2C
```

CLI options:
```
--csv          CSV filename inside dataset/  (default: lenova.csv)
--product_id   Product ID to index          (default: MOBE7JXXKS6PWW2C)
--max_reviews  Cap on reviews to embed      (default: 500)
--force        Re-ingest even if already indexed
```

---

## 10. How to Run

```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

### First Run Timeline

| Time | What is happening |
|---|---|
| 0-5s | App loads, ChromaDB directory created |
| 5-10s | Click Analyze — pipeline starts |
| 10-90s | First-time only: downloading bge model + embedding 500 reviews |
| 90-120s | LLM extraction via Groq API (batches of 10 reviews) |
| 120-130s | Safety guard + aggregation + summary generation |

> Second run onwards: ingestion is skipped — total time drops to ~15-30 seconds.

### Query Modes

| Query input | Mode | What gets retrieved |
|---|---|---|
| *(blank)* | balanced | 15 highest-rated + 15 lowest-rated reviews |
| "battery heating" | aspect | Top-25 semantically similar to that phrase |
| "camera quality" | aspect | Top-25 reviews about cameras |
| "overall" | balanced | Same as blank |

---

## 11. UI Walkthrough

**Top Bar:** Brand/CSV selector → Product Model selector → Query input → Analyze button

**Left Panel (60% width):**
- 🚨 **Critical Safety Warnings** (red box) — only shown if safety guard fires; animated pulse badge; Inspect button loads evidence
- ✅ **Consensus Summary** (green box) — 3-5 cited bullet points; each has a 🔎 inspect button; citation chips (#12, #45) are clickable
- ⚖️ **Contested Viewpoints** (amber box) — diverging bar chart (positive vs negative per aspect); pro/con claims with citations

**Right Panel (40% width):**
- 🔎 **Evidence Inspector** — click any 🔎 button or citation chip to load source review here; matching quote highlighted in amber; reviewer metadata shown (stars, date, helpful votes)

**Sidebar (☰):**
- Index status: Ready / Not yet ingested
- Re-ingest button (force refresh)
- Pipeline step reference

---

## 12. Sample Output

### Consensus Summary
```
* Battery life is excellent, lasting a full day under moderate use [Review #12, #34]
* Performance is smooth for everyday tasks but struggles under heavy load [Review #7]
* Build quality feels premium with a sturdy frame [Review #23, #56]
* Camera delivers good daylight shots but underperforms in low light [Review #4, #19]
```

### Safety Alert
```
CRITICAL — Overheating
Detected in 4 reviews (#2, #15, #33, #67)
"the phone is overheating after 10 mins of use"
"device gets dangerously hot while charging"
```

### Contested Aspect
```
Camera Quality — 8 positive vs 6 negative (contention 75%)
PRO: "Photos are crisp and vibrant" [#3, #18]
CON: "Blurry images in low light, disappointing" [#9, #44]
```

---

## 13. Configuration Reference

All tuneable parameters live in `config.py`:

| Constant | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | HuggingFace embedding model |
| `GROQ_MODEL` | `qwen/qwen3.8-27b` | LLM for extraction and summary |
| `MAX_REVIEWS_PER_PRODUCT` | `500` | Cap on reviews ingested per product |
| `TOP_K_ASPECT` | `25` | Reviews retrieved in aspect mode |
| `TOP_K_PER_BUCKET` | `15` | Reviews per rating bucket (balanced mode) |
| `EXTRACTION_BATCH_SIZE` | `10` | Reviews per LLM extraction call |
| `RISK_TAXONOMY` | 9 terms | List of critical risk keywords |
| `CRITICAL_ALERT_MIN_REVIEWS` | `2` | Min reviews to emit a safety alert |
| `RISK_SEMANTIC_THRESHOLD` | `0.75` | Cosine similarity for semantic risk match |
| `CONTESTED_MIN_TOTAL` | `4` | Min tuples to assess an aspect for contention |
| `CONTESTED_MIN_RATIO` | `0.4` | Contention ratio threshold |

---

## 14. Troubleshooting

**`Could not connect to tenant default_tenant`**
ChromaDB does not auto-create its directory on Windows. Fixed in the code via `Path(CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)`. If you see this, ensure you are on the latest version.

**`GROQ_API_KEY is not set`**
- Ensure `.env` (not `.env.example`) exists in the project root.
- File must contain: `GROQ_API_KEY=gsk_...`
- Note: Groq only shows the full key once at creation. If you missed it, generate a new one at console.groq.com/keys.

**`model_not_found` for `llama-3.3-70b-versatile`**
That model requires a paid Groq plan. The project uses `qwen/qwen3.8-27b` by default (free tier). Check available models:
```python
from groq import Groq
client = Groq()
print([m.id for m in client.models.list().data])
```

**Summary generation failed in the UI**
The LLM call failed — the rule-based fallback summary is shown. Common causes:
- Groq rate limit (free tier: ~30 req/min) — wait 60s and retry
- Check the Streamlit terminal for the exact error message

**HuggingFace symlink warning on Windows**
This is harmless. Suppress it by adding to `.env`:
```
HF_HUB_DISABLE_SYMLINKS_WARNING=1
```

**Re-ingesting a product from scratch**
```bash
python ingest.py --csv lenova.csv --product_id MOBE7JXXKS6PWW2C --force
```
Or use the Re-ingest button in the sidebar.

---

*For academic / educational use. Dataset sourced from Mendeley Data.*
