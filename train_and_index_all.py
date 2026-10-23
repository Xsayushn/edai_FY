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
    # 1. High-Performance Laptops (SemEval Benchmark)
    {
        "name": "Apple MacBook Air M2 (Midnight, 256 GB)",
        "csv": DATASET_DIR / "laptops.csv",
        "product_id": "MACBOOK_AIR_M2",
        "max_reviews": 150,
    },
    {
        "name": "Dell XPS 15 9530 (OLED 3.5K, Core i7)",
        "csv": DATASET_DIR / "laptops.csv",
        "product_id": "DELL_XPS_15",
        "max_reviews": 150,
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon Gen 11",
        "csv": DATASET_DIR / "laptops.csv",
        "product_id": "THINKPAD_X1_CARBON",
        "max_reviews": 150,
    },

    # 2. Audio & Headphones (Noise Cancelling & True Wireless)
    {
        "name": "Sony WH-1000XM4 Wireless Headphones",
        "csv": DATASET_DIR / "audio_headphones.csv",
        "product_id": "SONY_WH1000XM4",
        "max_reviews": 150,
    },
    {
        "name": "Apple AirPods Pro (2nd Generation)",
        "csv": DATASET_DIR / "audio_headphones.csv",
        "product_id": "AIRPODS_PRO_2",
        "max_reviews": 150,
    },

    # 3. Smartwatches & Wearables
    {
        "name": "Apple Watch Series 8 (GPS, 45mm)",
        "csv": DATASET_DIR / "smartwatches.csv",
        "product_id": "APPLE_WATCH_S8",
        "max_reviews": 150,
    },
    {
        "name": "Samsung Galaxy Watch 5 (44mm Bluetooth)",
        "csv": DATASET_DIR / "smartwatches.csv",
        "product_id": "GALAXY_WATCH_5",
        "max_reviews": 150,
    },

    # 4. Gaming Consoles & Handhelds
    {
        "name": "Sony PlayStation 5 Console (Disc Edition)",
        "csv": DATASET_DIR / "gaming_consoles.csv",
        "product_id": "PS5_CONSOLE",
        "max_reviews": 150,
    },
    {
        "name": "Valve Steam Deck OLED (512 GB)",
        "csv": DATASET_DIR / "gaming_consoles.csv",
        "product_id": "STEAM_DECK_OLED",
        "max_reviews": 150,
    },

    # 5. Smart Home & Security IoT
    {
        "name": "Amazon Echo Dot (5th Generation)",
        "csv": DATASET_DIR / "smart_home.csv",
        "product_id": "ECHO_DOT_GEN5",
        "max_reviews": 150,
    },
    {
        "name": "Google Nest Cam (Outdoor or Indoor, Battery)",
        "csv": DATASET_DIR / "smart_home.csv",
        "product_id": "NEST_CAM_INDOOR",
        "max_reviews": 150,
    },

    # 6. Power Banks & Chargers
    {
        "name": "Anker PowerCore 20100mAh Portable Charger",
        "csv": DATASET_DIR / "amazon_electronics.csv",
        "product_id": "B00X5RV14Y",
        "max_reviews": 150,
    },

    # 7. Mobile Smartphones (Flipkart / Mendeley Baseline)
    {
        "name": "Samsung Galaxy J7 Prime",
        "csv": DATASET_DIR / "samsung.csv",
        "product_id": "MOBEZF53HHFV6S8R",
        "max_reviews": 150,
    },
    {
        "name": "Lenovo A6000 Plus (Baseline)",
        "csv": DATASET_DIR / "lenova.csv",
        "product_id": "MOBE7JXXKS6PWW2C",
        "max_reviews": 150,
    },
    {
        "name": "Apple iPhone SE (Space Grey, 32 GB)",
        "csv": DATASET_DIR / "iphone.csv",
        "product_id": "MOBETM9FZWW5UEZG",
        "max_reviews": 150,
    },
    {
        "name": "Redmi Note 3 (Dark Grey, 16 GB)",
        "csv": DATASET_DIR / "redmi.csv",
        "product_id": "MOBEHCFD3FSTUU7T",
        "max_reviews": 150,
    },
    {
        "name": "Moto G (2nd Generation)",
        "csv": DATASET_DIR / "moto.csv",
        "product_id": "MOBDYZUSXMT2TDHF",
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
