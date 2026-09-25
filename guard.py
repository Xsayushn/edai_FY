"""
guard.py — Critical-Minority Safety Guard.

Detects low-frequency but high-severity complaints in extracted AspectTuples
and emits CriticalAlert objects when the same risk appears in ≥ N reviews.

Two detection strategies (applied in order):
  1. Fast path: case-insensitive substring matching against RISK_TAXONOMY.
  2. Semantic path: cosine similarity between tuple text and pre-embedded
     risk terms (threshold RISK_SEMANTIC_THRESHOLD).
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache

import numpy as np
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from config import (
    CRITICAL_ALERT_MIN_REVIEWS,
    EMBEDDING_MODEL,
    RISK_SEMANTIC_THRESHOLD,
    RISK_TAXONOMY,
)
from extractor import AspectTuple


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

class CriticalAlert(BaseModel):
    risk_term: str
    matching_reviews: list[int]      # unique review IDs
    quotes: list[str]                # verbatim quotes from the flagged tuples
    summary_claims: list[str]        # summary_claims from the flagged tuples


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _risk_embeddings() -> np.ndarray:
    """Pre-compute and cache embeddings for all RISK_TAXONOMY terms."""
    model = _get_model()
    return model.encode(RISK_TAXONOMY, normalize_embeddings=True)


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D normalised vectors."""
    return float(np.dot(a, b))


def _text_matches_risk_substring(text: str, risk_term: str) -> bool:
    return risk_term.lower() in text.lower()


def _text_matches_risk_semantic(text: str, risk_index: int) -> bool:
    """Return True if *text* is semantically similar to risk_term at risk_index."""
    model = _get_model()
    risk_embs = _risk_embeddings()
    text_emb = model.encode([text], normalize_embeddings=True)[0]
    sim = _cosine_sim(text_emb, risk_embs[risk_index])
    return sim >= RISK_SEMANTIC_THRESHOLD


def _tuple_matches_risk(t: AspectTuple) -> list[str]:
    """
    Return a list of risk terms (from RISK_TAXONOMY) that the tuple matches.
    Combines fast substring check with semantic fallback.
    """
    combined_text = f"{t.summary_claim} {t.quote}"
    matched: list[str] = []

    for idx, risk_term in enumerate(RISK_TAXONOMY):
        if _text_matches_risk_substring(combined_text, risk_term):
            matched.append(risk_term)
        elif _text_matches_risk_semantic(combined_text, idx):
            matched.append(risk_term)

    return matched


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_critical_risks(tuples: list[AspectTuple]) -> list[CriticalAlert]:
    """
    Scan extracted tuples for critical safety risks.
    Combines high-speed substring matching with vectorized batch semantic cosine similarity.
    """
    if not tuples:
        return []

    risk_to_reviews: dict[str, dict[int, list[AspectTuple]]] = defaultdict(lambda: defaultdict(list))
    unmatched_tuples: list[AspectTuple] = []

    # 1. Fast path: substring matching
    for t in tuples:
        combined = f"{t.summary_claim} {t.quote}".lower()
        matched = False
        for risk in RISK_TAXONOMY:
            if risk.lower() in combined:
                risk_to_reviews[risk][t.review_id].append(t)
                matched = True
        if not matched:
            unmatched_tuples.append(t)

    # 2. Semantic path: vectorized matrix dot-product in a single batch
    if unmatched_tuples:
        model = _get_model()
        risk_embs = _risk_embeddings()  # Shape: (num_risks, 384)
        texts = [f"{t.summary_claim} {t.quote}" for t in unmatched_tuples]
        text_embs = model.encode(texts, normalize_embeddings=True, batch_size=32)  # Shape: (num_texts, 384)
        sim_matrix = np.dot(text_embs, risk_embs.T)  # Shape: (num_texts, num_risks)

        for t_idx, t in enumerate(unmatched_tuples):
            for r_idx, risk in enumerate(RISK_TAXONOMY):
                if sim_matrix[t_idx, r_idx] >= RISK_SEMANTIC_THRESHOLD:
                    risk_to_reviews[risk][t.review_id].append(t)

    alerts: list[CriticalAlert] = []

    for risk_term, review_map in risk_to_reviews.items():
        if len(review_map) >= CRITICAL_ALERT_MIN_REVIEWS:
            matching_review_ids = list(review_map.keys())
            quotes: list[str] = []
            claims: list[str] = []
            for rid, ts in review_map.items():
                for t in ts:
                    if t.quote not in quotes:
                        quotes.append(t.quote)
                    if t.summary_claim not in claims:
                        claims.append(t.summary_claim)

            alerts.append(
                CriticalAlert(
                    risk_term=risk_term,
                    matching_reviews=matching_review_ids,
                    quotes=quotes[:10],
                    summary_claims=claims[:10],
                )
            )

    alerts.sort(key=lambda a: len(a.matching_reviews), reverse=True)
    return alerts
