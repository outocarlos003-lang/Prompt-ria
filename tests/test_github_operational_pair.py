import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "instrument-registry.json"
CONTINUOUS_ID = "github-operational-recoverable"
REFERENCE_ID = "github-operational"
TRANSFERRED_ID = "github-operational-demand-mirror"
COUNTERPART_ID = "github-operational-demand"


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


    def test_transferred_instrument_and_new_counterpart_are_exclusively_partitioned(self):
        transferred = self.entries[TRANSFERRED_ID]
        counterpart = self.entries[COUNTERPART_ID]
        continuous = json.loads((ROOT / "config" / "continuous-automation-catalog.json").read_text(encoding="utf-8"))
        recoverable = json.loads((ROOT / "config" / "recoverable-on-demand-catalog.json").read_text(encoding="utf-8"))
        continuous_ids = {item["id"] for item in continuous["instruments"]}
        recoverable_ids = {item["id"] for item in recoverable["instruments"]}

        self.assertEqual(transferred["category"], "continuous_automation")
        self.assertEqual(transferred["activation"]["mode"], "continuous_preconfiguration")
        self.assertIs(transferred["ui"]["visible"], False)
        self.assertIn(TRANSFERRED_ID, continuous_ids)
        self.assertNotIn(TRANSFERRED_ID, recoverable_ids)

        self.assertEqual(counterpart["category"], "recoverable_on_demand")
        self.assertEqual(counterpart["activation"]["mode"], "on_demand_title")
        self.assertIs(counterpart["ui"]["visible"], True)
        self.assertIn(COUNTERPART_ID, recoverable_ids)
        self.assertNotIn(COUNTERPART_ID, continuous_ids)

        self.assertNotEqual(transferred["id"], counterpart["id"])
        self.assertNotEqual(transferred["path"], counterpart["path"])
        self.assertIn(f"{TRANSFERRED_ID}->{COUNTERPART_ID}", transferred["relations"])
        self.assertIn(f"{COUNTERPART_ID}->{TRANSFERRED_ID}", counterpart["relations"])
        self.assertTrue((ROOT / transferred["path"]).is_file())
        self.assertTrue((ROOT / counterpart["path"]).is_file())
        self.assertNotEqual(
            (ROOT / transferred["path"]).read_text(encoding="utf-8"),
            (ROOT / counterpart["path"]).read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
