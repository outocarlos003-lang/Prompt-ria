import json
import tempfile
import unittest
from pathlib import Path

from scripts.activate_instrument import validate_executor_evidence


class ActivationExecutorEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        (self.root / "scripts").mkdir()
        self.item = {
            "id": "example-instrument",
            "title": "Example Instrument",
            "path": "instruments/example.md",
        }
        (self.root / "scripts" / "specialized.py").write_text(
            "def handler_example(context):\n    return {'result': 'ok'}\n",
            encoding="utf-8",
        )
        (self.root / "config" / "instrument-execution-map.json").write_text(
            json.dumps({
                "instruments": [{
                    **self.item,
                    "specialized_executor": "scripts/specialized.py",
                    "specialized_handler": "handler_example",
                    "specialized_execution_status": "implemented",
                    "side_effects_authorized_by_title": False,
                }]
            }),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_matching_implemented_handler(self):
        self.assertEqual(validate_executor_evidence(self.item, self.root), [])

    def test_rejects_missing_execution_map_entry(self):
        path = self.root / "config" / "instrument-execution-map.json"
        path.write_text(json.dumps({"instruments": []}), encoding="utf-8")
        self.assertTrue(any("exatamente uma vez" in error for error in validate_executor_evidence(self.item, self.root)))

    def test_rejects_identity_mismatch(self):
        path = self.root / "config" / "instrument-execution-map.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["instruments"][0]["path"] = "instruments/other.md"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("identidade do mapa" in error for error in validate_executor_evidence(self.item, self.root)))

    def test_rejects_unimplemented_handler(self):
        path = self.root / "config" / "instrument-execution-map.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["instruments"][0]["specialized_execution_status"] = "planned"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("não está marcado como implemented" in error for error in validate_executor_evidence(self.item, self.root)))

    def test_rejects_handler_name_not_present_in_executor(self):
        path = self.root / "config" / "instrument-execution-map.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["instruments"][0]["specialized_handler"] = "handler_missing"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("não existe no código" in error for error in validate_executor_evidence(self.item, self.root)))

    def test_rejects_title_based_side_effect_authorization(self):
        path = self.root / "config" / "instrument-execution-map.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["instruments"][0]["side_effects_authorized_by_title"] = True
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("side_effects_authorized_by_title=false" in error for error in validate_executor_evidence(self.item, self.root)))


if __name__ == "__main__":
    unittest.main()
