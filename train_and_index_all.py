"""
train_and_index_all.py — Automated multi-dataset vector training and indexing for OpinionLens.

Embeds and indexes all primary products into local ChromaDB persistent collections:
1. Lenovo A6000 Plus (MOBE7JXXKS6PWW2C) from dataset/lenova.csv
2. Samsung Galaxy J7 Prime (MOBEZF53HHFV6S8R) from dataset/samsung.csv
3. Anker PowerCore 20100 (B00X5RV14Y) from dataset/amazon_electronics.csv
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import DATASET_DIR
from ingest import ingest_product, is_already_ingested

TARGETS = [
    {
        "name": "Samsung Galaxy J7 Prime",
        "csv": DATASET_DIR / "samsung.csv",
        "product_id": "MOBEZF53HHFV6S8R",
        "max_reviews": 150,
    },
    {
        "name": "Anker PowerCore 20100mAh (Amazon Electronics)",
        "csv": DATASET_DIR / "amazon_electronics.csv",
        "product_id": "B00X5RV14Y",
        "max_reviews": 150,
    },
    {
        "name": "Lenovo A6000 Plus (Flipkart Baseline)",
        "csv": DATASET_DIR / "lenova.csv",
        "product_id": "MOBE7JXXKS6PWW2C",
        "max_reviews": 150,
    },
]

def main():
    print("=" * 60)
    print(">> OpinionLens Multi-Dataset Training & Indexing Pipeline")
    print("=" * 60)

    for item in TARGETS:
        csv_path = item["csv"]
        pid = item["product_id"]
        name = item["name"]

        print(f"\n[*] Processing dataset: {name} (ID: {pid})")
        print(f"    Source file: {csv_path.name}")

        if not csv_path.exists():
            print(f"    [!] File {csv_path} not found! Skipping.")
            continue

        start_time = time.time()
        count = ingest_product(
            csv_path=csv_path,
            product_id=pid,
            max_reviews=item["max_reviews"],
            force=False,
            progress_callback=lambda pct, msg: print(f"    [{int(pct*100)}%] {msg}"),
        )
        elapsed = time.time() - start_time
        print(f"    [+] Successfully indexed {count} reviews in {elapsed:.1f}s.")

    print("\n" + "=" * 60)
    print("All target datasets successfully trained and indexed into ChromaDB!")
    print("=" * 60)

if __name__ == "__main__":
    main()
