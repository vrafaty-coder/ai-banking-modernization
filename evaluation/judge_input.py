
"""
Prepare structured inputs for the LLM semantic judge.

This module does not call an API.
It does not modify the source rules or Gold Standard.
"""

from rule_parser import load_json


def build_judge_input(model_rule, gold_rule, source_context):
    """
    Build a structured judging request.

    Source context must come from verified COBOL files,
    not solely from model-generated evidence.
    """

    return {
        "reference_rule": {
            "id": gold_rule["id"],
            "category": gold_rule["category"],
            "rule_description": gold_rule["rule_description"],
            "condition": gold_rule["condition"],
            "action": gold_rule["action"],
            "evidence": gold_rule.get("evidence", []),
            "dependencies": gold_rule.get("dependencies", [])
        },
        "extracted_rule": {
            "category": model_rule.get("category", ""),
            "rule_description": model_rule.get(
                "rule_description", ""
            ),
            "condition": model_rule.get("condition", ""),
            "action": model_rule.get("action", ""),
            "evidence": model_rule.get("evidence", "")
        },
        "verified_source_context": source_context
    }
