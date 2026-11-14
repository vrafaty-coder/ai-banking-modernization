
"""
Prepare the first real semantic-judging case.

Read verified COBOL source lines and combine them
with the frozen Gold Standard and Gemini extraction.

No API calls are made.
"""

import json
from pathlib import Path

from rule_parser import load_json
from judge_input import build_judge_input
from source_context_loader import load_source_lines


project_root = Path(__file__).resolve().parent.parent

gold_file = project_root / "ai" / "tx01_gold_standard_v1.0.json"
gemini_file = project_root / "ai" / "tx01_llm_rules.json"
source_file = project_root / "cobol" / "programs" / "TX01.cbl"

gold_rules = load_json(gold_file)["rules"]
gemini_rules = load_json(gemini_file)

# Select the first Gemini rule and its reference rule.
model_rule = gemini_rules[0]

gold_rule = next(
    rule for rule in gold_rules
    if rule["id"] == "BR-TX01-001"
)

# Read a small source window around the reference evidence.
source_context = load_source_lines(
    source_file,
    start_line=60,
    end_line=70
)

# Verify that the cited Gold Standard snippets match
# the corresponding lines in the actual source file.
source_by_line = {
    entry["line"]: entry["text"]
    for entry in source_context["lines"]
}

for evidence in gold_rule["evidence"]:
    if evidence["file"] != source_file.name:
        continue

    line_number = evidence["line"]
    expected_snippet = evidence["snippet"]

    actual_line = source_by_line.get(line_number)

    if actual_line is None:
        raise ValueError(
            f"Missing source line: {line_number}"
        )

    if expected_snippet.strip() not in actual_line.strip():
        raise ValueError(
            f"Evidence mismatch at line {line_number}"
        )

# Build the structured judging request.
judge_case = build_judge_input(
    model_rule,
    gold_rule,
    source_context
)

output_file = (
    project_root / "evaluation" / "tx01_judge_case_item1.json"
)

output_file.write_text(
    json.dumps(judge_case, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("\n--- Judge Case Preparation ---")
print("Gemini item:", 1)
print("Reference rule:", gold_rule["id"])
print("Source file:", source_file.name)
print("Source lines:", "60-70")
print("Gold evidence verification: PASSED")
print("Saved:", output_file)
