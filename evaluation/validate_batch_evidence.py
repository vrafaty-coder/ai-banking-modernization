
"""
Validate Gold Standard evidence against actual COBOL files.

No API calls. No modifications to frozen research artifacts.
"""

import csv
from pathlib import Path

from rule_parser import load_json


ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = ROOT / "evaluation"

GOLD_FILE = ROOT / "ai" / "tx01_gold_standard_v1.0.json"
DRY_RUN_FILE = EVAL_DIR / "tx01_batch_judge_dry_run.csv"
OUTPUT_FILE = EVAL_DIR / "tx01_evidence_validation.csv"

gold_rules = {
    rule["id"]: rule
    for rule in load_json(GOLD_FILE)["rules"]
}

with DRY_RUN_FILE.open(
    encoding="utf-8-sig", newline=""
) as file:
    comparisons = list(csv.DictReader(file))


def resolve_source(file_name):
    """Resolve source files within known COBOL directories."""

    if Path(file_name).name != file_name:
        raise ValueError(f"Unsafe source filename: {file_name}")

    candidates = [
        ROOT / "cobol" / "programs" / file_name,
        ROOT / "cobol" / "copybooks" / file_name,
    ]

    matches = [path for path in candidates if path.is_file()]

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected one source file for {file_name}; "
            f"found {len(matches)}"
        )

    return matches[0]


def validate_evidence(rule):
    """Check source filename, line number and cited snippet."""

    evidence = rule.get("evidence", [])

    if not evidence:
        return "NO_EVIDENCE", 0

    verified = 0

    for entry in evidence:
        path = resolve_source(entry["file"])
        lines = path.read_text(encoding="utf-8").splitlines()

        line_number = int(entry["line"])

        if not 1 <= line_number <= len(lines):
            return "INVALID_LINE", verified

        expected = entry["snippet"].strip()
        actual = lines[line_number - 1].strip()

        if not expected or expected not in actual:
            return "SNIPPET_MISMATCH", verified

        verified += 1

    return "VERIFIED", verified


results = []

for comparison in comparisons:
    gold_id = comparison["gold_id"]

    if gold_id not in gold_rules:
        raise ValueError(f"Unknown Gold ID: {gold_id}")

    status, verified_count = validate_evidence(
        gold_rules[gold_id]
    )

    results.append({
        "gemini_item": comparison["gemini_item"],
        "gold_id": gold_id,
        "evidence_status": status,
        "verified_snippets": verified_count,
        "context_sufficiency": "NOT_ASSESSED",
    })

with OUTPUT_FILE.open(
    "w", encoding="utf-8", newline=""
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=list(results[0].keys())
    )
    writer.writeheader()
    writer.writerows(results)

print("\n--- TX01 Evidence Validation ---")
print("Comparisons:", len(results))

for status in sorted(set(r["evidence_status"] for r in results)):
    count = sum(
        r["evidence_status"] == status
        for r in results
    )
    print(f"{status}: {count}")

print("Context sufficiency: NOT ASSESSED")
print("API calls made: 0")
print("Saved:", OUTPUT_FILE)
