"""Prepare TX01 LLM-only judging cases without calling any API.

Run from the project root:
    python evaluation/prepare_tx01_batch.py

Existing case files are never overwritten. Draft mappings are not final verdicts.
"""

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVAL = ROOT / "evaluation"
MODEL = ROOT / "ai" / "tx01_llm_rules.json"
GOLD = ROOT / "ai" / "tx01_gold_standard_v1.0.json"
MAPPING = EVAL / "tx01_llm_semantic_mapping_draft.csv"
SOURCE = ROOT / "cobol" / "programs" / "TX01.cbl"

# These fixed ranges were selected for the TX01 pilot only.
# They are source-context supplements, not RAG retrieval results.
EXTRA_RANGES = {
    "INT-TX01-001": [(133, 174), (214, 223)],
    "INT-TX01-002": [(177, 213)],
    "INT-TX01-003": [(177, 213)],
    "BR-TX01-007": [(133, 174)],
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def merge_ranges(ranges):
    merged = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged


def build_context(gold_rule, source_lines, padding=5):
    ranges = []
    for evidence in gold_rule.get("evidence", []):
        if evidence["file"] != SOURCE.name:
            raise ValueError(f"Unexpected evidence file for {gold_rule['id']}: {evidence['file']}")
        line = int(evidence["line"])
        if not 1 <= line <= len(source_lines):
            raise ValueError(f"Invalid evidence line for {gold_rule['id']}: {line}")
        snippet = evidence["snippet"].strip()
        if not snippet or snippet not in source_lines[line - 1].strip():
            raise ValueError(f"Evidence mismatch: {gold_rule['id']} at line {line}")
        ranges.append((max(1, line - padding), min(len(source_lines), line + padding)))
    if not ranges:
        raise ValueError(f"Missing source evidence: {gold_rule['id']}")
    ranges.extend(EXTRA_RANGES.get(gold_rule["id"], []))
    result = []
    for start, end in merge_ranges(ranges):
        if end > len(source_lines):
            raise ValueError(f"Source range exceeds file: {start}-{end}")
        result.append({
            "file": SOURCE.name,
            "start_line": start,
            "end_line": end,
            "lines": [{"line": n, "text": source_lines[n - 1]}
                      for n in range(start, end + 1)],
        })
    return {
        "file": SOURCE.name,
        "reference_id": gold_rule["id"],
        "ranges": result,
        "context_strategy": "verified_evidence_plus_fixed_ranges",
        "context_sufficiency": "NOT_ASSESSED",
    }


def main():
    model_data = read_json(MODEL)
    model_rules = model_data["rules"] if isinstance(model_data, dict) else model_data
    gold_data = read_json(GOLD)
    gold_rules = {r["id"]: r for r in gold_data["rules"]}
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    with MAPPING.open(encoding="utf-8-sig", newline="") as handle:
        mapping_rows = list(csv.DictReader(handle))

    selected = [r for r in mapping_rows if r.get("file", "").strip() == MODEL.name]
    if len(selected) != len(model_rules):
        raise ValueError(f"Expected {len(model_rules)} mapping rows, found {len(selected)}")
    item_ids = [int(r["item"]) for r in selected]
    if sorted(item_ids) != list(range(1, len(model_rules) + 1)):
        raise ValueError("Mapping items must cover each extracted rule exactly once")

    # Validate every case before creating any files.
    cases = []
    for row in selected:
        item = int(row["item"])
        ids = [v.strip() for v in row["matched_reference_ids"].split(";") if v.strip()]
        if len(ids) != 1 or ids[0] not in gold_rules:
            raise ValueError(f"Item {item}: expected one known reference, found {ids}")
        reference = gold_rules[ids[0]]
        case = {
            "reference_rule": {
                key: reference[key] for key in (
                    "id", "category", "rule_description", "condition", "action"
                )
            },
            "extracted_rule": {
                key: model_rules[item - 1].get(key, "") for key in (
                    "category", "rule_description", "condition", "action", "evidence"
                )
            },
            "verified_source_context": build_context(reference, source_lines),
        }
        case["reference_rule"]["evidence"] = reference.get("evidence", [])
        case["reference_rule"]["dependencies"] = reference.get("dependencies", [])
        cases.append((item, ids[0], case))

    created = skipped = 0
    for item, reference_id, case in sorted(cases):
        path = EVAL / f"tx01_judge_case_item{item}.json"
        if path.exists():
            skipped += 1
            print(f"SKIPPED case Item {item}: already exists")
            continue
        with path.open("x", encoding="utf-8") as handle:
            json.dump(case, handle, indent=2, ensure_ascii=False)
        created += 1
        print(f"CREATED case Item {item}: {reference_id}")

    existing_results = [item for item, _, _ in cases
                        if (EVAL / f"tx01_judge_result_item{item}.json").exists()]
    pending = [item for item, _, _ in cases if item not in existing_results]
    duplicates = {ref: count for ref, count in Counter(ref for _, ref, _ in cases).items()
                  if count > 1}
    print("\n--- TX01 Judge Preparation ---")
    print("Total comparisons:", len(cases))
    print("Cases created:", created)
    print("Existing cases preserved:", skipped)
    print("Existing judge results:", existing_results)
    print("Pending judge items:", pending)
    print("Shared reference IDs:", duplicates)
    print("Context sufficiency: NOT ASSESSED")
    print("API calls made: 0")
    print("No judge results or frozen reference files were modified.")


if __name__ == "__main__":
    main()
