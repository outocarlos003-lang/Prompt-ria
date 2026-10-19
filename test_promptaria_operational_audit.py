import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_operational_audit as audit


class OperationalAuditTests(unittest.TestCase):
    def test_inventory_classifies_every_physical_instrument_once(self):
        report = audit.build_inventory()
        physical = {p.relative_to(ROOT).as_posix() for p in (ROOT / "instruments").glob("*.md")}
        reported = {item["path"] for item in report["instruments"]}
        self.assertTrue(physical.issubset(reported))
        self.assertEqual(report["summary"]["instrument_count"], len(report["instruments"]))
        self.assertEqual(
            sum(report["summary"]["category_counts"].values()),
            report["summary"]["instrument_count"],
        )
        for item in report["instruments"]:
            self.assertIn(item["category"], audit.CATEGORIES)
            self.assertIn("gaps", item)
            self.assertIn("evidence", item)

    def test_audit_does_not_claim_full_automation_without_explicit_evidence(self):
        report = audit.build_inventory()
        for item in report["instruments"]:
            if item["category"] == "already_automated":
                self.assertTrue(item["functional_execution_verified"])
                self.assertTrue(item["handler_present"])
                self.assertTrue(item["evidence"]["test_reference"])
                self.assertTrue(item["evidence"]["workflow_executor_reference"])

    def test_audit_schema_is_json_serializable(self):
        report = audit.build_inventory()
        self.assertEqual(json.loads(json.dumps(report))["schema_version"], 1)

    def test_catalog_integrity_detects_duplicate_ids_before_indexing(self):
        registry = {"instruments": [
            {"id": "alpha", "title": "Alpha", "path": "instruments/a.md"},
            {"id": "alpha", "title": "Alpha revised", "path": "instruments/a2.md"},
        ]}
        manifest = {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/a.md"}]}
        execution_map = {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/a.md"}]}

        report = audit.catalog_integrity_report(registry, manifest, execution_map)

        self.assertEqual(report["status"], "conflicts_detected")
        self.assertIn("alpha", report["affected_instrument_ids"])
        self.assertTrue(any(
            finding["type"] == "duplicate_id" and finding["source"] == "registry"
            for finding in report["findings"]
        ))
        self.assertTrue(any(
            finding["type"] == "title_mismatch" and finding["source"] == "cross_catalog"
            for finding in report["findings"]
        ))

    def test_catalog_integrity_detects_distinct_ids_sharing_a_path(self):
        entries = [
            {"id": "alpha", "title": "Alpha", "path": "instruments/shared.md"},
            {"id": "beta", "title": "Beta", "path": "instruments/shared.md"},
        ]
        report = audit.catalog_integrity_report(
            {"instruments": entries},
            {"instruments": entries},
            {"instruments": entries},
        )

        self.assertEqual(report["status"], "conflicts_detected")
        self.assertTrue(any(
            finding["type"] == "duplicate_path"
            and finding["source"] == "registry"
            and finding["path"] == "instruments/shared.md"
            for finding in report["findings"]
        ))
        self.assertEqual(report["affected_instrument_ids"], ["alpha", "beta"])

    def test_catalog_integrity_detects_missing_catalog_entries_and_path_mismatch(self):
        registry = {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/a.md"}]}
        manifest = {"instruments": [{"id": "alpha", "title": "Alpha", "path": "instruments/old-a.md"}]}
        execution_map = {"instruments": []}

        report = audit.catalog_integrity_report(registry, manifest, execution_map)

        finding_types = {finding["type"] for finding in report["findings"]}
        self.assertIn("catalog_presence_mismatch", finding_types)
        self.assertIn("path_mismatch", finding_types)
        self.assertEqual(report["status"], "conflicts_detected")
        self.assertEqual(report["affected_instrument_ids"], ["alpha"])

    def test_empty_catalogs_are_reported_as_clean(self):
        report = audit.catalog_integrity_report(
            {"instruments": []},
            {"instruments": []},
            {"instruments": []},
        )
        self.assertEqual(report, {
            "status": "clean",
            "finding_count": 0,
            "findings": [],
            "affected_instrument_ids": [],
        })

    def test_inventory_never_marks_conflicted_identity_as_fully_automated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for directory in ("config", "tests", "scripts", ".github/workflows", "instruments"):
                (root / directory).mkdir(parents=True, exist_ok=True)

            registry = {"instruments": [
                {"id": "alpha", "title": "Alpha", "path": "instruments/a.md",
                 "activation": {"enabled": True}},
                {"id": "alpha", "title": "Alpha", "path": "instruments/a2.md",
                 "activation": {"enabled": True}},
            ]}
            manifest = {"instruments": [
                {"id": "alpha", "title": "Alpha", "path": "instruments/a.md"}
            ]}
            execution_map = {"instruments": [
                {"id": "alpha", "title": "Alpha", "path": "instruments/a.md",
                 "specialized_handler": "handler_alpha",
                 "specialized_execution_status": "implemented",
                 "functional_execution_verified": True,
                 "side_effects_authorized_by_title": False}
            ]}
            for path, value in (
                ("config/instrument-registry.json", registry),
                ("tests/manifest.json", manifest),
                ("config/instrument-execution-map.json", execution_map),
            ):
                (root / path).write_text(json.dumps(value), encoding="utf-8")
            (root / "instruments/a.md").write_text("# Alpha\n", encoding="utf-8")
            (root / "scripts/promptaria_specialized_executor.py").write_text(
                "def handler_alpha(context):\n    return {}\nHANDLERS = {'alpha': handler_alpha}\n",
                encoding="utf-8",
            )
            (root / "tests/test_alpha.py").write_text("alpha regression test\n", encoding="utf-8")
            (root / ".github/workflows/regression.yml").write_text(
                "python scripts/promptaria_specialized_executor.py\n", encoding="utf-8"
            )

            report = audit.build_inventory(root)

            self.assertEqual(report["catalog_integrity"]["status"], "conflicts_detected")
            alpha = next(item for item in report["instruments"] if item["instrument_id"] == "alpha")
            self.assertEqual(alpha["category"], "no_executor")
            self.assertFalse(alpha["functional_execution_verified"])
            self.assertFalse(alpha["evidence"]["title_consistent"])


if __name__ == "__main__":
    unittest.main()
