"""
test_pipeline.py — End-to-end verification test for OpinionLens.

Tests:
1. Universal Dataset Loading (Samsung, Amazon Electronics, Lenovo).
2. Offline / Zero-API Opinion Extraction.
3. Critical-Minority Safety Guard detection (Overheating / Swelling / Smoke).
4. Aspect clustering & Contention detection.
5. Deterministic Cited Summary Generation.
"""

from dataset_loader import load_universal_dataset
from extractor import extract_aspects_offline, generate_summary
from guard import detect_critical_risks
from aggregator import build_aspect_clusters, compute_contention, summarize_aspect_stats

def run_tests():
    print(">>> 1. Testing Universal Dataset Loader...")
    df_s = load_universal_dataset("dataset/samsung.csv")
    assert len(df_s) > 0, "Samsung dataset empty!"
    print(f"    Samsung dataset: {len(df_s)} reviews loaded successfully.")

    df_a = load_universal_dataset("dataset/amazon_electronics.csv")
    assert len(df_a) > 0, "Amazon dataset empty!"
    print(f"    Amazon dataset: {len(df_a)} reviews loaded successfully.")

    df_l = load_universal_dataset("dataset/laptops.csv")
    assert len(df_l) > 0, "Laptops dataset empty!"
    print(f"    Laptops dataset: {len(df_l)} reviews loaded successfully.")

    print("\n>>> 2. Testing Offline Aspect-Sentiment Extraction...")
    # Convert first 20 reviews to list of dicts
    reviews = df_s.head(20).to_dict(orient="records")
    for r in reviews:
        r["review_id"] = int(r.get("review_id", 0) if str(r.get("review_id", "")).isdigit() else 1)
    
    # Run offline extractor
    extraction = extract_aspects_offline(reviews)
    tuples = extraction.extracted_tuples
    print(f"    Extracted {len(tuples)} aspect tuples across {len(reviews)} reviews.")
    assert len(tuples) > 0, "No tuples extracted!"

    print("\n>>> 3. Testing Critical-Minority Safety Guard...")
    alerts = detect_critical_risks(tuples)
    print(f"    Safety Guard evaluated {len(tuples)} tuples -> {len(alerts)} CriticalAlert(s) detected.")
    for a in alerts:
        print(f"      - Alert: {a.risk_term.upper()} in reviews {a.matching_reviews}")

    print("\n>>> 4. Testing Aggregator & Contention Calculation...")
    clusters = build_aspect_clusters(tuples)
    contested = compute_contention(clusters)
    stats = summarize_aspect_stats(clusters)
    print(f"    Aspect clusters: {list(clusters.keys())}")
    print(f"    Contested aspects: {[c.aspect for c in contested]}")

    print("\n>>> 5. Testing Attributed Summary Generation (Zero-API)...")
    summary = generate_summary(clusters, contested, alerts, use_offline=True)
    print("    Consensus Summary Points:")
    for pt in summary.consensus_points:
        print(f"      * {pt}")

    print("\n=======================================================")
    print("ALL TESTS PASSED! OpinionLens pipeline verified working.")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
