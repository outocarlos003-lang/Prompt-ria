import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "manifest.json"
EXECUTION_MAP = ROOT / "config" / "instrument-execution-map.json"


class PromptariaExecutionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.execution_map = json.loads(EXECUTION_MAP.read_text(encoding="utf-8"))

    def test_map_covers_exactly_the_canonical_manifest(self):
        canonical = {item["id"]: item for item in self.manifest["instruments"]}
        mapped_items = self.execution_map["instruments"]
        mapped = {item["id"]: item for item in mapped_items}
        self.assertEqual(len(mapped), len(mapped_items), "IDs duplicados no mapa")
        self.assertEqual(set(mapped), set(canonical), "Mapa deve cobrir exatamente o manifesto")
        for instrument_id, item in mapped.items():
            with self.subTest(instrument=instrument_id):
                self.assertEqual(item["title"], canonical[instrument_id]["title"])
                self.assertEqual(item["path"], canonical[instrument_id]["path"])

    def test_every_instrument_maps_to_a_dedicated_specialized_handler(self):
        handlers = {
            "github-operational": "handler_github_operational",
            "coordinator": "handler_coordinator",
            "master-activation": "handler_master_activation",
            "master-execution": "handler_master_execution",
            "functional-correference-architecture": "handler_functional_correference",
            "future-demand-preconfiguration": "handler_future_preconfiguration",
            "catalog-sitemap-preconfiguration": "handler_catalog_sitemap",
            "promptaria-instrument-template": "handler_promptaria_instrument_template",
            "protocol-update-integrity": "handler_protocol_update_integrity",
            "nocturna-arquitetura-necessidade-identidade-sistemica": "handler_nocturna_architecture",
        }
        specialized = ROOT / "scripts" / "promptaria_specialized_executor.py"
        self.assertTrue(specialized.is_file())
        self.assertEqual(set(handlers), {item["id"] for item in self.execution_map["instruments"]})
        for item in self.execution_map["instruments"]:
            with self.subTest(instrument=item["id"]):
                self.assertEqual(item["specialized_executor"], "scripts/promptaria_specialized_executor.py")
                self.assertEqual(item["specialized_execution_status"], "implemented")
                self.assertEqual(item["specialized_handler"], handlers[item["id"]])
                self.assertIs(item["side_effects_authorized_by_title"], False)

    def test_shared_executors_exist_and_generic_writer_is_narrowly_scoped(self):
        resolver = ROOT / self.execution_map["resolution_executor"]
        writer = ROOT / self.execution_map["generic_write_executor"]["path"]
        self.assertTrue(resolver.is_file())
        self.assertTrue(writer.is_file())
        writer_map = self.execution_map["generic_write_executor"]
        self.assertEqual(writer_map["operation"], "write_text")
        self.assertEqual(writer_map["allowed_destination_prefixes"], ["artifacts/"])
        self.assertIn("write_authorized=true", writer_map["requires"])
        self.assertIn("dry_run=false", writer_map["requires"])
        self.assertIn("--confirm-operation igual a operation_id", writer_map["requires"])

    def test_fixed_prompt_role_is_unified_under_canonical_github_identity(self):
        mapped = {item["id"]: item for item in self.execution_map["instruments"]}
        item = mapped["github-operational"]
        self.assertEqual(item["resolution_status"], "resolved_by_canonical_identity")
        self.assertIn("build_structured_demand_envelope", item["planning_capabilities"])
        self.assertFalse(item["side_effects_authorized_by_title"])
        self.assertNotIn("fixed-prompt-instrument-part-2", mapped)


if __name__ == "__main__":
    unittest.main()
