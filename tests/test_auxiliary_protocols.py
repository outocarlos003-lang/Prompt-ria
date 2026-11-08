import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_ID = "protocol-update-integrity"
TARGET_TITLE = "PROTOCOLO OPERACIONAL DE ATUALIZAÇÃO, REINTEGRAÇÃO E PRESERVAÇÃO FUNCIONAL DO ACERVO DE INSTRUMENTOS PROMPTUAIS DO PROMPTÁRIA"
TARGET_PATH = "auxiliary-protocols/protocolo-operacional-atualizacao-integridade-acervo.md"


class AuxiliaryProtocolTests(unittest.TestCase):
    def read(self, relative):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_auxiliary_is_enabled_but_outside_every_operational_catalog(self):
        auxiliary = self.read("auxiliary-protocols/registry.json")
        item = next(x for x in auxiliary["instruments"] if x["id"] == TARGET_ID)
        self.assertTrue(item["activation"]["enabled"])
        self.assertEqual(item["activation"]["status"], "active")
        self.assertEqual(item["membership"], "auxiliary")
        self.assertEqual(item["resolution_policy"], "explicit_only")
        for relative in ("config/instrument-registry.json", "config/instrument-catalog.json",
                         "config/instrument-execution-map.json", "tests/manifest.json", "manifest.json"):
            ids = [x["id"] for x in self.read(relative)["instruments"]]
            self.assertNotIn(TARGET_ID, ids, relative)

    def test_full_source_is_at_auxiliary_path_and_keeps_canonical_title(self):
        source = (ROOT / TARGET_PATH).read_text(encoding="utf-8")
        self.assertTrue(source.startswith("# " + TARGET_TITLE))
        self.assertFalse((ROOT / "instruments/protocolo-operacional-atualizacao-integridade-acervo.md").exists())

    def test_python_resolver_recovers_only_on_explicit_id_or_title(self):
        from scripts.promptaria_resolver import read_instruments, resolve
        instruments = read_instruments(ROOT / "instruments")
        self.assertFalse(any(x.get("id") == TARGET_ID for x in instruments if not x.get("explicit_only")))
        self.assertEqual(resolve("uma demanda ordinária sem referência ao protocolo", instruments), [])
        by_id = resolve("instrument_id:protocol-update-integrity", instruments)
        self.assertEqual(len(by_id), 1)
        self.assertEqual(by_id[0]["id"], TARGET_ID)
        self.assertTrue(by_id[0]["activation"])
        by_title = resolve("instrument_title: " + TARGET_TITLE, instruments)
        self.assertEqual(len(by_title), 1)
        self.assertEqual(by_title[0]["id"], TARGET_ID)


if __name__ == "__main__":
    unittest.main()
