import json
import unittest
from pathlib import Path

from scripts import promptaria_interconnection
from scripts import promptaria_specialized_executor

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "instrument-registry.json"
MAP_PATH = ROOT / "config" / "instrument-execution-map.json"
MANIFEST_PATH = ROOT / "tests" / "manifest.json"
CONTINUOUS_ID = "github-operational"
RECOVERABLE_ID = "github-operational-recoverable"


class GitHubOperationalPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.execution_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.entries = {item["id"]: item for item in cls.registry["instruments"]}
        cls.mapped = {item["id"]: item for item in cls.execution_map["instruments"]}

    def test_category_catalogs_keep_the_two_github_phases_separate(self):
        continuous = json.loads((ROOT / "config" / "continuous-automation-catalog.json").read_text(encoding="utf-8"))
        recoverable = json.loads((ROOT / "config" / "recoverable-on-demand-catalog.json").read_text(encoding="utf-8"))
        continuous_ids = {item["id"] for item in continuous["instruments"]}
        recoverable_ids = {item["id"] for item in recoverable["instruments"]}
        self.assertIn(CONTINUOUS_ID, continuous_ids)
        self.assertNotIn(CONTINUOUS_ID, recoverable_ids)
        self.assertIn(RECOVERABLE_ID, recoverable_ids)
        self.assertNotIn(RECOVERABLE_ID, continuous_ids)
        self.assertEqual(continuous["catalog_type"], "continuous_automation")
        self.assertEqual(recoverable["catalog_type"], "recoverable_on_demand")
        self.assertEqual(self.entries[CONTINUOUS_ID]["category"], "continuous_automation")
        self.assertEqual(self.entries[RECOVERABLE_ID]["category"], "recoverable_on_demand")

    def test_continuous_mirror_remains_internal(self):
        item = self.entries[CONTINUOUS_ID]
        self.assertEqual(item["path"], "instruments/acione-a-promptaria-pelo-github.md")
        self.assertEqual(item["category"], "continuous_automation")
        self.assertEqual(item["activation"]["mode"], "continuous_preconfiguration")
        self.assertIs(item["activation"]["enabled"], True)
        self.assertIs(item["ui"]["visible"], False)
        self.assertEqual(item["ui"]["node_id"], "instrument:github-operational")

    def test_recoverable_counterpart_has_independent_public_identity(self):
        continuous = self.entries[CONTINUOUS_ID]
        recoverable = self.entries[RECOVERABLE_ID]
        self.assertNotEqual(continuous["id"], recoverable["id"])
        self.assertNotEqual(continuous["path"], recoverable["path"])
        self.assertNotEqual(continuous["ui"]["node_id"], recoverable["ui"]["node_id"])
        self.assertEqual(recoverable["category"], "recoverable_on_demand")
        self.assertEqual(recoverable["activation"]["mode"], "on_demand_title")
        self.assertIs(recoverable["activation"]["enabled"], True)
        self.assertIs(recoverable["ui"]["visible"], True)
        self.assertTrue((ROOT / recoverable["path"]).is_file())

    def test_registry_references_are_reciprocal(self):
        continuous = self.entries[CONTINUOUS_ID]
        recoverable = self.entries[RECOVERABLE_ID]
        self.assertIn(f"{CONTINUOUS_ID}->{RECOVERABLE_ID}", continuous["relations"])
        self.assertIn(f"{RECOVERABLE_ID}->{CONTINUOUS_ID}", continuous["relations"])
        self.assertIn(f"{CONTINUOUS_ID}->{RECOVERABLE_ID}", recoverable["relations"])
        self.assertIn(f"{RECOVERABLE_ID}->{CONTINUOUS_ID}", recoverable["relations"])

    def test_manifest_and_execution_map_register_recoverable_phase(self):
        self.assertIn(RECOVERABLE_ID, {item["id"] for item in self.manifest["instruments"]})
        item = self.mapped[RECOVERABLE_ID]
        self.assertEqual(item["path"], self.entries[RECOVERABLE_ID]["path"])
        self.assertEqual(item["specialized_handler"], "handler_github_operational_recoverable")
        self.assertEqual(item["specialized_execution_status"], "implemented")
        self.assertIs(item["side_effects_authorized_by_title"], False)

    def test_recoverable_handler_requires_explicit_selection(self):
        catalog, _ = promptaria_specialized_executor.load_catalog()
        continuous_title = self.entries[CONTINUOUS_ID]["title"]
        recoverable_title = self.entries[RECOVERABLE_ID]["title"]
        self.assertEqual(promptaria_specialized_executor.resolve_ids(continuous_title, catalog), [])
        result = promptaria_specialized_executor.execute({"request": recoverable_title, "instrument_ids": [RECOVERABLE_ID]})
        self.assertEqual(result["selected_instrument_ids"], [RECOVERABLE_ID])
        handler_result = result["results"][0]["result"]
        self.assertEqual(handler_result["result"], "recoverable_phase_prepared")
        self.assertFalse(handler_result["execution_boundary"]["external_side_effects"])
        self.assertTrue(handler_result["phase_contract"]["instrument_ids_distinct"])
        self.assertFalse(handler_result["phase_contract"]["continuous_context_triggers_recoverable_execution"])

    def test_interconnection_correlates_pair_without_merger(self):
        plan = promptaria_interconnection.build(self.registry, selected_on_demand_ids=[RECOVERABLE_ID], request_id="req-pair-test")
        pair = next(link for link in plan["interconnections"] if
            link["continuous_instrument"]["id"] == CONTINUOUS_ID and
            link["recoverable_instrument"]["id"] == RECOVERABLE_ID)
        self.assertTrue(pair["correlation_id"].startswith("corr-"))
        self.assertEqual(pair["request_id"], "req-pair-test")
        self.assertTrue(pair["preservation"]["identities_and_ids_independent"])
        self.assertTrue(pair["preservation"]["functions_and_operations_independent"])
        self.assertFalse(pair["identity_merge"])
        self.assertEqual(pair["interconnection_status"], "interconnected_for_request")


if __name__ == "__main__":
    unittest.main()
