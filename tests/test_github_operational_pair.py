import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "instrument-registry.json"
CONTINUOUS_ID = "github-operational-recoverable"
REFERENCE_ID = "github-operational"
MIRROR_ID = "github-operational-demand-mirror"


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


    def test_new_demand_mirror_is_independent_and_exclusively_recoverable(self):
        mirror = self.entries[MIRROR_ID]
        reference = self.entries[REFERENCE_ID]
        continuous = json.loads((ROOT / "config" / "continuous-automation-catalog.json").read_text(encoding="utf-8"))
        recoverable = json.loads((ROOT / "config" / "recoverable-on-demand-catalog.json").read_text(encoding="utf-8"))
        continuous_ids = {item["id"] for item in continuous["instruments"]}
        recoverable_ids = {item["id"] for item in recoverable["instruments"]}
        self.assertEqual(reference["category"], "continuous_automation")
        self.assertEqual(mirror["category"], "recoverable_on_demand")
        self.assertNotEqual(reference["id"], mirror["id"])
        self.assertNotEqual(reference["path"], mirror["path"])
        self.assertIn(REFERENCE_ID, continuous_ids)
        self.assertNotIn(MIRROR_ID, continuous_ids)
        self.assertIn(MIRROR_ID, recoverable_ids)
        self.assertNotIn(REFERENCE_ID, recoverable_ids)
        self.assertIs(mirror["ui"]["visible"], True)
        self.assertEqual(mirror["activation"]["mode"], "on_demand_title")
        self.assertIn(f"{REFERENCE_ID}->{MIRROR_ID}", reference["relations"])
        self.assertIn(f"{MIRROR_ID}->{REFERENCE_ID}", mirror["relations"])
        self.assertTrue((ROOT / mirror["path"]).is_file())
        self.assertNotEqual(
            (ROOT / reference["path"]).read_text(encoding="utf-8"),
            (ROOT / mirror["path"]).read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
