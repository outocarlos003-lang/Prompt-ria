import json
import tempfile
import unittest
from pathlib import Path

from scripts.auto_enable_new_promptual_instruments import activate_new_entries

OVERRIDE = "<!-- promptaria: continuous_automation: explicit -->"


class AutoEnableNewPromptualInstrumentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in ("config", "instruments", "tests"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        self.base = {"instruments": [
            {"id": "legacy-disabled", "title": "INSTRUMENTO PROMPTUAL antigo",
             "activation": {"enabled": False, "status": "inactive"}}
        ]}
        self.items = [
            {"id": "legacy-disabled", "title": "INSTRUMENTO PROMPTUAL antigo",
             "path": "instruments/legacy.md", "activation": {"enabled": False, "status": "inactive"},
             "ui": {"visible": False}},
            {"id": "new-promptual", "title": "NOVO INSTRUMENTO PROMPTUAL — TESTE",
             "path": "instruments/new.md", "activation": {"enabled": False, "status": "draft"},
             "ui": {"visible": False}},
            {"id": "new-ordinary", "title": "Novo prompt comum",
             "path": "instruments/ordinary.md", "activation": {"enabled": False, "status": "draft"},
             "ui": {"visible": False}},
        ]
        (self.root / "instruments/legacy.md").write_text("# INSTRUMENTO PROMPTUAL antigo\n", encoding="utf-8")
        (self.root / "instruments/new.md").write_text("# NOVO INSTRUMENTO PROMPTUAL — TESTE\n\nConteúdo.\n", encoding="utf-8")
        (self.root / "instruments/ordinary.md").write_text("# Novo prompt comum\n", encoding="utf-8")
        self.write_mirrors()

    def write_mirrors(self):
        registry = {"instruments": [json.loads(json.dumps(x)) for x in self.items]}
        catalog = {"instruments": [json.loads(json.dumps(x)) for x in self.items]}
        manifest = {"instruments": [
            {"id": x["id"], "title": x["title"], "path": x["path"], "aliases": [], "capabilities": []}
            for x in self.items
        ]}
        for relative, payload in (
            ("config/instrument-registry.json", registry),
            ("instrument-registry.json", registry),
            ("config/instrument-catalog.json", catalog),
            ("instrument-catalog.json", catalog),
            ("manifest.json", manifest),
            ("tests/manifest.json", manifest),
        ):
            (self.root / relative).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def read(self, relative):
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def test_new_promptual_title_defaults_to_recoverable_on_demand_in_every_mirror(self):
        classified = activate_new_entries(self.root, self.base)
        self.assertEqual(classified, ["new-promptual"])
        for relative in ("config/instrument-registry.json", "instrument-registry.json",
                         "config/instrument-catalog.json", "instrument-catalog.json"):
            item = next(x for x in self.read(relative)["instruments"] if x["id"] == "new-promptual")
            self.assertEqual(item["category"], "recoverable_on_demand")
            self.assertEqual(item["classification_basis"], "default_title_rule")
            self.assertEqual(item["activation"], {
                "enabled": True, "status": "active", "mode": "on_demand_title"
            })
            self.assertTrue(item["ui"]["visible"])
        for relative in ("manifest.json", "tests/manifest.json"):
            item = next(x for x in self.read(relative)["instruments"] if x["id"] == "new-promptual")
            self.assertEqual(item["category"], "recoverable_on_demand")
            self.assertEqual(item["classification_basis"], "default_title_rule")

    def test_continuous_automation_requires_exact_source_declaration_and_stays_disabled(self):
        source = self.root / "instruments/new.md"
        source.write_text(f"# NOVO INSTRUMENTO PROMPTUAL — TESTE\n\n{OVERRIDE}\n", encoding="utf-8")
        classified = activate_new_entries(self.root, self.base)
        self.assertEqual(classified, ["new-promptual"])
        for relative in ("config/instrument-registry.json", "instrument-registry.json",
                         "config/instrument-catalog.json", "instrument-catalog.json"):
            item = next(x for x in self.read(relative)["instruments"] if x["id"] == "new-promptual")
            self.assertEqual(item["category"], "continuous_automation")
            self.assertEqual(item["classification_basis"], "explicit_source_declaration")
            self.assertFalse(item["activation"]["enabled"])
            self.assertEqual(item["activation"]["status"], "prepared_no_executor")
            self.assertNotIn("mode", item["activation"])
            self.assertFalse(item["ui"]["visible"])
        for relative in ("manifest.json", "tests/manifest.json"):
            item = next(x for x in self.read(relative)["instruments"] if x["id"] == "new-promptual")
            self.assertEqual(item["category"], "continuous_automation")
            self.assertEqual(item["classification_basis"], "explicit_source_declaration")

    def test_existing_disabled_entry_is_never_enabled_even_if_its_title_matches(self):
        classified = activate_new_entries(self.root, self.base)
        self.assertEqual(classified, ["new-promptual"])
        legacy = next(x for x in self.read("config/instrument-registry.json")["instruments"]
                      if x["id"] == "legacy-disabled")
        self.assertEqual(legacy["activation"], {"enabled": False, "status": "inactive"})

    def test_ordinary_new_title_is_not_classified_or_activated(self):
        classified = activate_new_entries(self.root, self.base)
        self.assertNotIn("new-ordinary", classified)
        ordinary = next(x for x in self.read("config/instrument-registry.json")["instruments"]
                        if x["id"] == "new-ordinary")
        self.assertEqual(ordinary["activation"], {"enabled": False, "status": "draft"})
        self.assertNotIn("category", ordinary)


if __name__ == "__main__":
    unittest.main()
