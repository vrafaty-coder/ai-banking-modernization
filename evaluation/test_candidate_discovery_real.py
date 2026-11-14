
"""
Candidate Discovery Experiment

Evaluate automatic candidate generation against
the existing draft mapping.

The draft mapping is used only for comparison,
not for candidate generation.
"""

import csv
from pathlib import Path

from rule_parser import load_json
from candidate_discovery import discover_candidates


# ---------------------------------------------------------
# 1. Define project paths
# ---------------------------------------------------------

project_root = Path(__file__).resolve().parent.parent
ai_dir = project_root / "ai"
evaluation_dir = project_root / "evaluation"

gold_file = ai_dir / "tx01_gold_standard_v1.0.json"
gemini_file = ai_dir / "tx01_llm_rules.json"

mapping_file = (
    evaluation_dir / "tx01_llm_semantic_mapping_draft.csv"
)


# ---------------------------------------------------------
# 2. Load the real rule datasets
# ---------------------------------------------------------

gold_data = load_json(gold_file)
gemini_rules = load_json(gemini_file)

gold_rules = gold_data["rules"]


# ---------------------------------------------------------
# 3. Load draft mappings for evaluation only
# ---------------------------------------------------------

with open(mapping_file, "r", encoding="utf-8-sig", newline="") as f:
    mapping_rows = list(csv.DictReader(f))

# Keep mappings for the selected Gemini run.
run_mappings = [
    row for row in mapping_rows
    if row["file"] == gemini_file.name
]

# Build a lookup from Gemini item number to reference IDs.
draft_lookup = {}

for row in run_mappings:
    item_number = int(row["item"])

    draft_lookup[item_number] = {
        value.strip()
        for value in row["matched_reference_ids"].split(";")
        if value.strip()
    }


# ---------------------------------------------------------
# 4. Generate candidates independently
# ---------------------------------------------------------

total_expected_links = 0
total_found_links = 0
total_candidates = 0
missing_links = []

print("\n--- Candidate Discovery Experiment ---")

for item_number, model_rule in enumerate(
    gemini_rules, start=1
):

    # Discover candidates using only model and Gold rules.
    candidates = discover_candidates(
        model_rule,
        gold_rules
    )

    # Collect the generated Gold Standard IDs.
    predicted_ids = {
        candidate["gold_id"]
        for candidate in candidates
    }

    # Read the draft reference links for evaluation.
    expected_ids = draft_lookup.get(
        item_number, set()
    )

    # Find which draft links were recovered.
    recovered_ids = expected_ids & predicted_ids

    # Find draft links missing from the candidate set.
    missed_ids = expected_ids - predicted_ids

    # Update aggregate counters.
    total_expected_links += len(expected_ids)
    total_found_links += len(recovered_ids)
    total_candidates += len(predicted_ids)

    # Record missing links for later analysis.
    for gold_id in sorted(missed_ids):
        missing_links.append((item_number, gold_id))

    # Display candidate IDs for this item.
    print(
        f"Item {item_number}: "
        f"Candidates={sorted(predicted_ids)} | "
        f"Recovered={len(recovered_ids)}/{len(expected_ids)}"
    )


# ---------------------------------------------------------
# 5. Calculate diagnostic metrics
# ---------------------------------------------------------

# Avoid division by zero if the draft mapping is empty.
candidate_recall = (
    total_found_links / total_expected_links
    if total_expected_links else 0.0
)

average_candidates = (
    total_candidates / len(gemini_rules)
    if gemini_rules else 0.0
)

print("\n--- Candidate Discovery Summary ---")
print("Draft candidate links:", total_expected_links)
print("Recovered draft links:", total_found_links)
print("Candidate recall:", round(candidate_recall, 4))
print("Average candidates per item:", round(average_candidates, 2))
print("Missing candidate links:", missing_links)
