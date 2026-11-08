import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITOR = ROOT / "scripts" / "promptaria_audit_inventory.py"


class PromptariaInventoryAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "instruments").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "config").mkdir()

    def write_json(self, path, value):
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def run_audit(self, strict=False):
        command = [
            sys.executable, str(AUDITOR),
            "--instruments", str(self.root / "instruments"),
            "--manifest", str(self.root / "tests/manifest.json"),
            "--registry", str(self.root / "config/instrument-registry.json"),
        ]
        if strict:
            command.append("--strict")
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8")

    def configure(self, registered=True):
        relative = "instruments/alpha.md"
        (self.root / relative).write_text("# Instrumento Alfa\n\nConteúdo.\n", encoding="utf-8")
        entry = {"id": "alpha", "title": "Instrumento Alfa", "path": relative,
                 "aliases": [], "activation": {"enabled": False, "status": "prepared"}}
        manifest = {"schema_version": 2, "instruments": [entry] if registered else []}
        registry = {"schema_version": 2, "instruments": [entry] if registered else []}
        self.write_json(self.root / "tests/manifest.json", manifest)
        self.write_json(self.root / "config/instrument-registry.json", registry)

    def test_complete_inventory_is_classified_without_activation(self):
        self.configure()
        proc = self.run_audit(strict=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertTrue(report["summary"]["complete"])
        self.assertEqual(report["summary"]["markdown_files"], 1)
        self.assertEqual(report["instruments"][0]["manifest_status"], "registered")
        self.assertFalse(report["instruments"][0]["activation_enabled"])

    def test_missing_manifest_and_registry_entries_fail_strict_mode(self):
        self.configure(registered=False)
        proc = self.run_audit(strict=True)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertFalse(report["summary"]["complete"])
        self.assertEqual(report["summary"]["errors"], 2)

    def test_duplicate_ids_are_reported(self):
        self.configure()
        manifest_path = self.root / "tests/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["instruments"].append(dict(manifest["instruments"][0], path="instruments/other.md"))
        self.write_json(manifest_path, manifest)
        proc = self.run_audit()
        report = json.loads(proc.stdout)
        self.assertTrue(any("id duplicado" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
