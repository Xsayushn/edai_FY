"""
dataset_loader.py — Universal Dataset Adapter for OpinionLens.

Supports:
1. Legacy headerless Mendeley Flipkart CSVs (latin1, 10 positional columns).
2. Standard modern CSVs with headers (UTF-8, custom encodings).
3. Amazon Reviews formats (e.g. reviewText, overall, asin, summary).
4. Kaggle, Trustpilot, and Google Play review formats.
5. In-memory uploaded CSV/JSON files from Streamlit.
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from config import (
    CSV_COLUMNS,
    CSV_ENCODING,
    DATASET_DIR,
    MIN_REVIEWS_FOR_PRODUCT,
)

# Canonical column names used internally across OpinionLens
CANONICAL_COLUMNS = [
    "reviewer_name",
    "reviewer_id",
    "product_name",
    "product_id",
    "rating",
    "review_title",
    "review_text",
    "helpful_votes",
    "total_votes",
    "date",
]

# Fuzzy matching patterns for auto-detecting column mappings
COLUMN_CANDIDATES = {
    "review_text": [
        "review_text", "reviewtext", "review", "text", "body", "content",
        "review_body", "review_content", "comments", "description", "opinion"
    ],
    "rating": [
        "rating", "overall", "stars", "score", "rate", "star_rating",
        "review_rating", "user_rating"
    ],
    "product_id": [
        "product_id", "productid", "asin", "item_id", "itemid", "sku",
        "model_id", "product_code", "id"
    ],
    "product_name": [
        "product_name", "productname", "title", "product_title", "item_name",
        "itemname", "phone_name", "model", "device", "name"
    ],
    "review_title": [
        "review_title", "reviewtitle", "title", "summary", "subject",
        "headline", "short_review"
    ],
    "reviewer_name": [
        "reviewer_name", "reviewername", "author", "user", "username",
        "user_name", "customer_name", "profile_name"
    ],
    "reviewer_id": [
        "reviewer_id", "reviewerid", "user_id", "userid", "customer_id",
        "author_id", "uuid"
    ],
    "date": [
        "date", "review_date", "reviewdate", "timestamp", "time", "created_at",
        "review_time", "posted_at"
    ],
    "helpful_votes": [
        "helpful_votes", "helpfulvotes", "upvotes", "helpful", "likes",
        "vote_count", "thumbs_up"
    ],
    "total_votes": [
        "total_votes", "totalvotes", "votes", "downvotes", "all_votes"
    ],
}


def clean_review_text(raw: Any) -> str:
    """Normalize text: strip HTML, boilerplate ('READ MORE'), extra whitespace."""
    if not isinstance(raw, str):
        return ""
    # Strip HTML tags if any
    text = re.sub(r"<[^>]+>", " ", raw)
    # Strip Flipkart boilerplate
    text = re.sub(r"\s*READ MORE\s*", " ", text, flags=re.IGNORECASE)
    # Strip excessive newlines and whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_encoding(file_source: Union[Path, str, bytes, io.BytesIO]) -> str:
    """Determine the most likely encoding (try UTF-8, UTF-8-SIG, Latin1)."""
    if isinstance(file_source, (str, Path)):
        p = Path(file_source)
        if not p.exists():
            return "utf-8"
        sample = p.read_bytes()[:16384]
    elif isinstance(file_source, bytes):
        sample = file_source[:16384]
    elif hasattr(file_source, "getvalue"):
        sample = file_source.getvalue()[:16384]
    elif hasattr(file_source, "read"):
        pos = file_source.tell() if hasattr(file_source, "tell") else 0
        sample = file_source.read(16384)
        if hasattr(file_source, "seek"):
            file_source.seek(pos)
    else:
        return "utf-8"

    for enc in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
        try:
            sample.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin1"


def detect_schema(df_sample: pd.DataFrame) -> Tuple[bool, Dict[str, str]]:
    """
    Check if a DataFrame has a header and detect column mapping.
    Returns: (has_header: bool, column_map: dict of canonical -> source_col)
    """
    cols = [str(c).strip() for c in df_sample.columns]

    # If columns look like default integers 0, 1, 2... or exactly match length 10 without headers
    is_integer_cols = all(isinstance(c, int) or str(c).isdigit() for c in df_sample.columns)
    first_row = [str(val).lower() for val in df_sample.iloc[0].values] if len(df_sample) > 0 else []

    # Check if first row contains column-like names
    header_keywords = {"product", "review", "rating", "author", "user", "text", "asin", "stars"}
    first_row_matches = any(any(kw in str(val) for kw in header_keywords) for val in first_row)

    if is_integer_cols and not first_row_matches and len(cols) == len(CSV_COLUMNS):
        # Matches original Mendeley Flipkart format
        mapping = {canonical: idx for idx, canonical in enumerate(CSV_COLUMNS)}
        return False, mapping

    # Otherwise, it has headers. Map columns using fuzzy matching.
    mapping = {}
    normalized_source = {re.sub(r"[^a-z0-9]", "", c.lower()): c for c in cols}

    for canonical, candidates in COLUMN_CANDIDATES.items():
        matched_source = None
        for candidate in candidates:
            cand_norm = re.sub(r"[^a-z0-9]", "", candidate.lower())
            if cand_norm in normalized_source:
                matched_source = normalized_source[cand_norm]
                break
        if matched_source:
            mapping[canonical] = matched_source

    return True, mapping


def load_universal_dataset(
    file_source: Union[Path, str, io.BytesIO, bytes],
    column_mapping: Optional[Dict[str, str]] = None,
    encoding: Optional[str] = None,
) -> pd.DataFrame:
    """
    Universal dataset reader. Accepts local paths, byte buffers, or Streamlit UploadedFiles.
    Standardizes DataFrame into CANONICAL_COLUMNS.
    """
    if encoding is None:
        encoding = detect_encoding(file_source)

    # 1. Read raw sample with header=None to inspect row 0
    try:
        sample_df = pd.read_csv(file_source, header=None, nrows=5, encoding=encoding, on_bad_lines="skip")
        if hasattr(file_source, "seek"):
            file_source.seek(0)
    except Exception:
        encoding = "latin1"
        sample_df = pd.read_csv(file_source, header=None, nrows=5, encoding=encoding, on_bad_lines="skip")
        if hasattr(file_source, "seek"):
            file_source.seek(0)

    # Check if first row is actually a header row
    first_row_vals = [str(val).strip() for val in sample_df.iloc[0].values] if len(sample_df) > 0 else []
    
    def _is_header_row(vals):
        if not vals:
            return False
        # If any value is longer than 50 characters, it's a review body, not a column name
        if any(len(str(v)) > 50 for v in vals):
            return False
        # If multiple values are pure numbers, it's a data row
        num_digits = sum(1 for v in vals if str(v).strip().isdigit())
        if num_digits >= 2:
            return False
        kws = {
            "productid", "productname", "reviewtext", "rating", "overall", "asin",
            "stars", "reviewername", "date", "reviewtitle", "text", "title", "review",
            "score", "comments", "itemid"
        }
        return any(re.sub(r"[^a-z0-9]", "", str(v).lower()) in kws for v in vals)

    has_header = _is_header_row(first_row_vals)

    if not has_header and len(sample_df.columns) == 10:
        # Standard Mendeley Flipkart format
        try:
            df = pd.read_csv(
                file_source,
                names=CSV_COLUMNS,
                encoding=encoding,
                on_bad_lines="skip",
            )
        except UnicodeDecodeError:
            df = pd.read_csv(
                file_source,
                names=CSV_COLUMNS,
                encoding="latin1",
                on_bad_lines="skip",
            )
    else:
        # File has headers or custom format
        try:
            raw_df = pd.read_csv(file_source, encoding=encoding, on_bad_lines="skip")
        except UnicodeDecodeError:
            raw_df = pd.read_csv(file_source, encoding="latin1", on_bad_lines="skip")
        _, auto_mapping = detect_schema(raw_df.head(5))
        mapping = column_mapping or auto_mapping

        standardized = pd.DataFrame()
        for canonical in CANONICAL_COLUMNS:
            source_col = mapping.get(canonical)
            if source_col and source_col in raw_df.columns:
                standardized[canonical] = raw_df[source_col]
            else:
                if canonical == "product_id":
                    if "product_name" in mapping and mapping["product_name"] in raw_df.columns:
                        standardized["product_id"] = (
                            raw_df[mapping["product_name"]].astype(str).str[:24].str.replace(r"\W+", "_", regex=True)
                        )
                    else:
                        standardized["product_id"] = "DEFAULT_PROD_1"
                elif canonical == "product_name":
                    standardized["product_name"] = standardized.get("product_id", "General Product")
                elif canonical == "rating":
                    standardized["rating"] = 3
                elif canonical == "helpful_votes":
                    standardized["helpful_votes"] = 0
                elif canonical == "total_votes":
                    standardized["total_votes"] = 0
                elif canonical == "review_title":
                    standardized["review_title"] = ""
                elif canonical == "reviewer_name":
                    standardized["reviewer_name"] = "Anonymous Reviewer"
                elif canonical == "reviewer_id":
                    standardized["reviewer_id"] = [f"user_{i}" for i in range(len(raw_df))]
                elif canonical == "date":
                    standardized["date"] = "Recent"
                else:
                    standardized[canonical] = ""

        df = standardized

    # Ensure required columns are present and clean
    df = df.dropna(subset=["product_id", "review_text"])
    df["review_text"] = df["review_text"].apply(clean_review_text)
    df = df[df["review_text"].str.len() > 10]

    # Coerce numeric types
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(3).astype(int)
    # Clip ratings between 1 and 5
    df["rating"] = df["rating"].clip(1, 5)
    df["helpful_votes"] = pd.to_numeric(df["helpful_votes"], errors="coerce").fillna(0).astype(int)
    df["total_votes"] = pd.to_numeric(df["total_votes"], errors="coerce").fillna(0).astype(int)

    return df.reset_index(drop=True)


def list_products_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return products with counts sorted descending."""
    counts = (
        df.groupby(["product_id", "product_name"])
        .size()
        .reset_index(name="review_count")
        .sort_values("review_count", ascending=False)
    )
    # If filtered results empty, lower threshold
    filtered = counts[counts["review_count"] >= MIN_REVIEWS_FOR_PRODUCT].reset_index(drop=True)
    if filtered.empty and not counts.empty:
        # Fall back to minimum of 5 reviews so small/custom datasets still work!
        filtered = counts[counts["review_count"] >= 5].reset_index(drop=True)
        if filtered.empty:
            filtered = counts.reset_index(drop=True)
    return filtered


def get_curated_dataset_catalog() -> List[Dict[str, Any]]:
    """
    Catalog of complementary open-access product review datasets.
    """
    return [
        {
            "name": "Mendeley Mobile Phone Reviews (Current Baseline)",
            "source": "Mendeley Data (Sheikh, 2021)",
            "url": "https://data.mendeley.com/datasets/wzxkx2kr6n/1",
            "doi": "10.17632/wzxkx2kr6n.1",
            "size": "200,773 reviews · 10 brands",
            "brands": ["Samsung", "Apple/iPhone", "Lenovo", "Motorola", "Nokia", "Redmi", "Micromax", "Panasonic", "Oppo", "Vivo"],
            "features": "Real Flipkart verified reviews, star ratings, upvotes/downvotes, dates.",
            "description": "Baseline dataset used in OpinionLens, containing reviews across 10 major mobile smartphone manufacturers.",
            "format": "Raw CSV, no headers, Latin-1 encoding.",
        },
        {
            "name": "Amazon Reviews 2023 (McAuley Lab / UCSD)",
            "source": "Hugging Face / McAuley Lab",
            "url": "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023",
            "size": "Millions of reviews across Electronics & Cell Phones",
            "brands": ["Anker", "Apple", "Samsung", "Sony", "Google Pixel", "Belkin"],
            "features": "ASIN, verified purchase badges, timestamp, helpful votes, rich text.",
            "description": "Comprehensive modern e-commerce review corpus. Crucial for detecting battery swelling, overheating chargers, counterfeit items, and fire safety warnings.",
            "format": "JSONL / Parquet / CSV with standard headers.",
        },
        {
            "name": "Amazon Mobile Electronics Reviews (Hugging Face)",
            "source": "Hugging Face (rkf2778)",
            "url": "https://huggingface.co/datasets/rkf2778/amazon_reviews_mobile_electronics",
            "size": "30,000+ reviews",
            "brands": ["Accessories", "Chargers", "Wireless Earbuds", "Phone Cases", "Cables"],
            "features": "Directly accessible via Hugging Face `load_dataset()`. Pre-cleaned.",
            "description": "Focused mobile electronics collection with high frequency of thermal, charging, and accessory quality reports.",
            "format": "HuggingFace Datasets API / CSV export.",
        },
        {
            "name": "Amazon Cell Phones & Accessories (Kaggle)",
            "source": "Kaggle (PromptCloud)",
            "url": "https://www.kaggle.com/datasets/promptcloud/amazon-cell-phones-reviews",
            "size": "67,986 reviews · 400+ phone models",
            "brands": ["Apple", "Samsung", "Motorola", "BLU", "LG", "Huawei", "OnePlus"],
            "features": "Item title, ASIN, verified reviews, price, ratings.",
            "description": "Curated phone reviews with diverse international models, carrier unlocks, and battery life discussions.",
            "format": "CSV with headers, UTF-8.",
        },
        {
            "name": "The Multilingual Amazon Reviews Corpus (MARC)",
            "source": "Amazon / Hugging Face (amazon_reviews_multi)",
            "url": "https://huggingface.co/datasets/amazon_reviews_multi",
            "size": "1.2 Million reviews in 6 languages",
            "brands": ["Global Consumer Electronics"],
            "features": "English, Spanish, German, French, Japanese, Chinese.",
            "description": "Ideal for extending OpinionLens accessibility to non-English languages and global markets.",
            "format": "JSON / HuggingFace Dataset.",
        },
        {
            "name": "Consumer Product Safety Commission (CPSC) Recalls & Reports",
            "source": "CPSC Open Data",
            "url": "https://www.cpsc.gov/Recalls",
            "size": "Official safety recall incidents",
            "brands": ["Lithium-Ion Devices, Chargers, Appliances"],
            "features": "Official hazard descriptions, injury reports, incident counts.",
            "description": "Benchmark ground-truth dataset to validate and evaluate OpinionLens's Critical-Minority Safety Guard.",
            "format": "JSON / CSV REST API.",
        }
    ]
