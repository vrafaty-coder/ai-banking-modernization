
"""
Semantic Matcher Module

Provides structural diagnostics for candidate
Gemini-to-Gold-Standard rule comparisons.

Diagnostic results are not final semantic verdicts.
"""

from rule_parser import extract_signals


# ---------------------------------------------------------
# 1. Compare two candidate rules
# ---------------------------------------------------------

def compare_rules(gemini_rule, gold_rule):
    """
    Compare selected structural signals.

    Return a dictionary containing:
        - Condition comparison
        - Alert-code coverage
        - GOBACK comparison
        - Diagnostic findings

    This function does not assign FULL/PARTIAL/NONE.
    """

    # Extract normalized structural information.
    gemini = extract_signals(gemini_rule)
    gold = extract_signals(gold_rule)

    # Compare normalized condition strings.
    # Different strings may still be semantically equivalent.
    condition_equal = (
        gemini["condition"] == gold["condition"]
    )

    # Convert numeric candidates into sets.
    gemini_codes = set(gemini["alert_candidates"])
    gold_codes = set(gold["alert_candidates"])

    # Find reference codes absent from Gemini's action.
    missing_codes = gold_codes - gemini_codes

    # Compare explicit GOBACK signals.
    goback_equal = (
        gemini["has_goback"] == gold["has_goback"]
    )

    # Collect diagnostic findings.
    findings = []

    if not condition_equal:
        findings.append("CONDITION_TEXT_DIFFERS")

    if missing_codes:
        findings.append("REFERENCE_CODE_NOT_FOUND")

    if not goback_equal:
        findings.append("GOBACK_TEXT_DIFFERS")

    # Return structured diagnostic information.
    return {
        "condition_equal": condition_equal,
        "required_codes": sorted(gold_codes),
        "model_codes": sorted(gemini_codes),
        "missing_codes": sorted(missing_codes),
        "goback_equal": goback_equal,
        "findings": findings
    }
