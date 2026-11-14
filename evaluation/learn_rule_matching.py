
import json
from pathlib import Path

# Project root directory
project_root = Path(__file__).resolve().parent.parent

# Gold Standard file
gold_file = project_root / "ai" / "tx01_gold_standard_v1.0.json"

# Read JSON
with open(gold_file, "r", encoding="utf-8") as f:
    gold_data = json.load(f)

# Explore the structure
print("Data type:", type(gold_data).__name__)
print("Top-level keys:", list(gold_data.keys()))

# Extract rules from Gold Standard
gold_rules = gold_data["rules"]

print("\nNumber of rules:", len(gold_rules))
print("Rules data type:", type(gold_rules).__name__)

# Explore the first rule
first_rule = gold_rules[0]

print("\nFirst rule:")
print(json.dumps(first_rule, indent=2, ensure_ascii=False))


# Read the existing Gemini output
gemini_file = project_root / "ai" / "tx01_llm_rules.json"

with open(gemini_file, "r", encoding="utf-8") as f:
    gemini_data = json.load(f)

print("\nGemini data type:", type(gemini_data).__name__)

if isinstance(gemini_data, dict):
    print("Gemini top-level keys:", list(gemini_data.keys()))
elif isinstance(gemini_data, list):
    print("Number of Gemini items:", len(gemini_data))
    if gemini_data:
        print("First item:", json.dumps(
            gemini_data[0], indent=2, ensure_ascii=False
        ))


gold_rule = gold_rules[0]
gemini_rule = gemini_data[0]

# Compare descriptions as plain text
description_equal = (
    gold_rule["rule_description"]
    == gemini_rule["rule_description"]
)

# Compare conditions as plain text
condition_equal = (
    gold_rule["condition"]
    == gemini_rule["condition"]
)

print("\n--- First Rule Comparison ---")
print("Description equal:", description_equal)
print("Condition equal:", condition_equal)


# Create our first reviewed semantic mapping
semantic_mapping = {
    "gold_rule_id": "BR-TX01-001",
    "gemini_rule_index": 0,
    "match_status": "FULL",
    "reason": (
        "Same zero-amount condition, alert code 1004, "
        "error message, and GOBACK behavior."
    )
}

# Access the mapping fields
print("\n--- Semantic Mapping ---")
print("Gold rule:", semantic_mapping["gold_rule_id"])
print("Gemini index:", semantic_mapping["gemini_rule_index"])
print("Match status:", semantic_mapping["match_status"])
print("Reason:", semantic_mapping["reason"])


gold_ids = {rule["id"] for rule in gold_rules}

assert semantic_mapping["gold_rule_id"] in gold_ids, (
    "Gold rule ID does not exist!"
)

assert 0 <= semantic_mapping["gemini_rule_index"] < len(gemini_data), (
    "Gemini rule index is invalid!"
)

assert semantic_mapping["match_status"] in {"FULL", "PARTIAL", "NONE"}, (
    "Invalid match status!"
)

print("\nSemantic mapping validation passed!")

matched_gold_ids = [
    "BR-TX01-001",
    "BR-TX01-001",
    "BR-TX01-001"
]

tp = len(set(matched_gold_ids))
fp = len(matched_gold_ids) - tp

print("TP:", tp)
print("FP:", fp)