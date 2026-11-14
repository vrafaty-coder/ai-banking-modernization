
"""
Unit tests for semantic_matcher.py
"""

import unittest

from semantic_matcher import compare_rules


class TestSemanticMatcher(unittest.TestCase):

    # Verify that identical structural signals match.
    def test_identical_rules(self):

        gold = {
            "condition": "RCV-AMOUNT = 0",
            "action": "Alert 1004; GOBACK"
        }

        gemini = {
            "condition": "RCV-AMOUNT = 0",
            "action": "Move 1004 to RSP-ALERT-CODE; GOBACK"
        }

        result = compare_rules(gemini, gold)

        self.assertTrue(result["condition_equal"])
        self.assertEqual(result["missing_codes"], [])
        self.assertTrue(result["goback_equal"])

    # Verify that a missing reference code is detected.
    def test_missing_alert_code(self):

        gold = {
            "condition": "STATUS NOT = 00",
            "action": "Alert 9001; GOBACK"
        }

        gemini = {
            "condition": "STATUS NOT = 00",
            "action": "GOBACK"
        }

        result = compare_rules(gemini, gold)

        self.assertEqual(result["missing_codes"], ["9001"])
        self.assertIn(
            "REFERENCE_CODE_NOT_FOUND",
            result["findings"]
        )

    # Verify that different condition text is reported.
    def test_condition_text_difference(self):

        gold = {
            "condition": "OPEN ACCOUNT-FILE status not 00",
            "action": "Alert 9001; GOBACK"
        }

        gemini = {
            "condition": "WS-ACC-STATUS not = 00",
            "action": "Move 9001 to RSP-ALERT-CODE; GOBACK"
        }

        result = compare_rules(gemini, gold)

        self.assertFalse(result["condition_equal"])
        self.assertIn(
            "CONDITION_TEXT_DIFFERS",
            result["findings"]
        )


if __name__ == "__main__":
    unittest.main()
