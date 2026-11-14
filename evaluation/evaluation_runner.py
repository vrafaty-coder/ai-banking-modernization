
"""
Evaluation Runner

Run structural diagnostics for all mapped rule pairs.

This script does not calculate final precision,
recall, or F1 scores.
"""

import csv
from pathlib import Path

from rule_parser import load_json
from semantic_matcher import compare_rules


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

report_file = (
    evaluation_dir / "tx01_matching_diagnostics.csv"
)


# ---------------------------------------------------------
# 2. Load the reference and model rules
# ---------------------------------------------------------

gold_data = load_json(gold_file)
gemini_rules = load_json(gemini_file)

# Create a lookup dictionary for reference rules.
gold_lookup = {
    rule["id"]: rule
    for rule in gold_data["rules"]
}


# ---------------------------------------------------------
# 3. Load candidate mappings
# ---------------------------------------------------------

with open(mapping_file, "r", encoding="utf-8-sig", newline="") as f:
    all_mappings = list(csv.DictReader(f))

# Keep only mappings for the selected model output.
run_mappings = [
    row for row in all_mappings
    if row["file"] == gemini_file.name
]


# ---------------------------------------------------------
# 4. Evaluate all candidate pairs
# ---------------------------------------------------------

results = []

for row in run_mappings:

    # Convert the one-based item number to a list index.
    item_number = int(row["item"])
    gemini_rule = gemini_rules[item_number - 1]

    # A model item may map to multiple reference rules.
    reference_ids = [
        value.strip()
        for value in row["matched_reference_ids"].split(";")
        if value.strip()
    ]

    for gold_id in reference_ids:

        # Retrieve the reference rule.
        gold_rule = gold_lookup[gold_id]

        # Run the reusable diagnostic function.
        comparison = compare_rules(
            gemini_rule,
            gold_rule
        )

        # Store the comparison and its findings.
        results.append({
            "source_file": gemini_file.name,
            "gemini_item": item_number,
            "gold_id": gold_id,
            "condition_equal": comparison["condition_equal"],
            "missing_codes": ";".join(
                comparison["missing_codes"]
            ),
            "goback_equal": comparison["goback_equal"],
            "findings": ";".join(comparison["findings"]),
            "semantic_verdict": "NEEDS_REVIEW"
        })


# ---------------------------------------------------------
# 5. Export the diagnostic report
# ---------------------------------------------------------

fieldnames = [
    "source_file",
    "gemini_item",
    "gold_id",
    "condition_equal",
    "missing_codes",
    "goback_equal",
    "findings",
    "semantic_verdict"
]

with open(report_file, "w", encoding="utf-8-sig", newline="") as f:

    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # Write the header and diagnostic rows.
    writer.writeheader()
    writer.writerows(results)


# ---------------------------------------------------------
# 6. Display the summary
# ---------------------------------------------------------

print("\n--- Evaluation Runner Summary ---")
print("Gold Standard rules:", len(gold_lookup))
print("Gemini rules:", len(gemini_rules))
print("Candidate comparisons:", len(results))
print("Report saved:", report_file)
print("Final semantic verdicts: not assigned")
