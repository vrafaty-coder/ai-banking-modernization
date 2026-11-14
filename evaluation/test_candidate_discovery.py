
"""
Unit tests for candidate discovery.
"""

import unittest

from candidate_discovery import discover_candidates


class TestCandidateDiscovery(unittest.TestCase):

    # Verify that a shared alert code generates a candidate.
    def test_shared_alert_code(self):

        model_rule = {
            "condition": "STATUS NOT = 00",
            "action": "Move 9001 to RSP-ALERT-CODE"
        }

        gold_rules = [
            {
                "id": "RULE-001",
                "condition": "OPEN error",
                "action": "Alert 9001"
            },
            {
                "id": "RULE-002",
                "condition": "WRITE error",
                "action": "Alert 9002"
            }
        ]

        candidates = discover_candidates(
            model_rule,
            gold_rules
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            candidates[0]["gold_id"],
            "RULE-001"
        )

    # Verify that no shared code produces no candidates.
    def test_no_shared_alert_code(self):

        model_rule = {
            "condition": "Balance updated",
            "action": "Update account balance"
        }

        gold_rules = [
            {
                "id": "RULE-001",
                "condition": "OPEN error",
                "action": "Alert 9001"
            }
        ]

        candidates = discover_candidates(
            model_rule,
            gold_rules
        )

        self.assertEqual(candidates, [])


    # Verify extraction of banking-operation signals.
    def test_extract_banking_operations(self):

        from candidate_discovery import extract_banking_operations

        rule = {
            "rule_description": "Account balance rollback",
            "condition": "Account was previously updated",
            "action": "Restore balance and rewrite ACCOUNT-RECORD"
        }

        operations = extract_banking_operations(rule)

        self.assertIn("ROLLBACK", operations)
        self.assertIn("BALANCE", operations)
        self.assertIn("REWRITE", operations)


    # Verify that shared alert codes receive higher weight.
    def test_hybrid_candidate_ranking(self):

        from candidate_discovery import discover_candidates_hybrid

        model_rule = {
            "rule_description": "Account file error",
            "condition": "OPEN status not 00",
            "action": "Alert 9001 and GOBACK"
        }

        gold_rules = [
            {
                "id": "RULE-A",
                "rule_description": "Account file error",
                "condition": "OPEN status not 00",
                "action": "Alert 9001 and GOBACK"
            },
            {
                "id": "RULE-B",
                "rule_description": "Account open operation",
                "condition": "OPEN account",
                "action": "Continue processing"
            }
        ]

        candidates = discover_candidates_hybrid(
            model_rule,
            gold_rules
        )

        # The exact alert-code match should rank first.
        self.assertEqual(
            candidates[0]["gold_id"],
            "RULE-A"
        )

        # The score must be higher for RULE-A.
        self.assertGreater(
            candidates[0]["score"],
            candidates[1]["score"]
        )


if __name__ == "__main__":
    unittest.main()
