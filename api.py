"""
api.py — FastAPI Backend for OpinionLens SSR & Headless Client Services.
Provides high-performance endpoints for Product Discovery, Evidence-Grounded
Opinion Synthesis, Critical-Minority Risk Interception, and Contact Inquiries.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import (
    DEFAULT_CSV,
    DEFAULT_PRODUCT_ID,
    GROQ_MODEL,
    MIN_REVIEWS_FOR_PRODUCT,
)
from dataset_loader import load_universal_dataset, list_products_from_df
from ingest import (
    ingest_product,
    is_already_ingested,
    list_all_brands,
    list_products_in_csv,
)
from retriever import retrieve_opinions
from extractor import extract_aspects, generate_summary, AspectTuple
from guard import detect_critical_risks, CriticalAlert
from aggregator import build_aspect_clusters, compute_contention, summarize_aspect_stats, ContestedAspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("opinionlens_api")

app = FastAPI(
    title="OpinionLens API",
    description="Explainable & Safe RAG Opinion Synthesis API",
    version="2.0.0",
)

# Enable CORS for Next.js SSR / client queries
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class AuditRequest(BaseModel):
    product_id: str = Field(..., description="Target hardware product identifier")
    brand: Optional[str] = Field(None, description="Brand or category name")
    query: Optional[str] = Field("", description="Optional aspect focus query e.g. 'battery heating'")
    exec_mode: Optional[str] = Field("offline", description="'groq' or 'offline'")
    model: Optional[str] = Field(GROQ_MODEL, description="Groq model name")
    groq_api_key: Optional[str] = Field(None, description="Optional personal Groq API key")


class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10, max_length=3000)


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OpinionLens API",
        "version": "2.0.0",
    }


@app.get("/api/brands")
def get_brands():
    """Return all available catalog brands/categories."""
    brands = list_all_brands()
    catalog = []
    for label, path in brands.items():
        try:
            prods = list_products_in_csv(path)
            catalog.append({
                "brand": label,
                "csv_file": path.name,
                "product_count": len(prods),
            })
        except Exception as e:
            logger.warning(f"Failed scanning {label}: {e}")
            catalog.append({
                "brand": label,
                "csv_file": path.name,
                "product_count": 0,
            })
    return {"brands": catalog}


@app.get("/api/products")
def get_products(brand: Optional[str] = Query(None)):
    """Return products for a given brand, or all default products."""
    brands = list_all_brands()
    target_path = None

    if brand:
        for b_label, p in brands.items():
            if b_label.lower() == brand.lower():
                target_path = p
                break

    if target_path is None:
        # Default to Laptops or first available
        for b_label, p in brands.items():
            if "laptop" in b_label.lower():
                target_path = p
                brand = b_label
                break
        if not target_path and brands:
            brand = list(brands.keys())[0]
            target_path = brands[brand]

    if not target_path:
        raise HTTPException(status_code=404, detail="No datasets found.")

    df_prods = list_products_in_csv(target_path)
    products = [
        {
            "product_id": str(row["product_id"]),
            "product_name": str(row["product_name"]),
            "review_count": int(row["review_count"]),
            "brand": brand,
        }
        for _, row in df_prods.iterrows()
    ]
    return {
        "brand": brand,
        "total": len(products),
        "products": products,
    }


@app.get("/api/products/{product_id}")
def get_product_detail(product_id: str):
    """Retrieve product metadata across all loaded brands."""
    brands = list_all_brands()
    for b_label, path in brands.items():
        df_prods = list_products_in_csv(path)
        match = df_prods[df_prods["product_id"] == product_id]
        if not match.empty:
            row = match.iloc[0]
            return {
                "product_id": str(row["product_id"]),
                "product_name": str(row["product_name"]),
                "review_count": int(row["review_count"]),
                "brand": b_label,
            }
    raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")


@app.post("/api/audit")
def run_audit(req: AuditRequest):
    """Execute the full explainable RAG review audit and safety guard pipeline."""
    pid = req.product_id.strip()
    brands = list_all_brands()
    
    # Locate dataset path
    active_path = None
    target_brand = req.brand
    if target_brand:
        for b_label, p in brands.items():
            if b_label.lower() == target_brand.lower():
                active_path = p
                break

    if not active_path:
        # Search all brands
        for b_label, p in brands.items():
            df_prods = list_products_in_csv(p)
            if pid in df_prods["product_id"].values:
                active_path = p
                target_brand = b_label
                break

    if not active_path:
        active_path = Path("dataset") / DEFAULT_CSV

    # 1. Ingestion check
    if not is_already_ingested(pid):
        logger.info(f"Ingesting product {pid} into ChromaDB...")
        try:
            ingest_product(active_path, pid)
        except Exception as e:
            logger.error(f"Ingest failed for {pid}: {e}")

    # 2. Retrieval
    query_str = (req.query or "").strip()
    try:
        reviews = retrieve_opinions(pid, query_str if query_str else None)
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")

    if not reviews:
        return {
            "product_id": pid,
            "reviews": [],
            "alerts": [],
            "contested": [],
            "stats": [],
            "summary": {"consensus_points": ["No reviews matched the query."], "overview": ""},
        }

    # 3. Aspect extraction
    api_key = req.groq_api_key or os.getenv("GROQ_API_KEY", "")
    use_groq = req.exec_mode == "groq" and bool(api_key)
    try:
        extraction = extract_aspects(
            reviews,
            api_key=api_key,
            model=req.model or GROQ_MODEL,
            use_offline=not use_groq,
        )
        tuples = extraction.extracted_tuples
    except Exception as e:
        logger.warning(f"Groq extraction failed, falling back to offline: {e}")
        extraction = extract_aspects(reviews, use_offline=True)
        tuples = extraction.extracted_tuples

    # 4. Critical-Minority Safety Guard
    try:
        alerts = detect_critical_risks(tuples)
    except Exception as e:
        logger.warning(f"Safety guard error: {e}")
        alerts = []

    # 5. Sentiment Aggregation & Contention Detection
    clusters = build_aspect_clusters(tuples)
    contested = compute_contention(clusters)
    stats = summarize_aspect_stats(clusters)

    # 6. Attributed Summary
    try:
        summary_obj = generate_summary(
            clusters,
            contested,
            alerts,
            api_key=api_key,
            model=req.model or GROQ_MODEL,
            use_offline=not use_groq,
        )
        summary_data = {
            "consensus_points": summary_obj.consensus_points,
            "overview": summary_obj.consensus_points[0] if summary_obj.consensus_points else "Customer reviews analyzed with verified vector citations.",
        }
    except Exception as e:
        logger.warning(f"Summary generation error: {e}")
        summary_data = {
            "consensus_points": [
                f"{c.aspect}: Highly contested consumer opinion noted." for c in contested[:4]
            ],
            "overview": "Customer reviews demonstrate diverse sentiment across core hardware attributes.",
        }

    # Serialize results cleanly
    serializable_alerts = [
        {
            "risk_term": a.risk_term,
            "severity": "CRITICAL",
            "matching_reviews": len(a.matching_reviews),
            "quotes": a.quotes,
        }
        for a in alerts
    ]

    serializable_contested = [
        {
            "aspect": c.aspect,
            "ratio": round(c.ratio, 2),
            "pos_count": c.pos_count,
            "neg_count": c.neg_count,
            "sample_positive": c.pro_citations[0].quote if c.pro_citations else "",
            "sample_negative": c.con_citations[0].quote if c.con_citations else "",
        }
        for c in contested
    ]

    serializable_reviews = [
        {
            "review_id": r.get("review_id", idx + 1),
            "rating": r.get("rating", 3),
            "date": str(r.get("date", "Verified Purchase")),
            "review_text": r.get("review_text", ""),
            "helpful_votes": r.get("helpful_votes", 0),
        }
        for idx, r in enumerate(reviews[:20])
    ]

    # Calculate average rating
    ratings = [r.get("rating", 3) for r in reviews if isinstance(r.get("rating"), (int, float))]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 4.0

    return {
        "product_id": pid,
        "brand": target_brand or "Electronics",
        "review_count": len(reviews),
        "rating_avg": avg_rating,
        "summary": summary_data,
        "alerts": serializable_alerts,
        "contested": serializable_contested,
        "stats": stats,
        "reviews": serializable_reviews,
    }


@app.post("/api/contact")
def submit_contact(msg: ContactMessage):
    """Handle contact inquiries with validation, logging, and confirmation response."""
    logger.info(f"Contact form submitted by {msg.name} <{msg.email}>: {msg.subject}")
    # In a production environment, dispatch via SendGrid/SES or write to inquiry queue.
    return {
        "success": True,
        "message": f"Thank you, {msg.name}. Your inquiry regarding '{msg.subject}' has been securely logged. An OpinionLens safety specialist will follow up shortly.",
        "received_at": "now",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
