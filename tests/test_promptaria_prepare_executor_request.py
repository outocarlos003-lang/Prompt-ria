import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.promptaria_prepare_executor_request import atomic_json, prepare


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

    def test_atomic_json_writes_complete_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "executor-request.json"
            atomic_json(output, {"ok": True, "value": "á"})
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"ok": True, "value": "á"})

    def test_atomic_json_replace_failure_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "executor-request.json"
            output.write_text("original\\n", encoding="utf-8")
            with patch("scripts.promptaria_prepare_executor_request.os.replace", side_effect=OSError("simulated failure")):
                with self.assertRaises(OSError):
                    atomic_json(output, {"new": True})
            self.assertEqual(output.read_text(encoding="utf-8"), "original\\n")
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])

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
