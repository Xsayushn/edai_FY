"""
aggregator.py — Aspect clustering and contested opinion detection.

Takes a flat list of AspectTuples and:
  1. Groups them into aspect clusters.
  2. Detects contested aspects using the Contention Ratio formula.
"""

from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel

from config import CONTESTED_MIN_RATIO, CONTESTED_MIN_TOTAL
from extractor import AspectTuple


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

class ContestedAspect(BaseModel):
    aspect: str
    pos_count: int
    neg_count: int
    neutral_count: int
    total: int
    ratio: float                        # min(pos,neg) / max(pos,neg)
    pro_citations: list[AspectTuple]    # positive tuples for this aspect
    con_citations: list[AspectTuple]    # negative tuples for this aspect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_aspect(aspect: str) -> str:
    """Title-case and strip extra whitespace for consistent grouping."""
    return aspect.strip().title()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_aspect_clusters(
    tuples: list[AspectTuple],
    excluded_review_ids: set[int] | None = None,
) -> dict[str, list[AspectTuple]]:
    """
    Group tuples by normalized aspect name.

    Args:
        tuples:               All extracted AspectTuples.
        excluded_review_ids:  Optionally exclude tuples from safety-flagged reviews
                              to avoid double-counting in the consensus summary.

    Returns:
        Dict mapping aspect → list of tuples (sorted by review_id).
    """
    excluded = excluded_review_ids or set()
    clusters: dict[str, list[AspectTuple]] = defaultdict(list)

    for t in tuples:
        if t.review_id in excluded:
            continue
        clusters[_normalize_aspect(t.aspect)].append(t)

    # Sort tuples within each cluster by review_id for determinism
    return {asp: sorted(ts, key=lambda t: t.review_id) for asp, ts in clusters.items()}


def compute_contention(
    clusters: dict[str, list[AspectTuple]],
) -> list[ContestedAspect]:
    """
    Identify contested aspects where positive and negative opinions are
    approximately balanced.

    Contention Ratio = min(N_pos, N_neg) / max(N_pos, N_neg)
    An aspect is CONTESTED if N_total >= CONTESTED_MIN_TOTAL
    AND ratio >= CONTESTED_MIN_RATIO.

    Args:
        clusters: Output of build_aspect_clusters().

    Returns:
        List of ContestedAspect objects, sorted by ratio descending.
    """
    contested: list[ContestedAspect] = []

    for aspect, tuples in clusters.items():
        pos = [t for t in tuples if t.sentiment == "positive"]
        neg = [t for t in tuples if t.sentiment == "negative"]
        neu = [t for t in tuples if t.sentiment == "neutral"]
        total = len(tuples)

        n_pos, n_neg = len(pos), len(neg)

        if total < CONTESTED_MIN_TOTAL:
            continue
        if n_pos == 0 or n_neg == 0:
            continue

        ratio = min(n_pos, n_neg) / max(n_pos, n_neg)

        if ratio >= CONTESTED_MIN_RATIO:
            contested.append(
                ContestedAspect(
                    aspect=aspect,
                    pos_count=n_pos,
                    neg_count=n_neg,
                    neutral_count=len(neu),
                    total=total,
                    ratio=round(ratio, 3),
                    pro_citations=pos,
                    con_citations=neg,
                )
            )

    contested.sort(key=lambda c: c.ratio, reverse=True)
    return contested


def summarize_aspect_stats(clusters: dict[str, list[AspectTuple]]) -> list[dict]:
    """
    Return a list of dicts with per-aspect counts for display in the UI.
    Useful for bar/pie charts.
    """
    stats = []
    for aspect, tuples in clusters.items():
        pos = sum(1 for t in tuples if t.sentiment == "positive")
        neg = sum(1 for t in tuples if t.sentiment == "negative")
        neu = sum(1 for t in tuples if t.sentiment == "neutral")
        stats.append(
            {
                "aspect": aspect,
                "positive": pos,
                "negative": neg,
                "neutral": neu,
                "total": len(tuples),
            }
        )
    stats.sort(key=lambda x: x["total"], reverse=True)
    return stats
