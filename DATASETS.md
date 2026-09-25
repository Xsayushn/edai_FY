# 📚 OpinionLens — Datasets, Accessibility & Integration Guide

This guide details the datasets used in OpinionLens, how to download and connect additional datasets, and how the accessibility architecture works.

---

## 1. Primary Datasets Used

### A. Mendeley Mobile Phone Reviews Dataset (Baseline)
- **DOI / URL:** [10.17632/wzxkx2kr6n.1](https://data.mendeley.com/datasets/wzxkx2kr6n/1)
- **Author:** Aijaz Sheikh (2021)
- **Total Reviews:** 200,773 verified e-commerce reviews
- **Brands Covered (10 total):**
  1. `samsung.csv` (*Added in this release*)
  2. `iphone.csv`
  3. `lenova.csv` (*Default demo model: Lenovo A6000 Plus*)
  4. `moto.csv`
  5. `nokia.csv`
  6. `redmi.csv`
  7. `micromax.csv`
  8. `panasonic.csv`
  9. `oppo.csv`
  10. `vivo.csv`
- **Fields:** `[reviewer_name, reviewer_id, product_name, product_id, rating, review_title, review_text, helpful_votes, total_votes, date]`

### B. Amazon Electronics Dataset (Cross-Domain Expansion)
- **File:** `dataset/amazon_electronics.csv`
- **Products:**
  - *Anker PowerCore 20100mAh Portable Charger* (`B00X5RV14Y`)
  - Discussion of charging capacity, fast charging, heavy build.
  - **Safety-Critical Hazards:** Real consumer reports of battery swelling, casing split, and port smoke during recharging.

---

## 2. Recommended External Datasets for Further Scaling

| Dataset Name | Source | Description | URL |
|---|---|---|---|
| **Amazon Reviews 2023** | McAuley Lab (UCSD) | Millions of modern electronics and smart device reviews with verified purchase tags. | [Hugging Face](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) |
| **Amazon Mobile Electronics** | Hugging Face (`rkf2778`) | 30k+ reviews focusing on mobile accessories, chargers, and audio gear. | [Hugging Face](https://huggingface.co/datasets/rkf2778/amazon_reviews_mobile_electronics) |
| **Amazon Cell Phones** | Kaggle (PromptCloud) | 67,000+ reviews across 400+ unlocked smartphone models. | [Kaggle](https://www.kaggle.com/datasets/promptcloud/amazon-cell-phones-reviews) |
| **Multilingual Amazon (MARC)**| Amazon / Hugging Face | 1.2M reviews in English, Spanish, German, French, Japanese, and Chinese. | [Hugging Face](https://huggingface.co/datasets/amazon_reviews_multi) |
| **CPSC Product Recalls** | US CPSC Open Data | Official government recall reports for lithium battery fires and hazard benchmarks. | [CPSC.gov](https://www.cpsc.gov/Recalls) |

---

## 3. Universal Dataset Ingestion

OpinionLens features a **Universal Schema Adapter** (`dataset_loader.py`). It automatically detects:
- File format (CSV, JSON)
- Header presence (works with both legacy headerless CSVs and modern titled CSVs)
- Encoding (`UTF-8`, `Latin-1`, `UTF-8-SIG`, `CP1252`)
- Fuzzy column mapping (`reviewText` -> `review_text`, `overall` -> `rating`, `asin` -> `product_id`)

### Drag & Drop via Web UI
1. Launch the app (`streamlit run app.py`).
2. Open the sidebar and click **"📤 Connect / Upload Dataset"**.
3. Drop in any CSV or JSON review file.
4. Click **"Use Uploaded Dataset Now"** to immediately index and analyze your custom data!

---

## 4. Accessibility Architecture (WCAG 2.1 & Inclusive AI)

OpinionLens is designed for universal accessibility:

1. **🔊 Audio Voice Briefing (Text-to-Speech)**:
   - Uses the browser's native **HTML5 SpeechSynthesis API**.
   - With 1 click, visually impaired or auditory-learning users can listen to a spoken synthesis of Critical Safety Alerts and Executive Consensus summaries.

2. **👁️ High-Contrast Mode (WCAG AAA)**:
   - Sidebar toggle enhances border contrast (sharp 2px boundaries), high-legibility status colors, and dark-background contrast ratios exceeding 7:1.

3. **🔤 Dynamic Text Scaling**:
   - 120% scale mode for enhanced readability.

4. **🛡️ Zero-API Local Mode (100% Free / Offline)**:
   - No Groq API key or internet access required.
   - Uses local heuristic opinion extraction and deterministic evidence synthesis on CPU.

5. **📥 Audit Report Exporters**:
   - Download the full cited analysis as **Markdown (`.md`)** or **Structured JSON (`.json`)**.
