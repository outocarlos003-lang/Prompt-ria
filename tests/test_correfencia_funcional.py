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

    def test_generic_title_mention_activates_own_function(self):
        r = self.validate("Aplique Instrumento Alfa à requisição.")
        self.assertEqual(r["matched_occurrences"], 1)
        self.assertTrue(r["matches"][0]["active"])
        self.assertEqual(r["matches"][0]["function_status"], "propria_preservada")
        self.assertTrue(r["matches"][0]["correferencia"])

    def test_silence_is_not_diverse(self):
        r = self.validate("Instrumento Alfa.")
        self.assertTrue(r["matches"][0]["active"])
        self.assertFalse(r["exceptions"])

    def test_ambiguous_context_favors_own_function(self):
        r = self.validate("Instrumento Alfa no contexto desta requisição.")
        self.assertTrue(r["matches"][0]["active"])
        self.assertFalse(r["exceptions"])

    def test_explicit_diverse_assignment_is_local_to_occurrence(self):
        r = self.validate(
            "Instrumento Alfa deve desempenhar outra função. Instrumento Beta."
        )
        self.assertEqual(r["matched_occurrences"], 2)
        alpha = next(m for m in r["matches"] if m["title"] == "Instrumento Alfa")
        beta = next(m for m in r["matches"] if m["title"] == "Instrumento Beta")
        self.assertFalse(alpha["active"])
        self.assertEqual(alpha["exception_scope"], "occurrence")
        self.assertTrue(beta["active"])

    def test_exception_does_not_project_to_other_occurrence_or_title(self):
        r = self.validate(
            "Instrumento Alfa deve desempenhar outra função. "
            "Instrumento Beta. Instrumento Alfa."
        )
        alpha = [m for m in r["matches"] if m["title"] == "Instrumento Alfa"]
        beta = next(m for m in r["matches"] if m["title"] == "Instrumento Beta")
        self.assertEqual(len(alpha), 2)
        self.assertFalse(alpha[0]["active"])
        self.assertTrue(alpha[1]["active"])
        self.assertTrue(beta["active"])

    def test_multiple_titles_are_mutual_cumulative_coordinated_and_nonexclusive(self):
        r = self.validate("Use Instrumento Alfa e Instrumento Beta.")
        self.assertEqual(r["matched_occurrences"], 2)
        self.assertEqual({m["title"] for m in r["matches"]},
                         {"Instrumento Alfa", "Instrumento Beta"})
        self.assertEqual(len(r["active_instruments"]), 2)
        self.assertEqual(len(r["execution_plan"]), 2)
        c = r["coordination"]
        self.assertTrue(c["coordination"]["is_mutual"])
        self.assertTrue(c["coordination"]["is_cumulative"])
        self.assertTrue(c["coordination"]["is_simultaneous"])
        self.assertTrue(c["coordination"]["is_nonexclusive"])

    def test_alias_is_only_navigation_hint_and_does_not_activate(self):
        r = self.validate("Use Alfa.")
        self.assertEqual(r["matched_occurrences"], 0)
        self.assertTrue(r["rule"]["aliases_are_non_activating_hints"])
        self.assertTrue(r["rule"]["capabilities_are_non_activating_hints"])

    def test_substring_does_not_create_false_positive(self):
        r = self.validate("Instrumento AlfaX não é o instrumento citado.")
        self.assertEqual(r["matched_occurrences"], 0)

    def test_original_text_and_local_context_are_preserved(self):
        r = self.validate(
            "Aplique Instrumento Alfa à requisição. "
            "Instrumento Alfa deve desempenhar outra função."
        )
        alpha = [m for m in r["matches"] if m["title"] == "Instrumento Alfa"]
        self.assertEqual(len(alpha), 2)
        first = next(m for m in alpha if m["active"])
        second = next(m for m in alpha if not m["active"])
        self.assertEqual(first["matched_text"], "Instrumento Alfa")
        self.assertIn("Aplique Instrumento Alfa", first["context_window"])
        self.assertIn("outra função", second["context_window"])

    def test_accent_and_case_normalization(self):
        r = self.validate("instrumento áLFA.")
        self.assertEqual(r["matched_occurrences"], 1)
        self.assertTrue(r["matches"][0]["active"])

    def test_manifest_is_not_required_for_unit_catalog(self):
        r = self.validate("Instrumento Alfa e Instrumento Beta.")
        self.assertEqual(r["status"], "ok")
        self.assertFalse(r["validation_errors"])

    def test_title_and_request_are_joint_activation_unit(self):
        r = self.validate(
            "Instrumento Alfa: executar a demanda concreta."
        )
        a = r["coordination"]["activation_unit"]
        self.assertTrue(a["title_plus_request_are_joint_entry"])
        self.assertTrue(a["title_plus_custom_request_are_joint_entry"])
        self.assertTrue(a["title_identifies_and_activates"])
        self.assertTrue(a["request_defines_concrete_application"])
        self.assertTrue(
            r["coordination"]["instrument_application_separation"]
            ["identity_is_not_changed_by_contextual_variation"]
        )

    def test_final_validation_traceability_and_writing_coordination(self):
        r = self.validate(
            "Instrumento Alfa e Instrumento Beta. "
            "Destino: Promptária/resultados; Origem: Promptária/entrada."
        )
        c = r["coordination"]
        self.assertTrue(c["writing_coordination"]["multiple_producers_require_role_assignment"])
        self.assertTrue(c["writing_coordination"]["destructive_resolution_requires_integrity_validation"])
        self.assertTrue(c["validation"]["final_validation_is_coordinated"])
        self.assertIn("integridade de ponta a ponta", c["validation"]["checks"])
        self.assertTrue(c["traceability"]["required"])
        self.assertEqual(len(c["traceability"]["occurrences"]), 2)

    def test_nocturna_is_not_default(self):
        normal = self.validate("Instrumento Alfa para executar a demanda.")
        d = normal["coordination"]["parameters"]["destination"]
        self.assertEqual(d["status"], "ambiguous")
        self.assertFalse(d["materialization_allowed"])

        nocturna = self.validate("Instrumento Alfa. Destino: Nocturna.")
        d = nocturna["coordination"]["parameters"]["destination"]
        self.assertEqual(d["status"], "resolved")
        self.assertTrue(d["is_nocturna"])
        self.assertTrue(d["materialization_allowed"])

    def test_negative_nocturna_does_not_authorize_materialization(self):
        r = self.validate("Instrumento Alfa; não use Nocturna como destino.")
        d = r["coordination"]["parameters"]["destination"]
        self.assertEqual(d["status"], "ambiguous")
        self.assertFalse(d["materialization_allowed"])

    def test_unknown_explicit_title_is_unresolved_not_invented(self):
        r = self.validate('título: "Instrumento Ômega Externo" para a demanda.')
        unresolved = r["coordination"]["unresolved_explicit_additional_titles"]
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0]["title"], "Instrumento Ômega Externo")
        self.assertEqual(unresolved[0]["status"], "catalog_missing")
        self.assertFalse(unresolved[0]["identity_presumed_from_title"])

    def test_repeated_occurrences_keep_one_participant_identity(self):
        r = self.validate("Instrumento Alfa. Instrumento Alfa. Instrumento Beta.")
        additional = r["coordination"]["additional_instruments"]
        self.assertEqual(len(additional), 2)
        alpha = next(x for x in additional if x["title"] == "Instrumento Alfa")
        self.assertEqual(alpha["occurrences"], 2)
        self.assertFalse(alpha["identity_presumed_from_title"])

    def test_architecture_has_all_nineteen_sections(self):
        r = self.validate("Instrumento Alfa.")
        policy = r["architecture_policy"]
        self.assertEqual(len(policy["sections"]), 19)
        self.assertTrue(policy["all_sections_accounted_for"])
        self.assertTrue(policy["instrument_prompt_elements_are_not_modified"])

    def test_github_limits_are_explicit(self):
        r = self.validate("Instrumento Alfa.")
        limits = r["coordination"]["github_limits"]
        self.assertTrue(limits["actions_process_only_received_request"])
        self.assertTrue(limits["does_not_observe_untransmitted_chat"])
        self.assertTrue(limits["does_not_create_permissions"])
        self.assertTrue(limits["does_not_create_access"])


if __name__ == "__main__":
    unittest.main()
