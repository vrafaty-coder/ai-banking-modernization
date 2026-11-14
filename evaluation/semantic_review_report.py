
"""
Create a consolidated semantic review report.

Preserve existing human-reviewed verdicts.
Do not infer final verdicts from diagnostic signals.
"""

import csv
from pathlib import Path

evaluation_dir = Path(__file__).resolve().parent

review_file = evaluation_dir / "tx01_strict_semantic_review.csv"
diagnostics_file = evaluation_dir / "tx01_matching_diagnostics.csv"
output_file = evaluation_dir / "tx01_semantic_review_report.csv"


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


reviews = read_csv(review_file)
diagnostics = read_csv(diagnostics_file)

# Match diagnostics to the corresponding Gemini item.
diagnostics_by_item = {
    str(row["gemini_item"]).strip(): row
    for row in diagnostics
    if row["source_file"] == "tx01_llm_rules.json"
}

# Preserve every existing review row.
report = []

for review in reviews:
    item = str(review["item"]).strip()
    diagnostic = diagnostics_by_item.get(item, {})

    report.append({
        **review,
        "diagnostic_findings": diagnostic.get("findings", ""),
        "diagnostic_missing_codes": diagnostic.get(
            "missing_codes", ""
        ),
        "diagnostic_condition_equal": diagnostic.get(
            "condition_equal", ""
        ),
        "diagnostic_goback_equal": diagnostic.get(
            "goback_equal", ""
        ),
    })

fieldnames = [
    "item",
    "gold_id",
    "role",
    "status",
    "diagnostic_findings",
    "diagnostic_missing_codes",
    "diagnostic_condition_equal",
    "diagnostic_goback_equal",
]

with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(report)

print("\n--- Semantic Review Report ---")
print("Review rows:", len(reviews))
print("Diagnostic rows:", len(diagnostics))
print("Report rows:", len(report))
print("Reviewed rows:", sum(
    row["status"] in {"FULL", "PARTIAL", "NONE"}
    for row in report
))
print("Pending rows:", sum(
    row["status"] == "PENDING"
    for row in report
))
print("Saved:", output_file)
