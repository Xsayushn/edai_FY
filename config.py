"""
config.py — Central configuration for the Explainable RAG Opinion Summarizer.
All paths, model names, thresholds, and taxonomies live here.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent
DATASET_DIR = PROJECT_ROOT / "dataset"
CHROMA_DB_PATH = str(PROJECT_ROOT / "chroma_db")

# ---------------------------------------------------------------------------
# Dataset schema
# The CSVs have no header row; columns are assigned in this order.
# ---------------------------------------------------------------------------
CSV_COLUMNS = [
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
CSV_ENCODING = "latin1"

# Minimum reviews a product must have to appear in the dropdown
MIN_REVIEWS_FOR_PRODUCT = 100

# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------
MAX_REVIEWS_PER_PRODUCT = 500   # cap per product to keep LLM cost manageable
DEFAULT_CSV = "lenova.csv"
DEFAULT_PRODUCT_ID = "MOBE7JXXKS6PWW2C"  # Lenovo A6000 Plus (970 reviews)

# ---------------------------------------------------------------------------
# Embeddings & Vector DB
# ---------------------------------------------------------------------------
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
CHROMA_COLLECTION_PREFIX = "reviews_"   # collection name = prefix + product_id

# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
TOP_K_ASPECT = 25          # semantic search mode
TOP_K_PER_BUCKET = 15      # reviews per rating bucket in balanced mode

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
GROQ_MODEL = "qwen/qwen3.8-27b"
EXTRACTION_BATCH_SIZE = 10  # reviews per LLM call

# ---------------------------------------------------------------------------
# Safety Guard
# ---------------------------------------------------------------------------
RISK_TAXONOMY = [
    "overheating",
    "burn",
    "battery explosion",
    "swelling",
    "electric shock",
    "fire",
    "smoke",
    "counterfeit",
    "fraud",
]
# Minimum number of distinct reviews flagging the same risk to emit an alert
CRITICAL_ALERT_MIN_REVIEWS = 2
# Cosine similarity threshold for semantic risk matching
RISK_SEMANTIC_THRESHOLD = 0.75

# ---------------------------------------------------------------------------
# Contested Opinion Detection
# ---------------------------------------------------------------------------
CONTESTED_MIN_TOTAL = 3      # minimum total tuples for an aspect to be assessed
CONTESTED_MIN_RATIO = 0.20   # min(pos,neg) / max(pos,neg) threshold (20%+ disagreement)

