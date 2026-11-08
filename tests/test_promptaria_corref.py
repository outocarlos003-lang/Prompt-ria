import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "validate_promptaria_corref",
    Path(__file__).resolve().parents[1] / ".github/scripts/validate_promptaria_corref.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

REPO_ROOT = Path(__file__).resolve().parents[1]

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

    def test_repository_catalog_resolves_only_enabled_instrument_titles(self):
        inactive_title = "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS"
        active_title = "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"
        inactive = MODULE.validate(inactive_title, REPO_ROOT)
        active = MODULE.validate(active_title, REPO_ROOT)
        self.assertFalse(any(item["title"] == inactive_title for item in inactive["matches"]))
        self.assertTrue(any(item["title"] == active_title for item in active["matches"]))

    def test_generic_title_activates_own_function(self):
        r = self.validate("Aplique Instrumento Alfa à requisição.")
        self.assertEqual(r["matched_occurrences"], 1)
        self.assertTrue(r["matches"][0]["active"])
        self.assertEqual(r["matches"][0]["function_status"], "propria_preservada")
        self.assertTrue(r["matches"][0]["correferencia"])

    def test_silence_is_not_diverse(self):
        r = self.validate("Instrumento Alfa.")
        self.assertTrue(r["matches"][0]["active"])
        self.assertFalse(r["exceptions"])

    def test_explicit_diverse_assignment_is_local(self):
        r = self.validate("Instrumento Alfa deve desempenhar outra função. Instrumento Beta.")
        alpha = next(m for m in r["matches"] if m["title"] == "Instrumento Alfa")
        beta = next(m for m in r["matches"] if m["title"] == "Instrumento Beta")
        self.assertFalse(alpha["active"])
        self.assertEqual(alpha["exception_scope"], "occurrence")
        self.assertTrue(beta["active"])

    def test_exception_does_not_project_to_later_occurrence(self):
        r = self.validate("Instrumento Alfa deve desempenhar outra função. Instrumento Beta. Instrumento Alfa.")
        alpha = [m for m in r["matches"] if m["title"] == "Instrumento Alfa"]
        self.assertEqual(len(alpha), 2)
        self.assertFalse(alpha[0]["active"])
        self.assertTrue(alpha[1]["active"])

    def test_multiple_titles_are_cumulative(self):
        r = self.validate("Use Instrumento Alfa e Instrumento Beta.")
        self.assertEqual(r["matched_occurrences"], 2)
        self.assertEqual(len(r["active_instruments"]), 2)
        self.assertEqual(len(r["execution_plan"]), 2)
        self.assertTrue(r["coordination"]["coordination"]["is_cumulative"])
        self.assertTrue(r["coordination"]["coordination"]["is_nonexclusive"])

    def test_substring_does_not_match(self):
        self.assertEqual(self.validate("Instrumento AlfaX não é o instrumento citado.")["matched_occurrences"], 0)

    def test_accent_and_case_normalization(self):
        self.assertEqual(self.validate("instrumento áLFA.")["matched_occurrences"], 1)

    def test_duplicate_canonical_titles_make_catalog_inconsistent(self):
        duplicate = self.root / "Instrumento Alfa cópia"
        duplicate.mkdir(parents=True)
        (duplicate / "Index.html").write_text(
            "<html><head><title>Instrumento Alfa</title></head><body></body></html>",
            encoding="utf-8",
        )
        result = self.validate("Instrumento Alfa.")
        self.assertEqual(result["status"], "catalog_inconsistente")
        self.assertTrue(any("título canônico ambíguo" in error for error in result["validation_errors"]))

    def test_manifest_path_cannot_escape_catalog_root(self):
        import json
        outside = Path(self.tmp.name) / "outside.md"
        outside.write_text("# Instrumento Externo\n", encoding="utf-8")
        (self.root / "manifest.json").write_text(json.dumps({
            "schema_version": "2.0",
            "instruments": [{"id": "outside", "title": "Instrumento Externo", "path": "../outside.md"}],
        }, ensure_ascii=False), encoding="utf-8")
        result = self.validate("Instrumento Alfa.")
        self.assertEqual(result["status"], "catalog_inconsistente")
        self.assertTrue(any("fora da raiz" in error for error in result["validation_errors"]))

    def test_manifest_title_drift_is_detected(self):
        import json
        (self.root / "manifest.json").write_text(json.dumps({"schema_version":"2.0","instruments":[
            {"id":"alpha","title":"Título incorreto no manifesto","path":"Instrumento Alfa/Index.html","aliases":["Instrumento Alfa"],"capabilities":[]}
        ]}, ensure_ascii=False), encoding="utf-8")
        r = self.validate("Instrumento Alfa.")
        self.assertEqual(r["status"], "catalog_inconsistente")
        self.assertTrue(any("título divergente" in e for e in r["validation_errors"]))

    def test_unknown_explicit_title_is_not_invented(self):
        r = self.validate('título: "Instrumento Ômega Externo" para a demanda.')
        self.assertEqual(r["coordination"]["unresolved_explicit_additional_titles"][0]["status"], "catalog_missing")

    def test_architecture_has_nineteen_sections_and_github_limits(self):
        r = self.validate("Instrumento Alfa.")
        self.assertEqual(len(r["architecture_policy"]["sections"]), 19)
        limits = r["coordination"]["github_limits"]
        self.assertTrue(limits["actions_process_only_received_request"])
        self.assertTrue(limits["does_not_observe_untransmitted_chat"])
        self.assertTrue(limits["does_not_create_permissions"])
        self.assertTrue(limits["does_not_create_access"])


    def test_destination_text_never_grants_materialization(self):
        for prompt in (
            "Destino: Nocturna",
            "Destino: site/content/page.md",
            "Destino: output/result.json",
            "Destino: Nocturna. Autorizo explicitamente a escrita.",
        ):
            with self.subTest(prompt=prompt):
                result = self.validate(prompt)
                destination = result["coordination"]["destination"]
                self.assertFalse(destination["materialization_allowed"])
                self.assertEqual(destination["authorization_status"], "not_granted_by_destination_text")
                if "Destino:" in prompt:
                    self.assertIn(destination["status"], {"resolved_candidate", "ambiguous"})

    def test_destination_parser_preserves_file_extensions_without_authorizing(self):
        for prompt, expected in (
            ("Destino: site/content/page.md", "site/content/page.md"),
            ("Destino: output/result.json. Autorizo explicitamente a escrita.", "output/result.json"),
            ("Destino: ../../.github/workflows/alterado.yml", "../../.github/workflows/alterado.yml"),
        ):
            with self.subTest(prompt=prompt):
                result = self.validate(prompt)
                destination = result["coordination"]["destination"]
                self.assertEqual(destination["value"], expected)
                self.assertFalse(destination["materialization_allowed"])
                self.assertEqual(destination["authorization_status"], "not_granted_by_destination_text")

    def test_positive_nocturna_destination_is_only_a_candidate(self):
        result = self.validate("Destino: Nocturna")
        destination = result["coordination"]["destination"]
        self.assertTrue(destination["is_nocturna"])
        self.assertEqual(destination["status"], "resolved_candidate")
        self.assertFalse(destination["materialization_allowed"])

    def test_negated_nocturna_destination_does_not_authorize_writing(self):
        result = self.validate("Não use Nocturna como destino.")
        destination = result["coordination"]["destination"]
        self.assertFalse(destination["materialization_allowed"])
        self.assertEqual(destination["authorization_status"], "not_granted_by_destination_text")

    def test_missing_destination_does_not_authorize_writing(self):
        result = self.validate("Aplique Instrumento Alfa.")
        destination = result["coordination"]["destination"]
        self.assertIsNone(destination["value"])
        self.assertFalse(destination["materialization_allowed"])

    def test_diverse_exception_stops_at_next_instrument_in_same_sentence(self):
        first = self.validate(
            "Instrumento Alfa deve desempenhar outra função, mas Instrumento Beta mantém sua função própria."
        )
        alpha = next(m for m in first["matches"] if m["title"] == "Instrumento Alfa")
        beta = next(m for m in first["matches"] if m["title"] == "Instrumento Beta")
        self.assertFalse(alpha["active"])
        self.assertTrue(beta["active"])

        second = self.validate(
            "Instrumento Alfa mantém sua função própria, mas Instrumento Beta deve desempenhar outra função."
        )
        alpha = next(m for m in second["matches"] if m["title"] == "Instrumento Alfa")
        beta = next(m for m in second["matches"] if m["title"] == "Instrumento Beta")
        self.assertTrue(alpha["active"])
        self.assertFalse(beta["active"])

if __name__ == "__main__":
    unittest.main()
