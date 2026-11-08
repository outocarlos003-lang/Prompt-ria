import json
import tempfile
import unittest
from pathlib import Path

from scripts.auto_enable_new_promptual_instruments import activate_new_entries


class AutoEnableNewPromptualInstrumentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        (self.root / "instruments").mkdir()
        self.base = {"instruments": [{"id": "legacy-disabled", "title": "Old prompt", "activation": {"enabled": False, "status": "inactive"}}]}
        current = {"instruments": [
            {"id": "legacy-disabled", "title": "Old prompt", "path": "instruments/old.md", "activation": {"enabled": False, "status": "inactive"}},
            {"id": "new-promptual", "title": "NOVO INSTRUMENTO PROMPTUAL — TESTE", "path": "instruments/new.md", "activation": {"enabled": False, "status": "draft"}},
            {"id": "new-ordinary", "title": "Novo prompt comum", "path": "instruments/ordinary.md", "activation": {"enabled": False, "status": "draft"}},
        ]}
        (self.root / "instruments/new.md").write_text("# NOVO INSTRUMENTO PROMPTUAL — TESTE\n\nConteúdo.\n", encoding="utf-8")
        (self.root / "instruments/ordinary.md").write_text("# Novo prompt comum\n", encoding="utf-8")
        for name in ("config/instrument-registry.json", "instrument-registry.json"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(current), encoding="utf-8")
        catalog = {"instruments": [dict(x) for x in current["instruments"]]}
        for name in ("config/instrument-catalog.json", "instrument-catalog.json"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(catalog), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_only_new_named_promptual_instrument_is_enabled_in_all_mirrors(self):
        activated = activate_new_entries(self.root, self.base)
        self.assertEqual(activated, ["new-promptual"])
        for name in ("config/instrument-registry.json", "instrument-registry.json",
                     "config/instrument-catalog.json", "instrument-catalog.json"):
            data = json.loads((self.root / name).read_text(encoding="utf-8"))
            items = {x["id"]: x for x in data["instruments"]}
            self.assertEqual(items["new-promptual"]["activation"], {"enabled": True, "status": "active"})
            self.assertEqual(items["legacy-disabled"]["activation"], {"enabled": False, "status": "inactive"})
            self.assertEqual(items["new-ordinary"]["activation"], {"enabled": False, "status": "draft"})

    def test_existing_disabled_entry_is_never_enabled_even_if_title_matches(self):
        self.base["instruments"].append({"id": "legacy-disabled", "title": "INSTRUMENTO PROMPTUAL antigo"})
        data = json.loads((self.root / "config/instrument-registry.json").read_text(encoding="utf-8"))
        data["instruments"][0]["title"] = "INSTRUMENTO PROMPTUAL antigo"
        (self.root / "config/instrument-registry.json").write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(activate_new_entries(self.root, self.base), ["new-promptual"])
        after = json.loads((self.root / "config/instrument-registry.json").read_text(encoding="utf-8"))
        legacy = next(x for x in after["instruments"] if x["id"] == "legacy-disabled")
        self.assertEqual(legacy["activation"], {"enabled": False, "status": "inactive"})

    def test_second_run_is_idempotent(self):
        self.assertEqual(activate_new_entries(self.root, self.base), ["new-promptual"])
        self.assertEqual(activate_new_entries(self.root, self.base), ["new-promptual"])


if __name__ == "__main__":
    unittest.main()
