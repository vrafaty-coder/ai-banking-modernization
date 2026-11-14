
"""
TX01 Semantic Matching — learning and review preparation

This script reads the frozen Gold Standard and one existing Gemini output,
inspects draft mappings, and prepares human semantic-review records.
It does NOT automatically decide semantic correctness or calculate final metrics.
The existing review CSV is never overwritten by this script.
"""

# JSON files store the structured rules extracted from COBOL.
import json
# pathlib creates file paths that work across operating systems.
from pathlib import Path

# __file__ is this script; parent is evaluation/, parent.parent is project root.
# Using this path avoids depending on the current terminal directory.
# Project root directory
project_root = Path(__file__).resolve().parent.parent

# The reviewed Gold Standard is our reference; do not modify it here.
# Gold Standard file
gold_file = project_root / "ai" / "tx01_gold_standard_v1.0.json"

# json.load() converts JSON into Python objects (dict/list).
# Read JSON
with open(gold_file, "r", encoding="utf-8") as f:
    gold_data = json.load(f)

# Inspect the shape of the loaded data before using its keys.
# Explore the structure
print("Data type:", type(gold_data).__name__)
print("Top-level keys:", list(gold_data.keys()))


# csv provides readers/writers for our mapping and human-review tables.
import csv

# This is a DRAFT association table, NOT a verified FULL/PARTIAL judgment.
# It includes rows from multiple Gemini runs.
mapping_file = (
    project_root
    / "evaluation"
    / "tx01_llm_semantic_mapping_draft.csv"
)

# utf-8-sig also accepts CSV files with a UTF-8 BOM (common in Excel).
# DictReader makes each CSV row a dictionary keyed by column names.
with open(mapping_file, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    mappings = list(reader)

print("\n--- CSV Mapping ---")
print("Number of rows:", len(mappings))

if mappings:
    print("Column names:", list(mappings[0].keys()))
    print("First row:", mappings[0])


# Always filter by model-output filename before comparing runs.
# Select the mappings for one Gemini run
selected_file = "tx01_llm_rules.json"

# List comprehension: keep only rows whose file equals selected_file.
run_mappings = [
    row for row in mappings
    if row["file"] == selected_file
]

print("\n--- Selected Gemini Run ---")
print("Mapping rows:", len(run_mappings))

# A mapping may contain multiple reference IDs separated by semicolons.
# strip() removes surrounding whitespace; empty values are ignored.
for row in run_mappings:
    reference_ids = [
        rule_id.strip()
        for rule_id in row["matched_reference_ids"].split(";")
        if rule_id.strip()
    ]

    print(
        f"Gemini item {row['item']}: "
        f"{reference_ids}"
    )


# Counter counts how often each reference rule ID is mentioned.
from collections import Counter

matched_ids = []

for row in run_mappings:
    ids = [
        rule_id.strip()
        for rule_id in row["matched_reference_ids"].split(";")
        if rule_id.strip()
    ]
    # extend() adds each ID individually (append(ids) would add a nested list).
    matched_ids.extend(ids)

# A repeated reference ID is a review signal, NOT proof of a duplicate rule.
counts = Counter(matched_ids)

duplicates = {
    rule_id: count
    for rule_id, count in counts.items()
    if count > 1
}

print("\n--- Duplicate Matches ---")
print("Total mapped references:", len(matched_ids))
print("Unique reference IDs:", len(counts))
print("Duplicates:", duplicates)


# Dictionary comprehension: key = reference rule ID, value = complete rule.
# This gives direct access without searching the entire list each time.
# Create a lookup dictionary for Gold Standard rules
gold_rules = gold_data["rules"]

gold_lookup = {
    rule["id"]: rule
    for rule in gold_rules
}

print("\n--- Rules for Semantic Review ---")

for row in run_mappings:
    reference_ids = [
        rule_id.strip()
        for rule_id in row["matched_reference_ids"].split(";")
        if rule_id.strip()
    ]

    for reference_id in reference_ids:
        # Retrieve the reference rule using its ID.
        gold_rule = gold_lookup[reference_id]

        print("\nGemini item:", row["item"])
        print("Gold ID:", reference_id)
        print("Gemini rule:", row["model_rule"])
        print("Gold condition:", gold_rule["condition"])
        print("Gold action:", gold_rule["action"])

# Read the original Gemini JSON to inspect full condition/action/evidence.
# The draft CSV only contains a short rule description.
gemini_file = project_root / "ai" / "tx01_llm_rules.json"

with open(gemini_file, "r", encoding="utf-8") as f:
    gemini_rules = json.load(f)

# Inspect the two items associated with the same reference rule.
# CSV item numbers start at 1, while Python list indices start at 0.
for item_number in [11, 14]:
    rule = gemini_rules[item_number - 1]

    print(f"\n--- Gemini Item {item_number} ---")
    print("Description:", rule["rule_description"])
    print("Condition:", rule["condition"])
    print("Action:", rule["action"])
    print("Evidence:", rule["evidence"])

    
# Compare the two rollback-related outputs using simple text checks.
# Text checks are NOT a substitute for human semantic review.
item_11 = gemini_rules[10]
item_14 = gemini_rules[13]

print("\n--- Comparing Rollback Rules ---")

print(
    "Same condition:",
    item_11["condition"] == item_14["condition"]
)

print(
    "Same action:",
    item_11["action"] == item_14["action"]
)

print(
    "Item 11 calls rollback:",
    "ROLLBACK-ACCOUNT" in item_11["action"]
)

print(
    "Item 14 restores balance:",
    "WS-OLD-BALANCE" in item_14["action"]
)



# Initial HUMAN-reviewed decisions for the two studied items.
# FULL: essential reference behavior is correctly covered.
# PARTIAL: related but does not independently cover the full reference rule.
# PRIMARY / COMPLEMENTARY describe their roles; neither means an extra TP.
review = [
    {
        "item": 11,
        "gold_id": "INT-TX01-001",
        "role": "PRIMARY",
        "status": "FULL"
    },
    {
        "item": 14,
        "gold_id": "INT-TX01-001",
        "role": "COMPLEMENTARY",
        "status": "PARTIAL"
    }
]


for result in review:
    print(
        result["item"],
        result["gold_id"],
        result["role"],
        result["status"]
    )


# Store review decisions separately from draft mapping data.
review_file = (
    project_root
    / "evaluation"
    / "tx01_strict_semantic_review.csv"
)



# IMPORTANT: create only when absent, so manual review is not erased.
# Existing CSV decisions take precedence over the initial Python example above.
if not review_file.exists():
    with open(review_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["item", "gold_id", "role", "status"]
        )
        writer.writeheader()
        writer.writerows(review)

    print("\nReview CSV created:", review_file)
else:
    print("\nExisting review CSV preserved:", review_file)


# Reload the actual saved file: this is the source for later steps.
with open(review_file, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    saved_reviews = list(reader)

# Allowed labels for schema validation; PENDING is NOT a scored result.
valid_statuses = {"FULL", "PARTIAL", "NONE", "PENDING"}
valid_roles = {"PRIMARY", "COMPLEMENTARY", "DUPLICATE"}

for record in saved_reviews:
    # assert stops execution if a record contains an invalid value.
    assert record["status"] in valid_statuses
    assert record["role"] in valid_roles
    assert record["gold_id"] in gold_lookup

print("\n--- Review Validation ---")
print("Saved review rows:", len(saved_reviews))
print("All review records valid!")


# defaultdict(list) creates an empty list automatically for a new gold ID.
from collections import defaultdict

# Group multiple Gemini items referring to the same reference rule.
# This helps prevent counting one reference rule more than once for recall.
reviews_by_gold = defaultdict(list)

for record in saved_reviews:
    gold_id = record["gold_id"]
    reviews_by_gold[gold_id].append(record)

print("\n--- Reviews Grouped by Gold Rule ---")

for gold_id, records in reviews_by_gold.items():
    print("Gold ID:", gold_id)
    print("Number of related items:", len(records))

    for record in records:
        print(
            "  Item:", record["item"],
            "| Role:", record["role"],
            "| Status:", record["status"]
        )


# Prepare missing review rows without overwriting existing decisions.
# Find already reviewed Gemini items
# Set comprehension: item numbers already present in the review CSV.
# int() converts CSV text values to integers for reliable comparison.
reviewed_items = {
    int(record["item"])
    for record in saved_reviews
}

new_reviews = []

for row in run_mappings:
    item_number = int(row["item"])

    # continue skips this loop iteration: never recreate an existing review.
    if item_number in reviewed_items:
        continue

    reference_ids = [
        rule_id.strip()
        for rule_id in row["matched_reference_ids"].split(";")
        if rule_id.strip()
    ]

    for reference_id in reference_ids:
        # A draft association is not verified, so new records start PENDING.
        new_reviews.append({
            "item": item_number,
            "gold_id": reference_id,
            "role": "PRIMARY",
            "status": "PENDING"
        })

print("\n--- New Review Records ---")
print("Existing reviews:", len(saved_reviews))
print("New reviews:", len(new_reviews))

# Deliberately do not append new_reviews to the CSV yet.
# Next step: review the proposed rows and then save them safely.
# No TP/FP/FN, precision, recall, or F1 is calculated here.


# ---------------------------------------------------------
# Save new review records without overwriting existing ones
# ---------------------------------------------------------

# Append new records only when there are records to save.
if new_reviews:

    # Open the existing CSV in append mode ("a").
    # Append mode preserves the existing rows.
    with open(review_file, "a", encoding="utf-8", newline="") as f:

        # Create a CSV writer using the existing column names.
        writer = csv.DictWriter(
            f,
            fieldnames=["item", "gold_id", "role", "status"]
        )

        # Do not write the header again.
        # The CSV already contains its column names.

        # Add all new review records to the existing CSV.
        writer.writerows(new_reviews)

    print("\nNew review records saved:", len(new_reviews))

else:
    # This message appears when all items already exist.
    print("\nNo new review records to save.")



# ---------------------------------------------------------
# Review Gemini Item 1 against its Gold Standard rule
# ---------------------------------------------------------

# Select the first Gemini rule.
# Python list indexes start from 0.
gemini_rule = gemini_rules[0]

# Find the corresponding reference rule by its unique ID.
gold_rule = gold_lookup["BR-TX01-001"]

# Display the Gemini extraction.
print("\n--- Gemini Item 1 ---")
print("Description:", gemini_rule["rule_description"])
print("Condition:", gemini_rule["condition"])
print("Action:", gemini_rule["action"])
print("Evidence:", gemini_rule["evidence"])

# Display the reference rule for comparison.
print("\n--- Gold Standard BR-TX01-001 ---")
print("Description:", gold_rule["rule_description"])
print("Condition:", gold_rule["condition"])
print("Action:", gold_rule["action"])


# ---------------------------------------------------------
# Update the semantic review status for Gemini Item 1
# ---------------------------------------------------------

# Read all existing review records from the CSV file.
with open(review_file, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    review_records = list(reader)

# Find the review record for Gemini Item 1.
for record in review_records:

    # CSV values are strings, so compare with "1".
    if record["item"] == "1":

        # Mark the rule as a complete semantic match.
        record["status"] = "FULL"

        # Stop searching after finding the target record.
        break

# Rewrite the CSV with the updated records.
# All other records retain their existing values.
with open(review_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["item", "gold_id", "role", "status"]
    )

    # Write the column names.
    writer.writeheader()

    # Save all records, including the updated Item 1.
    writer.writerows(review_records)

print("\n--- Semantic Review Updated ---")
print("Gemini Item 1: FULL")
