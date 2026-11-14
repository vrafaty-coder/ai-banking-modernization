
"""
Candidate Discovery Module

Generate candidate Gold Standard matches using
observable alert-code signals.

This module produces candidate suggestions only.
It does not determine semantic equivalence.
"""

from rule_parser import extract_signals


# ---------------------------------------------------------
# 1. Discover candidate reference rules
# ---------------------------------------------------------

def discover_candidates(model_rule, gold_rules):
    """
    Find candidate Gold Standard rules using shared
    numeric alert-code signals.

    Return all rules sharing at least one candidate code.
    """

    # Extract numeric candidates from the model rule.
    model_signals = extract_signals(model_rule)
    model_codes = set(model_signals["alert_candidates"])

    # Store candidate matches.
    candidates = []

    # Examine every Gold Standard rule.
    for gold_rule in gold_rules:

        # Extract numeric candidates from the reference.
        gold_signals = extract_signals(gold_rule)
        gold_codes = set(gold_signals["alert_candidates"])

        # Calculate the intersection of both code sets.
        shared_codes = model_codes & gold_codes

        # Keep rules sharing at least one code.
        if shared_codes:
            candidates.append({
                "gold_id": gold_rule["id"],
                "shared_codes": sorted(shared_codes)
            })

    return candidates


# ---------------------------------------------------------
# Detect banking operations for candidate discovery
# ---------------------------------------------------------

import re

from rule_parser import normalize_text


def extract_banking_operations(rule):
    """
    Extract selected banking-operation signals.

    These signals support candidate discovery.
    They do not prove semantic equivalence.
    """

    # Combine the extracted rule fields.
    text = normalize_text(
        " ".join([
            str(rule.get("rule_description", "")),
            str(rule.get("condition", "")),
            str(rule.get("action", ""))
        ])
    )

    # Define operation patterns independently of any item ID.
    patterns = {
        "ROLLBACK": r"\bROLLBACK\b",
        "REWRITE": r"\bREWRITE\b",
        "JOURNAL": r"\bJOURNAL\b",
        "BALANCE": r"\bBALANCE\b",
        "OPEN": r"\bOPEN\b",
        "READ": r"\bREAD\b",
        "WRITE": r"\bWRITE\b"
    }

    # Collect all operations mentioned in the rule.
    operations = set()

    for operation, pattern in patterns.items():
        if re.search(pattern, text):
            operations.add(operation)

    return operations


# ---------------------------------------------------------
# Hybrid candidate discovery (experimental)
# ---------------------------------------------------------

def discover_candidates_hybrid(model_rule, gold_rules):
    """
    Generate candidate matches using alert codes
    and banking-operation signals.

    This is an experimental ranking method.
    Scores are heuristic, not semantic probabilities.
    """

    # Extract model alert codes.
    model_codes = set(
        extract_signals(model_rule)["alert_candidates"]
    )

    # Extract model banking-operation signals.
    model_operations = extract_banking_operations(model_rule)

    candidates = []

    for gold_rule in gold_rules:

        # Extract reference signals.
        gold_codes = set(
            extract_signals(gold_rule)["alert_candidates"]
        )
        gold_operations = extract_banking_operations(gold_rule)

        # Calculate shared alert codes and operations.
        shared_codes = model_codes & gold_codes
        shared_operations = model_operations & gold_operations

        # Assign stronger weight to shared alert codes.
        score = (
            5 * len(shared_codes)
            + 2 * len(shared_operations)
        )

        # Keep candidates with a positive score.
        if score > 0:
            candidates.append({
                "gold_id": gold_rule["id"],
                "score": score,
                "shared_codes": sorted(shared_codes),
                "shared_operations": sorted(shared_operations)
            })

    # Rank candidates by descending score.
    candidates.sort(
        key=lambda item: (-item["score"], item["gold_id"])
    )

    return candidates
