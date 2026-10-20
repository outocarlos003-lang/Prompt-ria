"""Cross-check canonical instrument identity across registry, catalog, manifest and executor map."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "instrument-registry.json"
CATALOG = ROOT / "config" / "instrument-catalog.json"
EXECUTION_MAP = ROOT / "config" / "instrument-execution-map.json"
MANIFEST = ROOT / "tests" / "manifest.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def unique_by_id(entries: list[dict], label: str) -> dict[str, dict]:
    ids = [entry.get("id") for entry in entries]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        raise AssertionError(f"{label} contém IDs duplicados: {duplicates}")
    if any(not isinstance(value, str) or not value.strip() for value in ids):
        raise AssertionError(f"{label} contém ID vazio ou inválido.")
    return {entry["id"]: entry for entry in entries}


class CanonicalArtifactIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = read_json(REGISTRY)["instruments"]
        cls.catalog = read_json(CATALOG)["instruments"]
        cls.manifest = read_json(MANIFEST)["instruments"]
        cls.execution_map = read_json(EXECUTION_MAP)["instruments"]
        cls.registry_by_id = unique_by_id(cls.registry, "registro")
        cls.catalog_by_id = unique_by_id(cls.catalog, "catálogo")
        cls.manifest_by_id = unique_by_id(cls.manifest, "manifesto")
        cls.execution_by_id = unique_by_id(cls.execution_map, "mapa de execução")

    def test_registry_catalog_manifest_and_execution_map_have_same_ids(self):
        expected = set(self.registry_by_id)
        for label, actual in (
            ("catálogo", set(self.catalog_by_id)),
            ("manifesto", set(self.manifest_by_id)),
            ("mapa de execução", set(self.execution_by_id)),
        ):
            with self.subTest(artifact=label):
                self.assertEqual(actual, expected, f"IDs divergentes em {label}: ausentes={sorted(expected-actual)}, extras={sorted(actual-expected)}")

    def test_identity_fields_match_across_all_artifacts(self):
        for instrument_id, source in self.registry_by_id.items():
            for label, mapping in (
                ("catálogo", self.catalog_by_id),
                ("manifesto", self.manifest_by_id),
                ("mapa de execução", self.execution_by_id),
            ):
                with self.subTest(instrument=instrument_id, artifact=label):
                    item = mapping[instrument_id]
                    for field in ("title", "path"):
                        self.assertEqual(item.get(field), source.get(field), f"{instrument_id}: {field} diverge em {label}")

    def test_catalog_mirrors_activation_and_ui_visibility(self):
        for instrument_id, source in self.registry_by_id.items():
            catalog_item = self.catalog_by_id[instrument_id]
            with self.subTest(instrument=instrument_id):
                self.assertEqual(catalog_item.get("activation"), source.get("activation"))
                self.assertEqual(catalog_item.get("ui"), source.get("ui"))
                enabled = source.get("activation", {}).get("enabled") is True
                visible = source.get("ui", {}).get("visible") is True
                self.assertEqual(visible, enabled, "A visibilidade deve corresponder ao estado de ativação.")

    def test_active_instruments_have_implemented_handler_evidence(self):
        for instrument_id, source in self.registry_by_id.items():
            if source.get("activation", {}).get("enabled") is not True:
                continue
            entry = self.execution_by_id[instrument_id]
            with self.subTest(instrument=instrument_id):
                self.assertEqual(entry.get("specialized_execution_status"), "implemented")
                self.assertIs(entry.get("side_effects_authorized_by_title"), False)
                executor = entry.get("specialized_executor")
                handler = entry.get("specialized_handler")
                self.assertIsInstance(executor, str)
                self.assertTrue(executor.strip())
                executor_path = (ROOT / executor).resolve()
                self.assertTrue(executor_path.is_relative_to(ROOT.resolve()), "Executor fora da raiz do repositório.")
                self.assertTrue(executor_path.is_file(), f"Executor não encontrado: {executor}")
                self.assertIsInstance(handler, str)
                self.assertRegex(handler, r"^[A-Za-z_][A-Za-z0-9_]*$")
                source_code = executor_path.read_text(encoding="utf-8")
                self.assertRegex(source_code, rf"(?m)^def\s+{re.escape(handler)}\s*\(", f"Handler não encontrado: {handler}")

    def test_inactive_instruments_are_not_visible(self):
        for item in self.registry:
            if item.get("activation", {}).get("enabled") is not True:
                with self.subTest(instrument=item.get("id")):
                    self.assertIsNot(item.get("ui", {}).get("visible"), True)


if __name__ == "__main__":
    unittest.main()
