"""Regression tests for the additive extended instrument identity contract."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.validate_instrument_reference_contract import validate

ROOT = Path(__file__).resolve().parents[1]


class InstrumentReferenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / "config/instrument-reference-contract.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((ROOT / "config/instrument-registry.json").read_text(encoding="utf-8"))

    def test_repository_contract_and_registry_are_compatible(self):
        self.assertEqual(validate(self.contract, self.registry), [])

    def test_rejects_non_additive_migration(self):
        contract = copy.deepcopy(self.contract)
        contract["compatibility"]["migration_mode"] = "replace"
        self.assertTrue(any("migration_mode" in error for error in validate(contract, self.registry)))

    def test_rejects_missing_activation_gate(self):
        registry = copy.deepcopy(self.registry)
        registry["instruments"][0]["activation"]["enabled"] = "true"
        self.assertTrue(any("activation.enabled must be boolean" in error for error in validate(self.contract, registry)))

    def test_rejects_schema_version_mismatch(self):
        registry = copy.deepcopy(self.registry)
        registry["schema_version"] = 3
        self.assertTrue(any("registry schema_version 2" in error for error in validate(self.contract, registry)))


if __name__ == "__main__":
    unittest.main()
