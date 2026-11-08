#!/usr/bin/env python3
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from promptaria_context_router import analyze, registry_matches  # noqa: E402


class InstrumentRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "config/instrument-registry.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "tests/manifest.json").read_text(encoding="utf-8"))

    def test_template_is_registered_but_not_functionally_active(self):
        item = next(x for x in self.registry["instruments"] if x["id"] == self.registry["template_id"])
        self.assertFalse(item["ui"]["visible"])
        self.assertFalse(item["activation"]["enabled"])
        self.assertFalse(item["ui"]["featured"])
        self.assertEqual(item["path"], "instruments/modelo-instrumento-promptual-correferencia.md")

    def test_title_and_alias_matching_excludes_disabled_instruments(self):
        matches = registry_matches("use o MODELO FICTÍCIO instrumento modelo para uma nova demanda", self.registry)
        ids = [item["instrument_id"] for item in matches]
        self.assertNotIn("promptaria-instrument-template", ids)
        self.assertNotIn("coordinator", ids)
        active_matches = registry_matches("Nocturna", self.registry)
        active_ids = {item["instrument_id"] for item in active_matches}
        self.assertIn("nocturna-arquitetura-necessidade-identidade-sistemica", active_ids)
        self.assertNotIn("promptaria-instrument-template", active_ids)

    def test_multiple_instruments_are_retained(self):
        request = "automatize a correferência por título e atualize o catálogo de instrumentos do repositório usando Nocturna"
        result = analyze(request, self.manifest, self.registry)
        selected = set(result["selected_instrument_ids"])
        blocked = {
            instrument_id
            for candidate in result["task_candidates"]
            for instrument_id in candidate.get("blocked_inactive_instrument_ids", [])
        }
        self.assertNotIn("future-demand-preconfiguration", selected)
        self.assertNotIn("functional-correference-architecture", selected)
        self.assertNotIn("catalog-sitemap-preconfiguration", selected)
        self.assertIn("future-demand-preconfiguration", blocked)
        self.assertIn("functional-correference-architecture", blocked)
        self.assertIn("catalog-sitemap-preconfiguration", blocked)
        self.assertIn("nocturna-arquitetura-necessidade-identidade-sistemica", selected)
        self.assertIn("canonical_instrument_match", [item["task"] for item in result["task_candidates"]])

    def test_longer_canonical_title_shadows_only_its_embedded_short_title(self):
        registry = {"instruments": [
            {"id": "alpha", "title": "Arquitetura Unificada", "path": "instruments/alpha.md",
             "aliases": [], "activation": {"enabled": True}},
            {"id": "beta", "title": "Arquitetura Unificada de Execução Semântica", "path": "instruments/beta.md",
             "aliases": [], "activation": {"enabled": True}},
        ]}
        only_long = registry_matches("Arquitetura Unificada de Execução Semântica", registry)
        self.assertEqual([item["instrument_id"] for item in only_long], ["beta"])

        both_named = registry_matches(
            "Arquitetura Unificada; Arquitetura Unificada de Execução Semântica", registry
        )
        self.assertEqual({item["instrument_id"] for item in both_named}, {"alpha", "beta"})

    def test_registry_covers_every_instrument_file(self):
        registered = {item["path"] for item in self.registry["instruments"]}
        physical = {path.relative_to(ROOT).as_posix() for path in (ROOT / "instruments").glob("*.md")}
        self.assertEqual(physical, registered)


if __name__ == "__main__":
    unittest.main()
