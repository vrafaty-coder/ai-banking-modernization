
"""
Unit tests for rule_parser.py

Run with:
    python -m unittest discover -s evaluation -p "test_*.py"
"""

import unittest

from rule_parser import (
    normalize_text,
    normalize_condition,
    extract_signals,
    extract_file_operations,
)


class TestRuleParser(unittest.TestCase):

    # Verify that case and extra spaces are normalized.
    def test_normalize_text(self):
        result = normalize_text("  open   account-file  ")
        self.assertEqual(result, "OPEN ACCOUNT-FILE")

    # Verify normalization of equivalent inequality syntax.
    def test_normalize_condition(self):
        first = normalize_condition('STATUS NOT = "00"')
        second = normalize_condition('STATUS != "00"')
        self.assertEqual(first, second)

    # Verify detection of an alert code and GOBACK.
    def test_extract_signals(self):
        rule = {
            "condition": "RCV-AMOUNT = 0",
            "action": "Move 1004 to RSP-ALERT-CODE and GOBACK"
        }

        result = extract_signals(rule)

        self.assertIn("1004", result["alert_candidates"])
        self.assertTrue(result["has_goback"])
        self.assertFalse(result["has_rollback"])

    # Verify detection of an ACCOUNT-FILE OPEN operation.
    def test_extract_file_operations(self):
        evidence = """
        open i-o ACCOUNT-FILE
        if WS-ACC-STATUS not = "00"
            goback
        end-if
        """

        result = extract_file_operations(evidence)

        self.assertEqual(
            result["opened_files"],
            ["ACCOUNT-FILE"]
        )


if __name__ == "__main__":
    unittest.main()
