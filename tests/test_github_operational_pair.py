import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "instrument-registry.json"
CONTINUOUS_ID = "github-operational-recoverable"


class GitHubOperationalContinuousTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.entries = {item["id"]: item for item in cls.registry["instruments"]}

    def test_transferred_instrument_is_continuous_and_internal(self):
        item = self.entries[CONTINUOUS_ID]
        self.assertEqual(item["category"], "continuous_automation")
        self.assertEqual(item["activation"]["mode"], "continuous_preconfiguration")
        self.assertIs(item["activation"]["enabled"], True)
        self.assertIs(item["ui"]["visible"], False)
        self.assertTrue((ROOT / item["path"]).is_file())

    def test_catalogs_place_instrument_only_in_continuous_context(self):
        continuous = json.loads((ROOT / "config" / "continuous-automation-catalog.json").read_text(encoding="utf-8"))
        recoverable = json.loads((ROOT / "config" / "recoverable-on-demand-catalog.json").read_text(encoding="utf-8"))
        self.assertIn(CONTINUOUS_ID, {item["id"] for item in continuous["instruments"]})
        self.assertNotIn(CONTINUOUS_ID, {item["id"] for item in recoverable["instruments"]})

    def test_content_declares_continuous_operation(self):
        item = self.entries[CONTINUOUS_ID]
        source = (ROOT / item["path"]).read_text(encoding="utf-8")
        self.assertIn("IDENTIDADE E FUNÇÃO CONTÍNUA", source)
        self.assertIn("carregada como contexto operacional interno em toda demanda", source)
        self.assertNotIn("Acione esta fase somente quando", source)

    def test_public_manifest_marks_continuous_classification(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        item = next(item for item in manifest["instruments"] if item["id"] == CONTINUOUS_ID)
        self.assertEqual(item["category"], "continuous_automation")


if __name__ == "__main__":
    unittest.main()
