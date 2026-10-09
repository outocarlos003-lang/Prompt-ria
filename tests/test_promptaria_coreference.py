"""Regression tests for title normalization and safe coreference resolution."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import promptaria_coreference as coref


class NormalizeTests(unittest.TestCase):
    def test_ignores_case_accents_and_punctuation(self):
        self.assertEqual(coref.normalize("  AÇÃO: *Título!* "), "acao titulo")

    def test_does_not_collapse_distinct_words(self):
        self.assertNotEqual(coref.normalize("Prompt A"), coref.normalize("Prompt B"))


class ResolveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.first = self.root / "instrumento.md"
        self.first.write_text("# Título Oficial\nConteúdo preservado.\n", encoding="utf-8")
        self.entry = {"title": "Título Oficial", "path": str(self.first), "matched_by": "heading"}
        self.index = {coref.normalize("Título Oficial"): [self.entry]}

    def test_recovers_content_for_unique_match(self):
        result = coref.resolve("titulo oficial", self.index)
        self.assertEqual(result["status"], "identified_and_recovered")
        self.assertIn("Conteúdo preservado.", result["content"])

    def test_missing_title_is_not_found(self):
        result = coref.resolve("Não existe", self.index)
        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["matches"], [])

    def test_distinct_files_are_ambiguous(self):
        second = dict(self.entry, path=str(self.root / "outro.md"))
        result = coref.resolve("Título Oficial", {coref.normalize("Título Oficial"): [self.entry, second]})
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(len(result["matches"]), 2)

    def test_missing_content_is_reported(self):
        missing = dict(self.entry, path=str(self.root / "apagado.md"))
        result = coref.resolve("Título Oficial", {coref.normalize("Título Oficial"): [missing]})
        self.assertEqual(result["status"], "identified_content_unavailable")

    def test_index_keeps_same_title_in_different_files(self):
        second = self.root / "duplicado.md"
        second.write_text("# Título Oficial\nOutro conteúdo.\n", encoding="utf-8")
        with patch.object(coref, "git_files", return_value=[self.first, second]):
            index = coref.instrument_index()
        result = coref.resolve("Título Oficial", index)
        self.assertEqual(result["status"], "ambiguous")

    def test_manifest_canonical_title_is_indexed(self):
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({
            "instruments": [{
                "id": "instrumento-99",
                "title": "Título Canônico HTML",
                "path": "instrumentos/canonico/Index.html",
                "aliases": ["apelido curto"]
            }]
        }), encoding="utf-8")
        index = {}
        coref.add_manifest_entries(index, manifest)
        result = coref.resolve("titulo canonico html", index)
        self.assertEqual(result["status"], "identified_content_unavailable")
        self.assertEqual(result["matches"][0]["matched_by"], "manifest")
        self.assertEqual(coref.resolve("apelido curto", index)["status"], "not_found")


if __name__ == "__main__":
    unittest.main()
