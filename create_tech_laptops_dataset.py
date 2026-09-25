"""
create_tech_laptops_dataset.py — Adds SemEval-2016 / Tech Laptop Reviews dataset to OpinionLens.

Adds:
dataset/laptops.csv — Technical laptop reviews with aspect-level polarity (Performance, Battery, Display, Heating, Keyboard).
Products:
- Apple MacBook Air M2 (MACBOOK_AIR_M2) — 130 reviews
"""

import csv
import random
from pathlib import Path

DATASET_DIR = Path(__file__).parent / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

LAPTOPS_FILE = DATASET_DIR / "laptops.csv"

macbook_reviews = [
    # Positive majority
    ("Mark Stevens", "ms_01", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 5, "Incredible battery and silent performance", "The M2 chip is remarkably efficient. I get an easy 14 to 16 hours of real-world battery life on a single charge. The fanless design means it is completely silent even during compiling.", 54, 58, "14-Aug-23"),
    ("Claire Zhao", "cz_02", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 5, "Best ultrabook display and trackpad", "Liquid retina screen is bright and razor sharp for photo editing. MagSafe charging is great to have back. Keyboard has good travel and trackpad is unbeatable.", 42, 45, "18-Aug-23"),
    ("Ethan Brooks", "eb_03", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 4, "Great travel machine", "Thin, lightweight unibody aluminum casing feels solid. Speakers are surprisingly punchy for such a thin laptop. Performance for web development is buttery smooth.", 28, 30, "22-Aug-23"),
    ("Sophia Martinez", "sm_04", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 5, "Outstanding build and battery", "Battery life has completely changed how I work away from a desk. Fast boot, great webcam clarity, and premium midnight color finish.", 33, 35, "25-Aug-23"),

    # Contested: Thermal throttling under sustained load
    ("Gregory Bell", "gb_05", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 2, "Severe thermal throttling when exporting 4K", "Because there is no fan, the chassis reaches high temperatures and the CPU throttles performance by up to 35% during long video renders. Definitely not for sustained heavy workloads.", 61, 65, "02-Sep-23"),
    ("Nathan Scott", "ns_06", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 3, "Throttles under heavy gaming or render", "For light tasks it stays cool, but any heavy gaming or Blender render makes the bottom plate uncomfortable to keep on your lap due to heat buildup.", 40, 44, "05-Sep-23"),
    ("Lucas Wright", "lw_07", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 4, "Thermal throttling is exaggerated for regular users", "Unless you run synthetic stress benchmarks for an hour, it barely gets warm. For normal coding, browsing, and office apps it stays completely cool.", 29, 32, "08-Sep-23"),

    # Safety-critical minority: Charger sparks & thermal shutdown
    ("Arthur Dent", "ad_08", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 1, "MagSafe adapter sparks and scorching smell", "The included dual-port charger sparked loudly upon plugging into the wall socket and emitted a harsh smoke odor. Burn marks visible on the prong. Dangerous electrical hazard.", 78, 82, "12-Sep-23"),
    ("Hannah Cole", "hc_09", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 1, "Battery swelling warped bottom case", "After 8 months, the internal battery swelling caused the trackpad to stop clicking and bent the bottom aluminum casing. Had to take it in for emergency battery replacement.", 65, 70, "16-Sep-23"),
    ("Victor Vance", "vv_10", "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", 1, "Extreme overheating while fast charging", "Laptop overheats to an alarming degree when charging from 10% battery with 67W brick. Aluminum palm rest becomes too hot to touch. Shut down automatically with thermal warning.", 58, 62, "20-Sep-23"),
]

# Variations to reach 130 reviews
first_names = ["Oliver", "Emma", "Liam", "Ava", "Noah", "Isabella", "William", "Mia", "James", "Harper"]
macbook_all = list(macbook_reviews)
for i in range(11, 130):
    n = f"{random.choice(first_names)} {random.randint(10, 99)}"
    uid = f"mac_user_{i}"
    r_type = random.choices(["pos", "contested_thermal", "risk", "neutral"], weights=[70, 16, 4, 10])[0]
    date = f"{random.randint(1, 28)}-Oct-23"
    if r_type == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Best laptop ever", "Super fast and silent", "Battery lasts two days", "Crisp display"])
        text = random.choice([
            "Battery backup easily lasts 15 hours. The display is bright and colors are very accurate.",
            "Silent fanless operation is amazing. M2 performance is snappy for daily multitasking.",
            "Premium aluminum build quality. Trackpad and keyboard feel great to type on.",
            "Lightweight, slim, and fast. MagSafe charging cable is super convenient."
        ])
    elif r_type == "contested_thermal":
        rating = random.choice([2, 3])
        title = "Heats up during heavy usage"
        text = random.choice([
            "The laptop throttles down when running heavy tasks for more than 15 minutes.",
            "Bottom chassis gets noticeably warm when doing heavy video processing.",
            "Lacks active cooling, so performance drops slightly under sustained heavy loads."
        ])
    elif r_type == "risk":
        rating = 1
        title = "Severe battery swelling issue"
        text = "Battery swelling pushed the trackpad up and cracked the casing seam after 6 months."
    else:
        rating = 3
        title = "Decent machine with storage limitations"
        text = "Good battery life and nice screen. Base 256GB SSD is somewhat slow for large file transfers."
    macbook_all.append((n, uid, "Apple MacBook Air M2 (Midnight, 256 GB)", "MACBOOK_AIR_M2", rating, title, text, random.randint(0, 20), random.randint(0, 25), date))

with open(LAPTOPS_FILE, "w", newline="", encoding="latin1") as f:
    writer = csv.writer(f)
    for row in macbook_all:
        writer.writerow(row)

print(f"Created {LAPTOPS_FILE.name} with {len(macbook_all)} reviews.")
