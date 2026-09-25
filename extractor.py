"""
extractor.py — LLM-powered aspect-sentiment extraction and attributed summary generation.

Features:
1. Groq LLM integration (llama-3.3-70b-versatile, qwen/qwen3.8-27b, llama-3.1-8b-instant).
2. Offline / Local Heuristic Opinion Extractor (Zero-API fallback mode for maximum accessibility).
3. Pydantic v2 schemas and validation.
4. Dynamic API key and model selection support from UI.
"""

from __future__ import annotations

import json
import os
import re
from textwrap import dedent
from typing import List, Literal, Optional

from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

from config import EXTRACTION_BATCH_SIZE, GROQ_MODEL

# Anchor .env lookup to the project root regardless of CWD (Streamlit shifts it)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class AspectTuple(BaseModel):
    aspect: str = Field(
        description="Normalized aspect name, e.g., 'Battery Life', 'Camera Quality', 'Display'"
    )
    sentiment: Literal["positive", "negative", "neutral"]
    summary_claim: str = Field(
        description="Concise synthesis of what the user stated"
    )
    quote: str = Field(
        description="Verbatim excerpt from the review text justifying this claim (max 120 chars)"
    )
    review_id: int = Field(description="ID of the source review")


class ExtractionResult(BaseModel):
    extracted_tuples: List[AspectTuple]


class SummaryResult(BaseModel):
    consensus_points: List[str] = Field(
        description="3-5 cited summary bullet points. Every factual claim must end with [Review #ID] or [#ID, #ID]."
    )
    contested_aspects: List[str] = Field(
        description="Contrasting viewpoints with pro/con citations."
    )
    safety_alerts: List[str] = Field(
        description="Critical safety alerts with explicit review citations."
    )


# ---------------------------------------------------------------------------
# Groq client
# ---------------------------------------------------------------------------

def _get_client(api_key: Optional[str] = None) -> Optional[Groq]:
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key or not key.strip() or key.startswith("your_groq"):
        return None
    return Groq(api_key=key.strip())


# ---------------------------------------------------------------------------
# Offline / Local Heuristic Opinion Extractor (Zero-API Mode)
# ---------------------------------------------------------------------------

_ASPECT_KEYWORDS = {
    "Battery Life": [
        "battery", "backup", "drain", "charging", "charger", "mah", "discharging",
        "power", "standby", "battery life"
    ],
    "Camera Quality": [
        "camera", "picture", "photo", "selfie", "video", "clarity", "sensor",
        "portrait", "lens", "shutter", "pixels", "shots"
    ],
    "Display": [
        "display", "screen", "resolution", "brightness", "touch", "touchscreen",
        "amoled", "ips", "refresh rate", "glass"
    ],
    "Performance": [
        "performance", "speed", "lag", "hang", "lagging", "hanging", "smooth",
        "fast", "ram", "processor", "gaming", "multitasking"
    ],
    "Heating": [
        "heat", "heating", "warm", "overheat", "overheating", "hot", "temperature",
        "thermal"
    ],
    "Build Quality": [
        "build", "design", "body", "look", "feel", "finish", "weight", "slim",
        "plastic", "metal", "durable", "sturdy", "durability"
    ],
    "Value for Money": [
        "price", "value", "worth", "money", "budget", "cost", "cheap", "expensive",
        "pricing"
    ],
    "Sound & Audio": [
        "sound", "speaker", "audio", "music", "volume", "earpiece", "mic",
        "headphone", "bass", "loud"
    ],
    "Software & UI": [
        "software", "ui", "os", "android", "apps", "update", "updates", "interface"
    ],
    "Network & Signal": [
        "network", "signal", "wifi", "call", "sim", "volte", "connectivity", "4g", "5g"
    ],
}

_POSITIVE_INDICATORS = {
    "good", "great", "excellent", "superb", "best", "love", "awesome", "decent",
    "nice", "amazing", "smooth", "fast", "clear", "crisp", "impressive", "reliable",
    "satisfied", "perfect", "fantastic", "worthy", "happy", "liked", "brilliant"
}

_NEGATIVE_INDICATORS = {
    "bad", "poor", "worst", "lag", "hang", "slow", "drain", "draining", "terrible",
    "issue", "issues", "problem", "problems", "heat", "heating", "hot", "blurry",
    "defective", "waste", "horrible", "disappointed", "pathetic", "failed", "faulty",
    "overheat", "swelling", "burn", "shock", "fire", "smoke"
}


def extract_aspects_offline(reviews: list[dict]) -> ExtractionResult:
    """
    High-speed, zero-API local opinion extractor.
    Extracts aspect-sentiment tuples using linguistic analysis, aspect lexicons,
    and polarity scoring. Enables complete offline evaluation.
    """
    all_tuples: list[AspectTuple] = []

    for r in reviews:
        rid = r["review_id"]
        text = r.get("review_text", "")
        rating = r.get("rating", 3)

        # Split review into sentences
        sentences = re.split(r"(?<=[.!?])\s+|\n+", text)

        aspects_found_in_review = set()

        for raw_sent in sentences:
            sent = raw_sent.strip()
            if len(sent) < 10:
                continue

            sent_lower = sent.lower()
            tokens = set(re.findall(r"\b[a-z]{3,}\b", sent_lower))

            # Match aspects
            for aspect, keywords in _ASPECT_KEYWORDS.items():
                if aspect in aspects_found_in_review:
                    continue  # Limit to 1 tuple per aspect per review

                if any(kw in sent_lower for kw in keywords):
                    # Compute sentiment
                    pos_hits = len(tokens.intersection(_POSITIVE_INDICATORS))
                    neg_hits = len(tokens.intersection(_NEGATIVE_INDICATORS))

                    if pos_hits > neg_hits or (pos_hits == neg_hits and rating >= 4):
                        sentiment: Literal["positive", "negative", "neutral"] = "positive"
                        claim = f"Praised {aspect.lower()}"
                    elif neg_hits > pos_hits or (pos_hits == neg_hits and rating <= 2):
                        sentiment = "negative"
                        claim = f"Reported concerns regarding {aspect.lower()}"
                    else:
                        sentiment = "neutral"
                        claim = f"Discussed {aspect.lower()}"

                    quote = sent[:120]
                    all_tuples.append(
                        AspectTuple(
                            aspect=aspect,
                            sentiment=sentiment,
                            summary_claim=claim,
                            quote=quote,
                            review_id=rid,
                        )
                    )
                    aspects_found_in_review.add(aspect)
                    if len(aspects_found_in_review) >= 3:
                        break  # Max 3 tuples per review

    return ExtractionResult(extracted_tuples=all_tuples)


# ---------------------------------------------------------------------------
# Extraction (LLM with Automatic Offline Fallback)
# ---------------------------------------------------------------------------

_EXTRACTION_SYSTEM = dedent("""
You are a product review analyst. Given a batch of numbered product reviews,
extract aspect-sentiment tuples in strict JSON format.

Rules:
- Output a JSON object with a single key "extracted_tuples" containing a list.
- Each tuple must have: aspect, sentiment (positive/negative/neutral),
  summary_claim, quote (verbatim ≤120 chars), review_id (integer).
- Normalize aspect names: use consistent capitalized labels like
  "Battery Life", "Camera Quality", "Display", "Performance", "Build Quality",
  "Value for Money", "Software & UI", "Heating", "Network & Signal", "Sound & Audio".
- Extract 1-3 tuples per review. Skip unsubstantive reviews.
- Output ONLY the JSON object. No markdown, no explanation.
""").strip()


def _build_extraction_prompt(reviews: list[dict]) -> str:
    lines = []
    for r in reviews:
        lines.append(
            f"[Review #{r['review_id']} | Rating:{r['rating']} | {r.get('date', '')}]\n"
            f"{r['review_text']}\n"
        )
    return "\n---\n".join(lines)


def extract_aspects(
    reviews: list[dict],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    use_offline: bool = False,
) -> ExtractionResult:
    """
    Extract aspect-sentiment tuples from a list of review dicts.
    If use_offline=True or no Groq API key is configured, uses high-speed
    local heuristic extraction. Otherwise, invokes Groq LLM.
    """
    client = None if use_offline else _get_client(api_key)
    selected_model = model or GROQ_MODEL

    if client is None:
        print("[extractor] Running in Zero-API Local Mode (Offline Extractor).")
        return extract_aspects_offline(reviews)

    all_tuples: list[AspectTuple] = []
    valid_ids = {r["review_id"] for r in reviews}

    # Process in batches
    for i in range(0, len(reviews), EXTRACTION_BATCH_SIZE):
        batch = reviews[i : i + EXTRACTION_BATCH_SIZE]
        prompt = _build_extraction_prompt(batch)

        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": _EXTRACTION_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=4096,
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)
            result = ExtractionResult.model_validate(data)

            # Sanity-check: only keep tuples referencing real review IDs
            for t in result.extracted_tuples:
                if t.review_id in valid_ids:
                    all_tuples.append(t)

        except Exception as e:
            batch_ids = [r["review_id"] for r in batch]
            print(f"[extractor] Warning: batch {batch_ids} failed — {e}")
            # Fall back to offline extraction for this batch
            offline_sub = extract_aspects_offline(batch)
            all_tuples.extend(offline_sub.extracted_tuples)

    if not all_tuples:
        return extract_aspects_offline(reviews)

    return ExtractionResult(extracted_tuples=all_tuples)


# ---------------------------------------------------------------------------
# Summary Generation
# ---------------------------------------------------------------------------

_SUMMARY_SYSTEM = dedent("""
You are a strict evidence-based product summarizer.

Rules:
1. Synthesize into 3-5 consensus_points (bullet-style strings). Every factual
   claim MUST end with a citation like [Review #5] or [#12, #45]. You are
   FORBIDDEN from making ungrounded claims.
2. For contested_aspects, list each contested aspect with a balanced pro/con
   summary and their citations. If none, use an empty list.
3. For safety_alerts, repeat any critical safety warnings with their citations.
   If none, use an empty list.
4. Output ONLY a valid JSON object with exactly these three keys:
   "consensus_points", "contested_aspects", "safety_alerts".
   Each value must be a list of strings. No markdown fences, no explanation.
""").strip()

_MAX_EVIDENCE_CHARS = 5000


def _build_evidence_text(
    clusters: dict,
    contested: list,
    alerts: list,
) -> str:
    """Build the structured evidence payload, capped at _MAX_EVIDENCE_CHARS."""
    sections: list[str] = []

    sections.append("=== ASPECT EVIDENCE ===")
    for aspect, tuples in list(clusters.items())[:8]:
        pos = [t for t in tuples if t.sentiment == "positive"]
        neg = [t for t in tuples if t.sentiment == "negative"]
        sections.append(f"\n[{aspect}]")
        for t in pos[:3]:
            claim = t.summary_claim[:80]
            quote = t.quote[:80]
            sections.append(f"  + [Review #{t.review_id}]: {claim} | \"{quote}\"")
        for t in neg[:3]:
            claim = t.summary_claim[:80]
            quote = t.quote[:80]
            sections.append(f"  - [Review #{t.review_id}]: {claim} | \"{quote}\"")

    if contested:
        sections.append("\n=== CONTESTED ASPECTS ===")
        for c in contested[:5]:
            sections.append(
                f"[{c.aspect}] {c.pos_count} positive vs {c.neg_count} negative "
                f"(contention ratio={c.ratio:.2f})"
            )
            for cit in c.pro_citations[:2]:
                sections.append(f"  PRO [Review #{cit.review_id}]: {cit.summary_claim[:80]}")
            for cit in c.con_citations[:2]:
                sections.append(f"  CON [Review #{cit.review_id}]: {cit.summary_claim[:80]}")

    if alerts:
        sections.append("\n=== CRITICAL SAFETY ALERTS ===")
        for a in alerts:
            review_ids = ", ".join(f"#{r}" for r in a.matching_reviews[:6])
            sections.append(f"RISK: {a.risk_term} | Reviews: {review_ids}")
            for q in a.quotes[:2]:
                sections.append(f"  Quote: \"{q[:100]}\"")

    text = "\n".join(sections)
    return text[:_MAX_EVIDENCE_CHARS]


def _fallback_summary(
    clusters: dict,
    contested: list,
    alerts: list,
    error: Optional[Exception] = None,
) -> "SummaryResult":
    """
    Evidence-grounded deterministic summary generator.
    Produces cited bullet points directly from cluster statistics.
    """
    points: list[str] = []

    # Top positive & critical aspects
    for aspect, tuples in list(clusters.items())[:6]:
        pos = [t for t in tuples if t.sentiment == "positive"]
        neg = [t for t in tuples if t.sentiment == "negative"]
        if pos:
            ids = ", ".join(f"#{t.review_id}" for t in pos[:3])
            points.append(f"{aspect}: Generally praised by users — {pos[0].summary_claim} [{ids}].")
        if neg and len(neg) >= len(pos):
            ids = ", ".join(f"#{t.review_id}" for t in neg[:3])
            points.append(f"{aspect}: Critical user feedback noted — {neg[0].summary_claim} [{ids}].")

    contested_strs = [
        f"{c.aspect}: {c.pos_count} users positive vs {c.neg_count} negative "
        f"(contention {int(c.ratio*100)}%)"
        for c in contested
    ]

    alert_strs = [
        f"⚠ CRITICAL — {a.risk_term}: flagged across {len(a.matching_reviews)} reviews "
        f"({', '.join(f'#{r}' for r in a.matching_reviews[:4])})"
        for a in alerts
    ]

    if not points:
        points = ["Not enough evidence to generate a consensus summary."]

    if error:
        error_short = str(error)[:100]
        points.append(f"ℹ️ Note: LLM summarization unavailable ({error_short}). Showing evidence-grounded summary.")

    return SummaryResult(
        consensus_points=points,
        contested_aspects=contested_strs,
        safety_alerts=alert_strs,
    )


def generate_summary(
    clusters: dict[str, list[AspectTuple]],
    contested: list,
    alerts: list,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    use_offline: bool = False,
) -> "SummaryResult":
    """
    Generate an attributed, cited summary from aspect clusters, contested items,
    and safety alerts.
    """
    client = None if use_offline else _get_client(api_key)
    selected_model = model or GROQ_MODEL

    if client is None:
        return _fallback_summary(clusters, contested, alerts)

    evidence_text = _build_evidence_text(clusters, contested, alerts)

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": _SUMMARY_SYSTEM},
                {"role": "user", "content": evidence_text},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1500,
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        return SummaryResult.model_validate(data)

    except Exception as e:
        print(f"[extractor] Summary generation failed: {type(e).__name__}: {e}")
        return _fallback_summary(clusters, contested, alerts, e)
