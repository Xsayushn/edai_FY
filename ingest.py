"""
ingest.py — Load a product's reviews from a CSV and index them into ChromaDB.

Usage (CLI):
    python ingest.py --csv lenova.csv --product_id MOBE7JXXKS6PWW2C

Usage (API):
    from ingest import ingest_product, list_products_in_csv
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_PREFIX,
    CSV_COLUMNS,
    CSV_ENCODING,
    DATASET_DIR,
    DEFAULT_CSV,
    DEFAULT_PRODUCT_ID,
    EMBEDDING_MODEL,
    MAX_REVIEWS_PER_PRODUCT,
    MIN_REVIEWS_FOR_PRODUCT,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

from dataset_loader import load_universal_dataset, list_products_from_df


def _clean_text(raw: str) -> str:
    """Strip Flipkart boilerplate and normalise whitespace."""
    if not isinstance(raw, str):
        return ""
    text = re.sub(r"\s*READ MORE\s*", " ", raw, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_csv(csv_source: Path | str | pd.DataFrame) -> pd.DataFrame:
    """Load any review dataset (headerless or with headers) and return a tidy DataFrame."""
    if isinstance(csv_source, pd.DataFrame):
        return csv_source
    return load_universal_dataset(csv_source)


def list_products_in_csv(csv_source: Path | str | pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with (product_id, product_name, review_count) sorted by count."""
    df = load_csv(csv_source)
    return list_products_from_df(df)


def list_all_brands() -> dict[str, Path]:
    """Scan DATASET_DIR and return {brand_label: csv_path} for every CSV found."""
    brands: dict[str, Path] = {}
    for p in sorted(DATASET_DIR.glob("*.csv")):
        label = p.stem.replace("_", " ").title()
        brands[label] = p
    return brands


# ---------------------------------------------------------------------------
# ChromaDB helpers
# ---------------------------------------------------------------------------

def _get_client() -> chromadb.PersistentClient:
    # Ensure the directory exists before ChromaDB tries to open its SQLite file.
    # On Windows, PersistentClient raises "Could not connect to tenant default_tenant"
    # if the path doesn't exist yet instead of creating it automatically.
    Path(CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)


def _collection_name(product_id: str) -> str:
    # ChromaDB collection names must be 3-63 chars, alphanumeric + hyphens/underscores
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", product_id)
    return f"{CHROMA_COLLECTION_PREFIX}{safe}"


def is_already_ingested(product_id: str) -> bool:
    """Return True if the collection exists and has at least one document."""
    try:
        client = _get_client()
        cname = _collection_name(product_id)
        col = client.get_collection(cname)
        return col.count() > 0
    except Exception:
        # DB not yet initialised, collection missing, or any other startup error.
        return False


# ---------------------------------------------------------------------------
# Main ingestion function
# ---------------------------------------------------------------------------

def ingest_product(
    csv_path: Path | str | pd.DataFrame,
    product_id: str,
    max_reviews: int = MAX_REVIEWS_PER_PRODUCT,
    force: bool = False,
    progress_callback=None,
) -> int:
    """
    Embed and store reviews for *product_id* from *csv_path* (or DataFrame) into ChromaDB.

    Args:
        csv_path:          Path to the brand CSV, or a pandas DataFrame.
        product_id:        The product ID to filter on.
        max_reviews:       Cap on number of reviews to index.
        force:             If True, delete existing collection and re-ingest.
        progress_callback: Optional callable(pct: float, msg: str) for Streamlit progress.

    Returns:
        Number of documents indexed.
    """
    cname = _collection_name(product_id)
    client = _get_client()

    # --- Idempotency check --------------------------------------------------
    if not force and is_already_ingested(product_id):
        col = client.get_collection(cname)
        count = col.count()
        print(f"[ingest] Collection '{cname}' already has {count} docs. Skipping re-ingest.")
        return count

    # --- Load & filter data -------------------------------------------------
    if progress_callback:
        progress_callback(0.05, "Loading dataset…")

    df = load_csv(csv_path)
    product_df = df[df["product_id"] == product_id].copy()

    if product_df.empty:
        src_name = getattr(csv_path, "name", "dataset")
        raise ValueError(f"No reviews found for product_id='{product_id}' in {src_name}")

    # Sort by helpful_votes so we keep the most informative reviews when capping
    product_df = product_df.sort_values("helpful_votes", ascending=False).head(max_reviews)
    product_df = product_df.reset_index(drop=True)
    product_df["review_id"] = product_df.index  # 0-indexed integer review_id

    print(f"[ingest] Ingesting {len(product_df)} reviews for product '{product_id}'…")

    # --- Embed ---------------------------------------------------------------
    if progress_callback:
        progress_callback(0.10, f"Loading embedding model ({EMBEDDING_MODEL})…")

    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = product_df["review_text"].tolist()

    if progress_callback:
        progress_callback(0.20, f"Embedding {len(texts)} reviews… (this may take 30-90s on CPU)")

    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    # --- Upsert into ChromaDB -----------------------------------------------
    if progress_callback:
        progress_callback(0.85, "Storing vectors in ChromaDB…")

    # Delete collection if force re-ingest
    if force:
        try:
            client.delete_collection(cname)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=cname,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [str(row["review_id"]) for _, row in product_df.iterrows()]
    metadatas = [
        {
            "review_id": int(row["review_id"]),
            "product_id": str(row["product_id"]),
            "product_name": str(row.get("product_name", "")),
            "rating": int(row["rating"]),
            "date": str(row.get("date", "")),
            "helpful_votes": int(row["helpful_votes"]),
            "review_title": str(row.get("review_title", "")),
        }
        for _, row in product_df.iterrows()
    ]

    collection.upsert(
        ids=ids,
        embeddings=[e.tolist() for e in embeddings],
        documents=texts,
        metadatas=metadatas,
    )

    if progress_callback:
        progress_callback(1.0, "Ingestion complete.")

    count = collection.count()
    print(f"[ingest] Done. Collection '{cname}' now has {count} documents.")
    return count


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _cli():
    parser = argparse.ArgumentParser(description="Ingest product reviews into ChromaDB")
    parser.add_argument("--csv", default=DEFAULT_CSV, help="CSV filename inside dataset/")
    parser.add_argument("--product_id", default=DEFAULT_PRODUCT_ID)
    parser.add_argument("--max_reviews", type=int, default=MAX_REVIEWS_PER_PRODUCT)
    parser.add_argument("--force", action="store_true", help="Re-ingest even if collection exists")
    args = parser.parse_args()

    csv_path = DATASET_DIR / args.csv
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found.", file=sys.stderr)
        sys.exit(1)

    count = ingest_product(csv_path, args.product_id, args.max_reviews, args.force)
    print(f"Indexed {count} documents.")


if __name__ == "__main__":
    _cli()
