import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from promptaria_resolver import read_instruments, resolve


class AuxiliaryProtocolTests(unittest.TestCase):
    def test_auxiliary_protocol_is_enabled_but_not_an_operational_member(self):
        instruments = read_instruments(ROOT / "instruments")
        auxiliary = [item for item in instruments if item.get("id") == "protocol-update-integrity"]
        self.assertEqual(len(auxiliary), 1)
        self.assertTrue(auxiliary[0]["active"])
        self.assertTrue(auxiliary[0]["auxiliary"])
        self.assertEqual(auxiliary[0]["repository_path"],
                         "auxiliary-protocols/protocolo-operacional-atualizacao-integridade-acervo.md")
        operational = [item for item in instruments if not item.get("auxiliary")]
        self.assertEqual(len(operational), 8)

    def test_auxiliary_protocol_is_not_selected_by_ordinary_title_mention(self):
        instruments = read_instruments(ROOT / "instruments")
        title = next(item["title"] for item in instruments if item.get("auxiliary"))
        self.assertEqual(resolve("Considere o título " + title + " como texto comum.", instruments), [])

    def test_auxiliary_protocol_is_recovered_by_explicit_id_and_title(self):
        instruments = read_instruments(ROOT / "instruments")
        by_id = resolve("instrument_id: protocol-update-integrity", instruments)
        self.assertEqual(len(by_id), 1)
        self.assertEqual(by_id[0]["function_status"], "auxiliary_explicit")
        self.assertTrue(by_id[0]["activation"])
        title = next(item["title"] for item in instruments if item.get("auxiliary"))
        by_title = resolve("instrument_title: " + title, instruments)
        self.assertEqual(len(by_title), 1)
        self.assertEqual(by_title[0]["id"], "protocol-update-integrity")
        self.assertTrue(by_title[0]["activation"])

    def test_operational_indexes_do_not_contain_auxiliary_protocol(self):
        for relative in (
            "config/instrument-registry.json",
            "config/instrument-catalog.json",
            "instrument-registry.json",
            "instrument-catalog.json",
            "tests/manifest.json",
            "config/instrument-execution-map.json",
        ):
            data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertNotIn("protocol-update-integrity",
                             {item.get("id") for item in data.get("instruments", [])},
                             relative)

    def test_auxiliary_activation_and_source_are_preserved(self):
        data = json.loads((ROOT / "auxiliary-protocols/registry.json").read_text(encoding="utf-8"))
        item = next(item for item in data["instruments"] if item["id"] == "protocol-update-integrity")
        self.assertEqual(item["activation"], {"enabled": True, "status": "active"})
        self.assertTrue((ROOT / item["path"]).is_file())
        self.assertFalse((ROOT / "instruments/protocolo-operacional-atualizacao-integridade-acervo.md").exists())


if __name__ == "__main__":
    unittest.main()
