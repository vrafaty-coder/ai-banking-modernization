
"""
Rule Parser Module

This module provides reusable functions for:
1. Loading JSON rule files.
2. Normalizing rule text.
3. Extracting structural signals.
4. Detecting COBOL file-opening operations.

It does not perform semantic-equivalence decisions.
"""

import json
import re
from pathlib import Path


# ---------------------------------------------------------
# 1. Load JSON data
# ---------------------------------------------------------

def load_json(file_path):
    """
    Load a JSON file and return its Python data structure.
    """

    # Convert the input path to a Path object.
    file_path = Path(file_path)

    # Open the file and parse its JSON content.
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------
# 2. Normalize text
# ---------------------------------------------------------

def normalize_text(text):
    """
    Normalize case and whitespace without changing meaning.
    """

    # Convert text to uppercase.
    text = str(text).upper()

    # Replace consecutive whitespace with a single space.
    text = re.sub(r"\s+", " ", text)

    # Remove surrounding whitespace.
    return text.strip()


# ---------------------------------------------------------
# 3. Normalize simple inequality expressions
# ---------------------------------------------------------

def normalize_condition(condition):
    """
    Normalize selected inequality operators.

    This is syntactic normalization only.
    It does not prove logical equivalence.
    """

    # Apply basic text normalization.
    condition = normalize_text(condition)

    # Convert NOT = into !=.
    condition = re.sub(r"\bNOT\s*=", "!=", condition)

    return condition


# ---------------------------------------------------------
# 4. Extract structural signals
# ---------------------------------------------------------

def extract_signals(rule):
    """
    Extract observable signals from a rule's condition
    and action fields.
    """

    # Normalize the rule's condition and action.
    condition = normalize_condition(
        rule.get("condition", "")
    )
    action = normalize_text(
        rule.get("action", "")
    )

    # Extract four-digit numeric candidates.
    # These are not necessarily all alert codes.
    alert_candidates = re.findall(
        r"\b\d{4}\b",
        action
    )

    # Detect selected control-flow terms.
    has_goback = bool(
        re.search(r"\bGOBACK\b", action)
    )
    has_rollback = bool(
        re.search(r"\bROLLBACK\b", action)
    )

    return {
        "condition": condition,
        "action": action,
        "alert_candidates": alert_candidates,
        "has_goback": has_goback,
        "has_rollback": has_rollback
    }


# ---------------------------------------------------------
# 5. Extract COBOL OPEN operations
# ---------------------------------------------------------

def extract_file_operations(evidence):
    """
    Detect simple COBOL OPEN statements in evidence.

    This function currently supports single-file
    OPEN statements with standard opening modes.
    """

    # Normalize the evidence snippet.
    text = normalize_text(evidence)

    # Match OPEN mode followed by a file name.
    pattern = (
        r"\bOPEN\s+"
        r"(?:INPUT|OUTPUT|I-O|EXTEND)\s+"
        r"([A-Z][A-Z0-9-]*)"
    )

    opened_files = re.findall(pattern, text)

    return {
        "opened_files": opened_files
    }
