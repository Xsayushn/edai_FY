"""
retriever.py — ChromaDB query layer.

Two retrieval modes:
  1. aspect  — semantic vector search for a specific query string.
  2. balanced — top-K from low-rated AND top-K from high-rated buckets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_PREFIX,
    EMBEDDING_MODEL,
    TOP_K_ASPECT,
    TOP_K_PER_BUCKET,
)
from ingest import _collection_name


# Singleton model & client (loaded once per process)
_model: SentenceTransformer | None = None
_client: chromadb.PersistentClient | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        # Ensure directory exists before ChromaDB opens its SQLite file (Windows fix)
        Path(CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _client


def _result_to_docs(results: dict) -> list[dict]:
    """Flatten ChromaDB query results into a list of doc dicts."""
    docs = []
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    for doc_id, text, meta in zip(ids, documents, metadatas):
        docs.append(
            {
                "review_id": int(meta.get("review_id", doc_id)),
                "review_text": text,
                "rating": int(meta.get("rating", 3)),
                "date": str(meta.get("date", "")),
                "helpful_votes": int(meta.get("helpful_votes", 0)),
                "review_title": str(meta.get("review_title", "")),
                "product_name": str(meta.get("product_name", "")),
            }
        )
    return docs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def retrieve_opinions(
    product_id: str,
    query: str,
    top_k: int = TOP_K_ASPECT,
    mode: Literal["aspect", "balanced"] = "aspect",
) -> list[dict]:
    """
    Retrieve reviews for *product_id* from ChromaDB.

    Args:
        product_id: The product to query.
        query:      Natural-language query (used in 'aspect' mode).
        top_k:      Number of results to return.
        mode:       'aspect' for semantic search, 'balanced' for rating-bucket sampling.

    Returns:
        List of review dicts with keys: review_id, review_text, rating, date,
        helpful_votes, review_title, product_name.
    """
    client = _get_client()
    cname = _collection_name(product_id)

    try:
        collection = client.get_collection(cname)
    except Exception as exc:
        raise RuntimeError(
            f"Collection for product_id='{product_id}' not found. "
            "Run ingest_product() first."
        ) from exc

    if mode == "balanced":
        return _retrieve_balanced(collection, top_k_per_bucket=TOP_K_PER_BUCKET)

    # --- Aspect / semantic mode --------------------------------------------
    model = _get_model()
    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    return _result_to_docs(results)


def _retrieve_balanced(collection, top_k_per_bucket: int) -> list[dict]:
    """
    Fetch up to *top_k_per_bucket* reviews from negative (1-2 stars) and
    positive (4-5 stars) rating buckets separately, then merge.
    """
    total = collection.count()
    all_docs: list[dict] = []

    for rating_range, label in [
        ([1, 2], "negative"),
        ([4, 5], "positive"),
    ]:
        try:
            results = collection.get(
                where={"rating": {"$in": rating_range}},
                limit=min(top_k_per_bucket, total),
                include=["documents", "metadatas"],
            )
            # .get() returns a flat dict, not nested lists
            ids = results.get("ids", [])
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])
            for doc_id, text, meta in zip(ids, documents, metadatas):
                all_docs.append(
                    {
                        "review_id": int(meta.get("review_id", doc_id)),
                        "review_text": text,
                        "rating": int(meta.get("rating", 3)),
                        "date": str(meta.get("date", "")),
                        "helpful_votes": int(meta.get("helpful_votes", 0)),
                        "review_title": str(meta.get("review_title", "")),
                        "product_name": str(meta.get("product_name", "")),
                    }
                )
        except Exception as e:
            print(f"[retriever] Warning: could not fetch {label} reviews: {e}")

    # Deduplicate by review_id
    seen: set[int] = set()
    unique: list[dict] = []
    for doc in all_docs:
        if doc["review_id"] not in seen:
            seen.add(doc["review_id"])
            unique.append(doc)

    return unique
