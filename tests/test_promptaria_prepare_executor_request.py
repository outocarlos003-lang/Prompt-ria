import json
import unittest

from scripts.promptaria_prepare_executor_request import prepare


class PrepareExecutorRequestTests(unittest.TestCase):
    def valid(self, **overrides):
        payload = {
            "operation_id": "workflow-op-01",
            "operation": "write_text",
            "destination": "artifacts/report.txt",
            "content": "conteúdo de teste",
            "dry_run": False,
            "write_authorized": True,
        }
        payload.update(overrides)
        return json.dumps(payload)

    def test_empty_input_disables_executor(self):
        self.assertIsNone(prepare("  "))

    def test_forces_simulation_and_removes_authorization(self):
        result = prepare(self.valid())
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["write_authorized"])
        self.assertEqual(result["operation_id"], "workflow-op-01")

    def test_rejects_invalid_json(self):
        with self.assertRaises(ValueError):
            prepare("{invalid")

    def test_rejects_non_object_json(self):
        with self.assertRaises(ValueError):
            prepare('["not", "an", "object"]')

    def test_requires_structured_fields(self):
        with self.assertRaises(ValueError):
            prepare(json.dumps({"operation_id": "workflow-op-01"}))


if __name__ == "__main__":
    unittest.main()
