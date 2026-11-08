import unittest

from scripts.promptaria_validate_result import validate


class PromptariaResultValidationTests(unittest.TestCase):
    def valid_result(self):
        return {
            "schema_version": 2,
            "mandatory_components": [{"found": True}, {"found": True}, {"found": True}],
            "missing_mandatory_components": [],
            "matched_instruments": [
                {"content_recovered": True, "activation_status": "recognized_not_executed"},
                {"content_recovered": True, "activation_status": "included_in_plan_not_executed"},
            ],
            "write_execution_available": False,
            "status": "plan_created_needs_execution_integration",
        }

    def test_accepts_complete_traceable_plan(self):
        self.assertEqual(validate(self.valid_result()), [])

    def test_rejects_missing_mandatory_components(self):
        result = self.valid_result()
        result["missing_mandatory_components"] = ["missing"]
        self.assertTrue(validate(result))

    def test_rejects_false_claim_of_execution(self):
        result = self.valid_result()
        result["matched_instruments"][0]["activation_status"] = "executed"
        self.assertTrue(validate(result))

    def test_rejects_claim_that_write_execution_is_available(self):
        result = self.valid_result()
        result["write_execution_available"] = True
        self.assertTrue(validate(result))


if __name__ == "__main__":
    unittest.main()
