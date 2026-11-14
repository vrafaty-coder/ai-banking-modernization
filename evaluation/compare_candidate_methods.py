
"""
Compare Code-only and Hybrid candidate discovery.

The draft mapping is used only for evaluation,
not for generating candidate matches.
"""

import csv
from pathlib import Path

from rule_parser import load_json
from candidate_discovery import (
    discover_candidates,
    discover_candidates_hybrid,
)


project_root = Path(__file__).resolve().parent.parent
ai_dir = project_root / "ai"
evaluation_dir = project_root / "evaluation"

gold_file = ai_dir / "tx01_gold_standard_v1.0.json"
gemini_file = ai_dir / "tx01_llm_rules.json"
mapping_file = evaluation_dir / "tx01_llm_semantic_mapping_draft.csv"

gold_rules = load_json(gold_file)["rules"]
gemini_rules = load_json(gemini_file)

# Load existing draft links for evaluation only.
with open(mapping_file, "r", encoding="utf-8-sig", newline="") as f:
    mapping_rows = list(csv.DictReader(f))

expected = {}

for row in mapping_rows:
    if row["file"] != gemini_file.name:
        continue

    item = int(row["item"])

    expected[item] = {
        value.strip()
        for value in row["matched_reference_ids"].split(";")
        if value.strip()
    }


def evaluate_method(method):
    """
    Evaluate candidate recall, candidate volume,
    and ranking of expected reference rules.
    """

    total_links = 0
    recovered_links = 0
    total_candidates = 0
    top1_hits = 0
    top3_hits = 0
    missing_links = []

    for item, model_rule in enumerate(gemini_rules, start=1):

        candidates = method(model_rule, gold_rules)

        predicted = [
            candidate["gold_id"]
            for candidate in candidates
        ]

        expected_ids = expected.get(item, set())

        total_links += len(expected_ids)
        total_candidates += len(predicted)

        recovered = expected_ids & set(predicted)
        recovered_links += len(recovered)

        for gold_id in expected_ids - set(predicted):
            missing_links.append((item, gold_id))

        # Top-k measures are item-level hit rates.
        if expected_ids:
            if expected_ids & set(predicted[:1]):
                top1_hits += 1

            if expected_ids & set(predicted[:3]):
                top3_hits += 1

    item_count = len(gemini_rules)
    mapped_item_count = sum(bool(ids) for ids in expected.values())

    return {
        "candidate_recall": (
            recovered_links / total_links if total_links else 0
        ),
        "average_candidates": (
            total_candidates / item_count if item_count else 0
        ),
        "top1_hit_rate": (
            top1_hits / mapped_item_count if mapped_item_count else 0
        ),
        "top3_hit_rate": (
            top3_hits / mapped_item_count if mapped_item_count else 0
        ),
        "missing_links": missing_links,
    }


methods = {
    "Code-only": discover_candidates,
    "Hybrid": discover_candidates_hybrid,
}

print("\n--- Candidate Discovery Method Comparison ---")

for name, method in methods.items():

    result = evaluate_method(method)

    print(f"\nMethod: {name}")
    print("Candidate Recall:",
          round(result["candidate_recall"], 4))
    print("Average Candidates:",
          round(result["average_candidates"], 2))
    print("Top-1 Hit Rate:",
          round(result["top1_hit_rate"], 4))
    print("Top-3 Hit Rate:",
          round(result["top3_hit_rate"], 4))
    print("Missing Links:", result["missing_links"])
