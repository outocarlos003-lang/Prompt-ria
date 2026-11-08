import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_operational_audit as audit


class OperationalAuditCatalogIntegrityTests(unittest.TestCase):
    def test_duplicate_ids_are_reported_before_catalog_indexing(self):
        registry = {"instruments": [
            {"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"},
            {"id": "alpha", "title": "Alpha revised", "path": "instruments/alpha-v2.md"},
        ]}
        manifest = {"instruments": [
            {"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"},
        ]}
        execution_map = {"instruments": [
            {"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"},
        ]}

        report = audit.catalog_integrity_report(registry, manifest, execution_map)

        self.assertEqual(report["status"], "conflicts_detected")
        self.assertIn("alpha", report["affected_instrument_ids"])
        self.assertTrue(any(
            finding["type"] == "duplicate_id" and finding["source"] == "registry"
            for finding in report["findings"]
        ))
        self.assertTrue(any(
            finding["type"] == "path_mismatch"
            for finding in report["findings"]
        ))

    def test_missing_catalog_membership_is_reported(self):
        registry = {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"}]}
        manifest = {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"}]}
        execution_map = {"instruments": []}

        report = audit.catalog_integrity_report(registry, manifest, execution_map)

        self.assertTrue(any(
            finding["type"] == "catalog_presence_mismatch"
            and finding["instrument_ids"] == ["alpha"]
            for finding in report["findings"]
        ))

    def test_missing_identity_fields_are_reported_and_mark_id_conflicted(self):
        report = audit.catalog_integrity_report(
            {"instruments": [{"id": "alpha", "path": "instruments/alpha.md"}]},
            {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"}]},
            {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"}]},
        )
        self.assertIn("alpha", report["affected_instrument_ids"])
        self.assertTrue(any(
            finding["type"] == "missing_identity_field" and finding["field"] == "title"
            for finding in report["findings"]
        ))

    def test_non_object_catalog_entry_is_reported(self):
        report = audit.catalog_integrity_report(
            {"instruments": ["malformed"]},
            {"instruments": []},
            {"instruments": []},
        )
        self.assertTrue(any(
            finding["type"] == "invalid_catalog_entry" and finding["source"] == "registry"
            for finding in report["findings"]
        ))

    def test_non_list_catalog_collection_is_reported_for_each_source(self):
        empty = {"instruments": []}
        for source_name in ("registry", "manifest", "execution_map"):
            with self.subTest(source=source_name):
                catalogs = {
                    "registry": empty,
                    "manifest": empty,
                    "execution_map": empty,
                }
                catalogs[source_name] = {"instruments": None}
                report = audit.catalog_integrity_report(
                    catalogs["registry"], catalogs["manifest"], catalogs["execution_map"]
                )
                self.assertTrue(any(
                    finding["type"] == "invalid_catalog_collection"
                    and finding["source"] == source_name
                    for finding in report["findings"]
                ))

    def test_inventory_survives_null_catalog_collection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for directory in ("config", "tests", "scripts", "instruments", ".github/workflows"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "config/instrument-registry.json").write_text(
                json.dumps({"instruments": None}), encoding="utf-8"
            )
            (root / "tests/manifest.json").write_text(
                json.dumps({"instruments": []}), encoding="utf-8"
            )
            (root / "config/instrument-execution-map.json").write_text(
                json.dumps({"instruments": []}), encoding="utf-8"
            )
            report = audit.build_inventory(root)
            self.assertEqual(report["summary"]["instrument_count"], 0)
            self.assertTrue(any(
                finding["type"] == "invalid_catalog_collection"
                and finding["source"] == "registry"
                for finding in report["catalog_integrity"]["findings"]
            ))

    def test_malformed_activation_metadata_is_not_enabled_or_fatal(self):
        for activation in (None, [], "enabled", {"enabled": "true"}, {"enabled": False}):
            with self.subTest(activation=activation):
                self.assertFalse(audit.activation_enabled({"activation": activation}))
        self.assertTrue(audit.activation_enabled({"activation": {"enabled": True}}))

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for directory in ("config", "tests", "scripts", "instruments", ".github/workflows"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "instruments/alpha.md").write_text("# Alpha\n", encoding="utf-8")
            item = {"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md", "activation": None}
            (root / "config/instrument-registry.json").write_text(
                json.dumps({"instruments": [item]}), encoding="utf-8"
            )
            catalog_item = {"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"}
            (root / "tests/manifest.json").write_text(
                json.dumps({"instruments": [catalog_item]}), encoding="utf-8"
            )
            (root / "config/instrument-execution-map.json").write_text(
                json.dumps({"instruments": [catalog_item]}), encoding="utf-8"
            )
            report = audit.build_inventory(root)
            alpha = next(record for record in report["instruments"] if record["instrument_id"] == "alpha")
            self.assertFalse(alpha["activation_enabled"])

    def test_clean_catalogs_return_clean_status(self):
        item = {"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"}
        report = audit.catalog_integrity_report(
            {"instruments": [item]},
            {"instruments": [item]},
            {"instruments": [item]},
        )
        self.assertEqual(report["status"], "clean")
        self.assertEqual(report["finding_count"], 0)
        self.assertEqual(report["affected_instrument_ids"], [])

    def test_conflicted_identity_is_not_classified_as_partially_automated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for directory in ("config", "tests", "scripts", "instruments", ".github/workflows"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "instruments/alpha.md").write_text("# Alpha\n", encoding="utf-8")
            registry = {"instruments": [
                {"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md", "activation": {"enabled": True}},
                {"id": "alpha", "title": "Alpha revised", "path": "instruments/alpha-v2.md", "activation": {"enabled": True}},
            ]}
            manifest = {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"}]}
            execution_map = {"instruments": [{
                "id": "alpha", "title": "Alpha", "path": "instruments/alpha.md",
                "specialized_handler": "run_alpha", "specialized_execution_status": "implemented",
                "functional_execution_verified": False,
            }]}
            (root / "config/instrument-registry.json").write_text(json.dumps(registry), encoding="utf-8")
            (root / "tests/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "config/instrument-execution-map.json").write_text(json.dumps(execution_map), encoding="utf-8")
            (root / "scripts/promptaria_specialized_executor.py").write_text(
                "def run_alpha(payload): return payload\nHANDLERS = {'alpha': run_alpha}\n",
                encoding="utf-8",
            )
            (root / ".github/workflows/test.yml").write_text(
                "python scripts/promptaria_specialized_executor.py\n", encoding="utf-8"
            )
            (root / "tests/test_alpha.py").write_text("alpha regression\n", encoding="utf-8")

            report = audit.build_inventory(root)
            alpha = next(item for item in report["instruments"] if item["path"] == "instruments/alpha.md")
            self.assertEqual(alpha["category"], "no_executor")
            self.assertFalse(alpha["evidence"]["title_consistent"])

    def test_handler_mapping_must_match_declared_function_name(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for directory in ("config", "tests", "scripts", "instruments", ".github/workflows"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "instruments/alpha.md").write_text("# Alpha\n", encoding="utf-8")
            item = {"id": "alpha", "title": "Alpha", "path": "instruments/alpha.md"}
            registry_item = {**item, "activation": {"enabled": True}}
            mapped_item = {
                **item,
                "specialized_handler": "run_wrong",
                "specialized_execution_status": "implemented",
                "functional_execution_verified": False,
            }
            (root / "config/instrument-registry.json").write_text(
                json.dumps({"instruments": [registry_item]}), encoding="utf-8"
            )
            (root / "tests/manifest.json").write_text(
                json.dumps({"instruments": [item]}), encoding="utf-8"
            )
            (root / "config/instrument-execution-map.json").write_text(
                json.dumps({"instruments": [mapped_item]}), encoding="utf-8"
            )
            (root / "scripts/promptaria_specialized_executor.py").write_text(
                "def run_alpha(payload): return payload\nHANDLERS = {'alpha': run_alpha}\n",
                encoding="utf-8",
            )
            (root / ".github/workflows/test.yml").write_text(
                "python scripts/promptaria_specialized_executor.py\n", encoding="utf-8"
            )
            (root / "tests/test_alpha.py").write_text("alpha regression\n", encoding="utf-8")

            report = audit.build_inventory(root)
            alpha = next(record for record in report["instruments"] if record["instrument_id"] == "alpha")
            self.assertFalse(alpha["handler_present"])
            self.assertFalse(alpha["evidence"]["handler_function"])
            self.assertEqual(alpha["category"], "no_executor")
            self.assertIn("no matching specialized handler is proven by the handler map", alpha["gaps"])

    def test_handler_map_rejects_multiple_top_level_assignments(self):
        source = """def run_alpha(): pass
def run_wrong(): pass
HANDLERS = {"alpha": run_alpha}
HANDLERS = {"alpha": run_wrong}
"""
        self.assertEqual(audit.handler_map(source), {})

    def test_handler_map_rejects_tuple_target_assignment(self):
        source = """def run_alpha(): pass
HANDLERS = {"alpha": run_alpha}
HANDLERS, unused = ({"alpha": run_alpha}, None)
"""
        self.assertEqual(audit.handler_map(source), {})

    def test_handler_map_rejects_conditional_reassignment(self):
        source = """def run_alpha(): pass
def run_wrong(): pass
HANDLERS = {"alpha": run_alpha}
if condition:
    HANDLERS = {"alpha": run_wrong}
"""
        self.assertEqual(audit.handler_map(source), {})

    def test_handler_map_rejects_duplicate_literal_ids_as_ambiguous(self):
        source = "def run_first(): pass\ndef run_second(): pass\nHANDLERS = {'alpha': run_first, 'alpha': run_second}\n"
        self.assertNotIn("alpha", audit.handler_map(source))

    def test_handler_map_treats_invalid_python_as_missing_evidence(self):
        self.assertEqual(audit.handler_map("HANDLERS = {\n"), {})

    def test_repository_execution_map_matches_static_handler_functions(self):
        execution_map = audit.read_json(audit.EXECUTION_MAP)
        source = audit.SPECIALIZED.read_text(encoding="utf-8")
        handlers = audit.handler_map(source)

        for item in execution_map.get("instruments", []):
            with self.subTest(instrument_id=item.get("id")):
                self.assertEqual(
                    handlers.get(item.get("id")),
                    item.get("specialized_handler"),
                    "execution map must name the function actually mapped for this instrument",
                )

    def test_full_report_includes_json_serializable_integrity_section(self):
        report = audit.build_inventory()
        integrity = json.loads(json.dumps(report["catalog_integrity"]))
        self.assertIn(integrity["status"], {"clean", "conflicts_detected"})
        self.assertEqual(integrity["finding_count"], len(integrity["findings"]))


if __name__ == "__main__":
    unittest.main()
