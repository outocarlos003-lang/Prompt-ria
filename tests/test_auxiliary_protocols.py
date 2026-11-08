from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.resolve_auxiliary_protocol import resolve
from scripts.promptaria_registry_audit import audit
from scripts.promptaria_context_router import BASE_IDS
from scripts.promptaria_resolver import read_instruments, resolve as resolve_operational

IDENT = "protocol-update-integrity"
TITLE = "PROTOCOLO OPERACIONAL DE ATUALIZAÇÃO, REINTEGRAÇÃO E PRESERVAÇÃO FUNCIONAL DO ACERVO DE INSTRUMENTOS PROMPTUAIS DO PROMPTÁRIA"
SOURCE = "auxiliary-protocols/protocolo-operacional-atualizacao-integridade-acervo.md"


class AuxiliaryProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.aux = json.loads((ROOT / "auxiliary-protocols/registry.json").read_text(encoding="utf-8"))

    def test_exact_title_and_id_recover_enabled_auxiliary_source(self) -> None:
        for reference in (TITLE, IDENT, f"instrument_id:{IDENT}", "preservação funcional do acervo"):
            with self.subTest(reference=reference):
                result = resolve(reference)
                self.assertEqual(result["instrument_id"], IDENT)
                self.assertEqual(result["path"], SOURCE)
                self.assertTrue(result["activation"]["enabled"])
                self.assertEqual(result["activation"]["status"], "active")
                self.assertEqual(result["membership"], "auxiliary")
                self.assertFalse(result["operational_member"])
                self.assertFalse(result["operational_counted"])
                self.assertTrue(result["content"].startswith("# " + TITLE))

    def test_auxiliary_identity_is_absent_from_every_operational_index(self) -> None:
        paths = (
            "config/instrument-registry.json",
            "config/instrument-catalog.json",
            "instrument-registry.json",
            "instrument-catalog.json",
            "config/instrument-execution-map.json",
            "instrument-execution-map.json",
            "manifest.json",
            "tests/manifest.json",
        )
        for relative in paths:
            payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertNotIn(IDENT, {item.get("id") for item in payload.get("instruments", [])}, relative)

    def test_operational_registry_count_decreases_by_exactly_one(self) -> None:
        registry = json.loads((ROOT / "config/instrument-registry.json").read_text(encoding="utf-8"))
        catalog = json.loads((ROOT / "config/instrument-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(len(registry["instruments"]), 8)
        self.assertEqual(len(catalog["instruments"]), 8)
        self.assertNotIn(IDENT, BASE_IDS)

    def test_audit_counts_auxiliary_separately(self) -> None:
        result = audit(ROOT / "config/instrument-registry.json", ROOT)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["instrument_count"], 8)
        self.assertEqual(result["auxiliary_protocol_count"], 1)
        self.assertTrue(result["auxiliary_protocols_checked"])

    def test_auxiliary_protocol_is_not_preloaded_or_auto_selected_operationally(self) -> None:
        operational = read_instruments(ROOT / "instruments")
        self.assertNotIn(IDENT, {item.get("id") for item in operational})
        self.assertNotIn(TITLE, {item.get("title") for item in operational})
        self.assertFalse(resolve_operational(TITLE, operational))

    def test_source_is_not_under_operational_instruments_directory(self) -> None:
        self.assertTrue((ROOT / SOURCE).is_file())
        self.assertFalse((ROOT / "instruments/protocolo-operacional-atualizacao-integridade-acervo.md").exists())
        self.assertFalse(any(p.name == "protocolo-operacional-atualizacao-integridade-acervo.md"
                             for p in (ROOT / "instruments").glob("*.md")))


if __name__ == "__main__":
    unittest.main()
