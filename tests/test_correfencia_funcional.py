#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

SPEC = spec_from_file_location("validate_promptaria_corref", Path(".github/scripts/validate_promptaria_corref.py"))
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class CorreferenciaRulesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "Promptária"
        for name in ("Instrumento Alfa", "Instrumento Beta"):
            d = root / name
            d.mkdir(parents=True)
            (d / "Index.html").write_text(
                f"<html><head><title>{name}</title></head><body><h1>{name}</h1></body></html>",
                encoding="utf-8",
            )
        self.root = root

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self, prompt):
        return MODULE.validate(prompt, self.root)

    def test_generic_mention_preserves_function(self):
        r = self.validate("Aplique Instrumento Alfa à requisição.")
        self.assertEqual(r["matched_occurrences"], 1)
        self.assertTrue(r["matches"][0]["active"])
        self.assertEqual(r["matches"][0]["function_status"], "propria_preservada")

    def test_silence_is_not_diverse(self):
        r = self.validate("Instrumento Alfa.")
        self.assertTrue(r["matches"][0]["active"])
        self.assertFalse(r["exceptions"])

    def test_explicit_diverse_assignment_is_local(self):
        r = self.validate("Instrumento Alfa deve atuar como outro papel. Instrumento Beta.")
        self.assertEqual(r["matched_occurrences"], 2)
        self.assertFalse(r["matches"][0]["active"])
        self.assertEqual(r["matches"][0]["exception_scope"], "occurrence")
        self.assertTrue(r["matches"][1]["active"])

    def test_multiple_titles_are_cumulative(self):
        r = self.validate("Use Instrumento Alfa e Instrumento Beta.")
        self.assertEqual(r["matched_occurrences"], 2)
        self.assertEqual({m["title"] for m in r["matches"]}, {"Instrumento Alfa", "Instrumento Beta"})
        self.assertEqual(len(r["active_instruments"]), 2)

    def test_exception_does_not_project_to_other_title(self):
        r = self.validate("Instrumento Alfa deve desempenhar outro papel; Instrumento Beta.")
        self.assertFalse(r["matches"][0]["active"])
        self.assertTrue(r["matches"][1]["active"])

    def test_repeated_occurrences_are_individual(self):
        r = self.validate("Instrumento Alfa. Instrumento Alfa deve atuar como outro papel.")
        self.assertEqual(r["matched_occurrences"], 2)
        self.assertTrue(r["matches"][0]["active"])
        self.assertFalse(r["matches"][1]["active"])

    def test_ambiguity_favors_own_function(self):
        r = self.validate("Considere Instrumento Alfa no contexto desta requisição.")
        self.assertTrue(r["matches"][0]["active"])
        self.assertFalse(r["exceptions"])

if __name__ == "__main__":
    unittest.main()
