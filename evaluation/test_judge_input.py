
import unittest

from judge_input import build_judge_input


class TestJudgeInput(unittest.TestCase):

    def test_build_judge_input(self):

        model_rule = {
            "category": "BUSINESS",
            "rule_description": "Transaction amount cannot be zero",
            "condition": "RCV-AMOUNT = 0",
            "action": "Alert 1004 and GOBACK",
            "evidence": "if RCV-AMOUNT = 0"
        }

        gold_rule = {
            "id": "BR-TX01-001",
            "category": "BUSINESS",
            "rule_description": "Reject zero deposit amount",
            "condition": "RCV-AMOUNT = 0",
            "action": "Alert 1004; Invalid amount; GOBACK",
            "evidence": [
                {
                    "file": "TX01.cbl",
                    "line": 64,
                    "snippet": "if RCV-AMOUNT = 0"
                }
            ],
            "dependencies": ["TX01-RECEIVE.cpy"]
        }

        source_context = {
            "file": "TX01.cbl",
            "lines": [
                "if RCV-AMOUNT = 0",
                "move 1004 to RSP-ALERT-CODE",
                "goback"
            ]
        }

        result = build_judge_input(
            model_rule,
            gold_rule,
            source_context
        )

        self.assertEqual(
            result["reference_rule"]["id"],
            "BR-TX01-001"
        )

        self.assertEqual(
            result["extracted_rule"]["condition"],
            "RCV-AMOUNT = 0"
        )

        self.assertEqual(
            result["verified_source_context"]["file"],
            "TX01.cbl"
        )


if __name__ == "__main__":
    unittest.main()
