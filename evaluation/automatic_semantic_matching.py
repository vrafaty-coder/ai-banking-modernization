
############################################ Semantic Matching Engine #########################################

"""
Automatic Semantic Matching Engine

Purpose:
    Prepare Gemini-extracted rules for systematic
    comparison against the frozen Gold Standard.

This first version extracts structural signals.
It does NOT assign FULL/PARTIAL/NONE automatically.
"""

import json
import re
from pathlib import Path


# ---------------------------------------------------------
# 1. Define project paths
# ---------------------------------------------------------

# Find the project root relative to this Python script.
project_root = Path(__file__).resolve().parent.parent

# Define input files.
gold_file = project_root / "ai" / "tx01_gold_standard_v1.0.json"
gemini_file = project_root / "ai" / "tx01_llm_rules.json"


# ---------------------------------------------------------
# 2. Load JSON data
# ---------------------------------------------------------

# Read the frozen Gold Standard.
with open(gold_file, "r", encoding="utf-8") as f:
    gold_data = json.load(f)

# Read the existing Gemini extraction.
# No new Gemini API call is required.
with open(gemini_file, "r", encoding="utf-8") as f:
    gemini_rules = json.load(f)

gold_rules = gold_data["rules"]


# ---------------------------------------------------------
# 3. Normalize rule text
# ---------------------------------------------------------

def normalize_text(text):
    """
    Normalize text for basic structural comparison.

    This function:
        - Converts text to uppercase.
        - Removes extra whitespace.
        - Does not determine semantic equivalence.
    """

    # Convert input into uppercase text.
    text = str(text).upper()

    # Replace multiple whitespace characters with one space.
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading and trailing spaces.
    return text.strip()


# ---------------------------------------------------------
# 4. Extract structural signals
# ---------------------------------------------------------

def extract_signals(rule):
    """
    Extract observable signals from a rule.

    Signals are evidence for later comparison,
    not a final semantic matching decision.
    """

    # Combine the condition and action fields.
    condition = normalize_text(rule.get("condition", ""))
    action = normalize_text(rule.get("action", ""))

    # Detect numeric alert codes in the action.
    # Four-digit values are candidates, not necessarily alerts.
    alert_candidates = re.findall(
        r"\b\d{4}\b",
        action
    )

    # Detect explicit GOBACK instructions.
    has_goback = "GOBACK" in action

    # Detect rollback references.
    has_rollback = "ROLLBACK" in action

    # Return all extracted information.
    return {
        "condition": condition,
        "action": action,
        "alert_candidates": alert_candidates,
        "has_goback": has_goback,
        "has_rollback": has_rollback
    }


# ---------------------------------------------------------
# 5. Process every Gemini rule automatically
# ---------------------------------------------------------

print("\n--- Automatic Rule Processing ---")

for index, rule in enumerate(gemini_rules, start=1):

    # Extract signals from the current Gemini rule.
    signals = extract_signals(rule)

    # Display the rule number and structural signals.
    print(f"\nGemini Item {index}")
    print("Description:", rule.get("rule_description"))
    print("Alert candidates:", signals["alert_candidates"])
    print("Has GOBACK:", signals["has_goback"])
    print("Has ROLLBACK:", signals["has_rollback"])


# ---------------------------------------------------------
# 6. Display processing summary
# ---------------------------------------------------------

print("\n--- Processing Summary ---")
print("Gold Standard rules:", len(gold_rules))
print("Gemini rules processed:", len(gemini_rules))
print("Structural extraction completed.")


# ---------------------------------------------------------
# 7. Load the existing candidate mapping
# ---------------------------------------------------------

import csv

# This CSV contains candidate links between Gemini items
# and Gold Standard rules. These links are not final matches.
mapping_file = (
    project_root
    / "evaluation"
    / "tx01_llm_semantic_mapping_draft.csv"
)

# Read the mapping table as dictionaries.
with open(mapping_file, "r", encoding="utf-8-sig", newline="") as f:
    mappings = list(csv.DictReader(f))

# Select only the rows for the current Gemini extraction.
selected_file = gemini_file.name

run_mappings = [
    row for row in mappings
    if row["file"] == selected_file
]

# Build a lookup table to find Gold rules by their IDs.
gold_lookup = {
    rule["id"]: rule
    for rule in gold_rules
}


# ---------------------------------------------------------
# 8. Compare structural signals
# ---------------------------------------------------------

def compare_signals(gemini_rule, gold_rule):
    """
    Compare observable structural signals.

    This is a diagnostic comparison, not a final
    semantic-equivalence decision.
    """

    # Extract signals from both rules.
    gemini = extract_signals(gemini_rule)
    gold = extract_signals(gold_rule)

    # Compare normalized conditions.
    # False does not necessarily mean semantic mismatch.
    condition_equal = (
        gemini["condition"] == gold["condition"]
    )

    # Compare candidate numeric alert codes.
    gemini_alerts = set(gemini["alert_candidates"])
    gold_alerts = set(gold["alert_candidates"])

    # Check whether the model includes every reference code.
    alert_codes_covered = gold_alerts.issubset(gemini_alerts)

    # Check whether GOBACK appears in both action fields.
    # This is a text signal, not proof of equivalent control flow.
    goback_equal = (
        gemini["has_goback"] == gold["has_goback"]
    )

    return {
        "condition_equal": condition_equal,
        "alert_codes_covered": alert_codes_covered,
        "goback_equal": goback_equal
    }


# ---------------------------------------------------------
# 9. Compare all mapped Gemini rules
# ---------------------------------------------------------

comparison_results = []

for row in run_mappings:

    # CSV item numbers start at 1; Python indexes start at 0.
    item_number = int(row["item"])
    gemini_rule = gemini_rules[item_number - 1]

    # One Gemini rule may be linked to multiple Gold rules.
    reference_ids = [
        rule_id.strip()
        for rule_id in row["matched_reference_ids"].split(";")
        if rule_id.strip()
    ]

    for reference_id in reference_ids:

        # Retrieve the corresponding reference rule.
        gold_rule = gold_lookup[reference_id]

        # Perform the structural comparison.
        result = compare_signals(gemini_rule, gold_rule)

        # Store the result with identifying information.
        comparison_results.append({
            "item": item_number,
            "gold_id": reference_id,
            **result
        })


# ---------------------------------------------------------
# 10. Display the diagnostic report
# ---------------------------------------------------------

print("\n--- Structural Comparison Report ---")

for result in comparison_results:
    print(
        f"Item {result['item']} -> {result['gold_id']} | "
        f"Condition: {result['condition_equal']} | "
        f"Alerts: {result['alert_codes_covered']} | "
        f"GOBACK: {result['goback_equal']}"
    )

print("\nComparisons completed:", len(comparison_results))



# ---------------------------------------------------------
# 11. Demonstrate text normalization vs semantic equivalence
# ---------------------------------------------------------

# Define two conditions with the same logical meaning.
# COBOL-style NOT = and != both represent inequality.
condition_a = 'WS-ACC-STATUS NOT = "00"'
condition_b = 'WS-ACC-STATUS != "00"'

# Apply our existing text normalization function.
normalized_a = normalize_text(condition_a)
normalized_b = normalize_text(condition_b)

# Display the original conditions.
print("\n--- Normalization Demonstration ---")
print("Original A:", condition_a)
print("Original B:", condition_b)

# Display the normalized conditions.
print("\nNormalized A:", normalized_a)
print("Normalized B:", normalized_b)

# Python compares the resulting strings character by character.
print("\nTextually equal:", normalized_a == normalized_b)

# Both conditions express inequality, but our current
# normalization function does not understand that meaning.
print("Expected logical equivalence: True")


# ---------------------------------------------------------
# 13. Normalize equivalent inequality operators
# ---------------------------------------------------------

def normalize_condition(condition):
    """
    Normalize simple inequality expressions.

    This is a limited syntactic normalization,
    not a complete semantic equivalence checker.
    """

    # Apply our existing text normalization.
    condition = normalize_text(condition)

    # Convert COBOL-style NOT = into !=.
    # \s* allows optional spaces between NOT and =.
    condition = re.sub(r"\bNOT\s*=", "!=", condition)

    # Return the normalized condition.
    return condition


# Normalize both example conditions.
result_a = normalize_condition(condition_a)
result_b = normalize_condition(condition_b)

print("\n--- Improved Condition Normalization ---")
print("Normalized A:", result_a)
print("Normalized B:", result_b)

# Compare the normalized strings.
print("Equal after normalization:", result_a == result_b)

# Gemini Item 2 is linked to Gold TECH-TX01-001.
gemini_condition = gemini_rules[1]["condition"]
gold_condition = gold_lookup["TECH-TX01-001"]["condition"]

print("\n--- Real Condition Comparison: Item 2 ---")
print("Gemini condition:", gemini_condition)
print("Gold condition:", gold_condition)

print("\nNormalized Gemini:", normalize_text(gemini_condition))
print("Normalized Gold:", normalize_text(gold_condition))


# ---------------------------------------------------------
# 14. Inspect the context of a real Gemini rule
# ---------------------------------------------------------

# Retrieve Gemini Item 2.
item_2 = gemini_rules[1]

# Retrieve the corresponding Gold Standard rule.
gold_2 = gold_lookup["TECH-TX01-001"]

# Show the complete extracted rule and its evidence.
print("\n--- Gemini Item 2 Context ---")
print("Description:", item_2.get("rule_description"))
print("Condition:", item_2.get("condition"))
print("Action:", item_2.get("action"))
print("Evidence:", item_2.get("evidence"))

# Show the reference rule's behavior.
print("\n--- Gold Standard Context ---")
print("Description:", gold_2.get("rule_description"))
print("Condition:", gold_2.get("condition"))
print("Action:", gold_2.get("action"))


# ---------------------------------------------------------
# 15. Detect file operations in extracted evidence
# ---------------------------------------------------------

def extract_file_operations(evidence):
    """
    Detect COBOL file operations from an evidence snippet.

    This function identifies explicit file operations.
    It does not independently prove that the evidence
    matches the original COBOL source.
    """

    # Normalize the evidence text.
    text = normalize_text(evidence)

    # Match OPEN statements with their file names.
    # Support common COBOL modes: INPUT, OUTPUT, I-O, EXTEND.
    pattern = (
        r"\bOPEN\s+"
        r"(?:INPUT|OUTPUT|I-O|EXTEND)\s+"
        r"([A-Z][A-Z0-9-]*)"
    )

    # Extract all matching file names.
    opened_files = re.findall(pattern, text)

    return {
        "opened_files": opened_files
    }


# ---------------------------------------------------------
# 16. Test the function using Gemini Item 2
# ---------------------------------------------------------

# Extract file operations from the actual evidence.
operations = extract_file_operations(item_2["evidence"])

print("\n--- File Operation Detection ---")
print("Opened files:", operations["opened_files"])

# Check whether ACCOUNT-FILE is explicitly opened.
print(
    "ACCOUNT-FILE opened:",
    "ACCOUNT-FILE" in operations["opened_files"]
)


# ---------------------------------------------------------
# 17. Build a structural evidence report for all rules
# ---------------------------------------------------------

# Store one diagnostic record per candidate rule pair.
evidence_report = []

for row in run_mappings:

    # Convert the Gemini item number to an integer.
    item_number = int(row["item"])

    # Retrieve the corresponding Gemini rule.
    gemini_rule = gemini_rules[item_number - 1]

    # Extract condition/action signals.
    signals = extract_signals(gemini_rule)

    # Extract file operations from the evidence snippet.
    operations = extract_file_operations(
        gemini_rule.get("evidence", "")
    )

    # Read all candidate Gold Standard IDs.
    reference_ids = [
        rule_id.strip()
        for rule_id in row["matched_reference_ids"].split(";")
        if rule_id.strip()
    ]

    # Create a separate record for each candidate pair.
    for reference_id in reference_ids:

        evidence_report.append({
            "source_file": selected_file,
            "gemini_item": item_number,
            "gold_id": reference_id,
            "condition": signals["condition"],
            "alert_candidates": ";".join(
                signals["alert_candidates"]
            ),
            "has_goback": signals["has_goback"],
            "has_rollback": signals["has_rollback"],
            "opened_files": ";".join(
                operations["opened_files"]
            ),
            "semantic_status": "NEEDS_REVIEW"
        })


# ---------------------------------------------------------
# 18. Save the report as a CSV file
# ---------------------------------------------------------

report_file = (
    project_root
    / "evaluation"
    / "tx01_structural_evidence_report.csv"
)

# Define the output columns in a stable order.
fieldnames = [
    "source_file",
    "gemini_item",
    "gold_id",
    "condition",
    "alert_candidates",
    "has_goback",
    "has_rollback",
    "opened_files",
    "semantic_status"
]

# Write the report using UTF-8 encoding.
with open(report_file, "w", encoding="utf-8-sig", newline="") as f:

    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # Write the CSV header.
    writer.writeheader()

    # Write all diagnostic records.
    writer.writerows(evidence_report)


# ---------------------------------------------------------
# 19. Display the report summary
# ---------------------------------------------------------

print("\n--- Structural Evidence Report ---")
print("Candidate pairs:", len(evidence_report))
print("Report saved:", report_file)

# Count rules with detected file-opening operations.
open_count = sum(
    bool(record["opened_files"])
    for record in evidence_report
)

print("Pairs with OPEN evidence:", open_count)
print("Initial semantic status: NEEDS_REVIEW")


# ---------------------------------------------------------
# 20. Compare alert codes for every candidate pair
# ---------------------------------------------------------

def compare_alert_codes(gemini_rule, gold_rule):
    """
    Compare numeric alert-code candidates.

    This function returns a diagnostic result.
    It does not determine full semantic equivalence.
    """

    # Extract structural signals from both rules.
    gemini_signals = extract_signals(gemini_rule)
    gold_signals = extract_signals(gold_rule)

    # Convert candidate codes into sets.
    gemini_codes = set(
        gemini_signals["alert_candidates"]
    )
    gold_codes = set(
        gold_signals["alert_candidates"]
    )

    # If the Gold Standard does not specify a numeric
    # alert code, we cannot make a code-based decision.
    if not gold_codes:
        return "NOT_APPLICABLE"

    # Find reference codes missing from Gemini's action.
    missing_codes = gold_codes - gemini_codes

    # Report whether every reference code is present.
    if missing_codes:
        return "MISSING_CODE"

    return "CODES_PRESENT"


# ---------------------------------------------------------
# 21. Run alert-code checks for all mapped rules
# ---------------------------------------------------------

print("\n--- Automatic Alert Code Checks ---")

for row in run_mappings:

    # Identify the Gemini rule.
    item_number = int(row["item"])
    gemini_rule = gemini_rules[item_number - 1]

    # Process every candidate reference rule.
    reference_ids = [
        rule_id.strip()
        for rule_id in row["matched_reference_ids"].split(";")
        if rule_id.strip()
    ]

    for reference_id in reference_ids:

        # Retrieve the Gold Standard rule.
        gold_rule = gold_lookup[reference_id]

        # Perform the automatic diagnostic check.
        result = compare_alert_codes(
            gemini_rule,
            gold_rule
        )

        print(
            f"Item {item_number} -> "
            f"{reference_id}: {result}"
        )


# ---------------------------------------------------------
# 22. Group candidate matches by Gold Standard rule
# ---------------------------------------------------------

from collections import defaultdict

# Create a dictionary that automatically initializes lists.
matches_by_gold = defaultdict(list)

# Group Gemini items by their candidate Gold Standard IDs.
for row in run_mappings:

    # Read the Gemini item number.
    item_number = int(row["item"])

    # Split multiple reference IDs, if present.
    reference_ids = [
        rule_id.strip()
        for rule_id in row["matched_reference_ids"].split(";")
        if rule_id.strip()
    ]

    # Register this Gemini item under every candidate rule.
    for reference_id in reference_ids:
        matches_by_gold[reference_id].append(item_number)


# ---------------------------------------------------------
# 23. Identify references with multiple candidate items
# ---------------------------------------------------------

print("\n--- Multiple Candidate Matches ---")

for gold_id, item_numbers in matches_by_gold.items():

    # Only display references linked to multiple items.
    if len(item_numbers) > 1:
        print(
            f"{gold_id}: Gemini items {item_numbers}"
        )


# ---------------------------------------------------------
# 24. Check whether alert codes are covered collectively
# ---------------------------------------------------------

def compare_group_alert_codes(item_numbers, gold_rule):
    """
    Check whether the combined actions of candidate
    Gemini items contain all reference alert codes.

    This is a coverage diagnostic, not proof that the
    rules are semantically equivalent.
    """

    # Extract the required alert-code candidates.
    gold_codes = set(
        extract_signals(gold_rule)["alert_candidates"]
    )

    # Collect codes from every related Gemini item.
    combined_codes = set()

    for item_number in item_numbers:

        # Convert the one-based item number to a list index.
        gemini_rule = gemini_rules[item_number - 1]

        # Add the item's detected codes to the set.
        combined_codes.update(
            extract_signals(gemini_rule)["alert_candidates"]
        )

    # Determine which reference codes remain missing.
    missing_codes = gold_codes - combined_codes

    return {
        "required_codes": sorted(gold_codes),
        "combined_codes": sorted(combined_codes),
        "missing_codes": sorted(missing_codes)
    }


# ---------------------------------------------------------
# 25. Display collective coverage diagnostics
# ---------------------------------------------------------

print("\n--- Collective Alert Coverage ---")

for gold_id, item_numbers in matches_by_gold.items():

    # Focus on reference rules with multiple candidates.
    if len(item_numbers) <= 1:
        continue

    # Retrieve the Gold Standard rule.
    gold_rule = gold_lookup[gold_id]

    # Calculate collective code coverage.
    result = compare_group_alert_codes(
        item_numbers,
        gold_rule
    )

    print("\nGold rule:", gold_id)
    print("Gemini items:", item_numbers)
    print("Required codes:", result["required_codes"])
    print("Combined codes:", result["combined_codes"])
    print("Missing codes:", result["missing_codes"])
