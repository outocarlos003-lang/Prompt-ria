import json
import tempfile
import unittest
from pathlib import Path

from scripts.resolve_auxiliary_protocol import recover_protocol
from scripts.promptaria_specialized_executor import execute

class AuxiliaryProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "auxiliary-protocols").mkdir()
        self.title = "PROTOCOLO AUXILIAR DE TESTE"
        self.protocol = {"id": "aux-test", "title": self.title,
                         "path": "auxiliary-protocols/test.md",
                         "activation": {"enabled": True, "status": "active"},
                         "operational_membership": False}
        (self.root / self.protocol["path"]).write_text("# " + self.title + "\n\nConteúdo integral.\n", encoding="utf-8")
        (self.root / "auxiliary-protocols/registry.json").write_text(
            json.dumps({"operational_membership": False, "protocols": [self.protocol]}, ensure_ascii=False),
            encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_explicit_recovery_by_id_and_title_preserves_full_content(self):
        by_id = recover_protocol(self.root, instrument_id="aux-test")
        by_title = recover_protocol(self.root, title=self.title)
        expected = "# " + self.title + "\n\nConteúdo integral.\n"
        self.assertEqual(by_id["content"], expected)
        self.assertEqual(by_title["id"], "aux-test")
        self.assertEqual(by_id["activation"], {"enabled": True, "status": "active"})
        self.assertFalse(by_id["operational_membership"])

    def test_rejects_unknown_and_disabled_auxiliary_records(self):
        with self.assertRaises(LookupError):
            recover_protocol(self.root, title="Título inexistente")
        self.protocol["activation"] = {"enabled": False, "status": "inactive"}
        (self.root / "auxiliary-protocols/registry.json").write_text(
            json.dumps({"protocols": [self.protocol]}), encoding="utf-8")
        with self.assertRaises(ValueError):
            recover_protocol(self.root, instrument_id="aux-test")

    def test_repository_protocol_is_enabled_separate_and_explicitly_executable(self):
        root = Path(__file__).resolve().parents[1]
        recovered = recover_protocol(root, instrument_id="protocol-update-integrity")
        self.assertTrue(recovered["activation"]["enabled"])
        self.assertEqual(recovered["activation"]["status"], "active")
        self.assertFalse(recovered["operational_membership"])
        for path in ("config/instrument-registry.json", "config/instrument-catalog.json",
                     "config/instrument-execution-map.json", "tests/manifest.json",
                     "instrument-registry.json", "instrument-catalog.json", "instrument-execution-map.json", "manifest.json"):
            data = json.loads((root / path).read_text(encoding="utf-8"))
            self.assertNotIn("protocol-update-integrity", {item["id"] for item in data["instruments"]})
        result = execute({"request": "Solicitação explícita de integridade",
                          "instrument_ids": ["protocol-update-integrity"]})
        self.assertIn("protocol-update-integrity", result["selected_instrument_ids"])
        self.assertEqual(result["results"][0]["handler"], "build-integrity-preservation-plan")

if __name__ == "__main__":
    unittest.main()
