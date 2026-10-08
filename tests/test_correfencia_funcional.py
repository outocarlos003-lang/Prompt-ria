#!/usr/bin/env python3
import tempfile
import unittest
import json
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
        manifest = {
            "schema_version": "3.0",
            "instruments": [
                {
                    "id": "instrumento-alfa",
                    "title": "Instrumento Alfa",
                    "path": "Promptária/Instrumento Alfa/Index.html",
                    "aliases": ["alfa"],
                    "capabilities": ["capacidade alfa"],
                    "canonical_reference": {"id": "instrumento-alfa", "title": "Instrumento Alfa", "path": "Promptária/Instrumento Alfa/Index.html"},
                },
                {
                    "id": "instrumento-beta",
                    "title": "Instrumento Beta",
                    "path": "Promptária/Instrumento Beta/Index.html",
                    "aliases": ["beta"],
                    "capabilities": ["capacidade beta"],
                    "canonical_reference": {"id": "instrumento-beta", "title": "Instrumento Beta", "path": "Promptária/Instrumento Beta/Index.html"},
                },
            ],
        }
        (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
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
        self.assertEqual(len(r["execution_plan"]), 2)

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

    def test_substring_does_not_create_false_positive(self):
        r = self.validate("Instrumento AlfaX não é o instrumento citado.")
        self.assertEqual(r["matched_occurrences"], 0)

    def test_original_text_and_local_context_are_preserved(self):
        r = self.validate("Aplique Instrumento Alfa à requisição. Instrumento Alfa deve atuar como outro papel.")
        self.assertEqual(r["matched_occurrences"], 2)
        first = next(m for m in r["matches"] if m["active"])
        second = next(m for m in r["matches"] if not m["active"])
        self.assertEqual(first["matched_text"], "Instrumento Alfa")
        self.assertIn("Aplique Instrumento Alfa", first["context_window"])
        self.assertIn("deve atuar como outro papel", second["context_window"])

    def test_accent_and_case_normalization(self):
        r = self.validate("instrumento áLFA.")
        self.assertEqual(r["matched_occurrences"], 1)
        self.assertTrue(r["matches"][0]["active"])

    def test_manifest_is_required_as_executable_contract(self):
        (self.root / "manifest.json").unlink()
        r = self.validate("Instrumento Alfa e Instrumento Beta.")
        self.assertEqual(r["status"], "blocked_contract")
        self.assertEqual(r["active_instruments"], [])

    def test_identity_mismatch_blocks_activation(self):
        path = self.root / "Instrumento Alfa" / "Index.html"
        path.write_text("<html><head><title>Outro Instrumento</title></head><body></body></html>", encoding="utf-8")
        r = self.validate("Instrumento Alfa.")
        self.assertEqual(r["matched_occurrences"], 1)
        self.assertFalse(r["matches"][0]["identity_verified"])
        self.assertFalse(r["matches"][0]["active"])
        self.assertEqual(r["matches"][0]["activation_status"], "blocked_identity")

    def test_capability_is_discovery_only_and_never_activates(self):
        r = self.validate("capacidade alfa.")
        self.assertEqual(r["matched_occurrences"], 0)
        self.assertEqual(r["active_instruments"], [])

    def test_coordination_preserves_roles_and_open_cardinality(self):
        r = self.validate(
            "Acionamento Coordenado de Instrumentos Promptuais + Instrumento Alfa + Instrumento Beta. "
            "Destino: Promptária/resultados; Origem: Promptária/entrada."
        )
        c = r["coordination"]
        self.assertTrue(c["preserves_existing_correfencia"])
        self.assertFalse(c["coordination"]["is_fusion"])
        self.assertTrue(c["cardinality"]["additional_is_unbounded"])
        self.assertEqual(c["cardinality"]["maximum_additional"], None)
        self.assertEqual(
            {x["title"] for x in c["additional_instruments"]},
            {"Instrumento Alfa", "Instrumento Beta"},
        )
        self.assertEqual(c["parameters"]["origin"]["value"], "Promptária/entrada")
        self.assertEqual(c["parameters"]["destination"]["status"], "resolved")
        self.assertTrue(c["traceability"]["required"])
        self.assertTrue(c["activation"]["coordinator_title_present"])

    def test_fixed_and_coordinator_are_explicit_participants_even_when_missing(self):
        r = self.validate("Instrumento Alfa para a demanda.")
        participants = r["coordination"]["participants"]
        roles = {p["role"] for p in participants}
        self.assertIn("coordinator", roles)
        self.assertIn("fixed_github_instrument", roles)
        fixed = next(p for p in participants if p["role"] == "fixed_github_instrument")
        self.assertEqual(fixed["status"], "catalog_missing")
        self.assertFalse(next(p for p in participants if p["role"] == "coordinator")["activated_by_current_prompt"])

    def test_nocturna_requires_explicit_destination_and_is_not_default(self):
        normal = self.validate("Instrumento Alfa para executar a demanda.")
        self.assertEqual(normal["coordination"]["parameters"]["destination"]["status"], "ambiguous")
        self.assertFalse(normal["coordination"]["parameters"]["destination"]["materialization_allowed"])

        nocturna = self.validate("Instrumento Alfa. Destino: Nocturna.")
        d = nocturna["coordination"]["parameters"]["destination"]
        self.assertEqual(d["status"], "resolved")
        self.assertTrue(d["is_nocturna"])
        self.assertTrue(d["materialization_allowed"])

    def test_multiple_occurrences_do_not_duplicate_participant_identity(self):
        r = self.validate("Instrumento Alfa. Instrumento Alfa. Instrumento Beta.")
        additional = r["coordination"]["additional_instruments"]
        self.assertEqual(len(additional), 2)
        alpha = next(x for x in additional if x["title"] == "Instrumento Alfa")
        self.assertEqual(alpha["occurrences"], 2)
        self.assertFalse(alpha["identity_presumed_from_title"])

    def test_explicit_unknown_additional_title_is_represented_as_unresolved(self):
        r = self.validate('título: "Instrumento Ômega Externo" para a demanda.')
        unresolved = r["coordination"]["unresolved_explicit_additional_titles"]
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0]["title"], "Instrumento Ômega Externo")
        self.assertEqual(unresolved[0]["status"], "catalog_missing")
        self.assertFalse(unresolved[0]["identity_presumed_from_title"])
        self.assertTrue(r["coordination"]["cardinality"]["additional_is_unbounded"])

    def test_title_and_request_are_joint_activation_unit(self):
        r = self.validate("Acionamento Coordenado de Instrumentos Promptuais: executar a demanda concreta.")
        a = r["coordination"]["activation_unit"]
        self.assertTrue(a["title_plus_custom_request_forms_activation_unit"])
        self.assertTrue(a["title_identifies_and_activates"])
        self.assertTrue(a["request_defines_concrete_application"])
        self.assertTrue(r["coordination"]["instrument_application_separation"]["identity_is_not_changed_by_contextual_variation"])

    def test_final_validation_and_writing_coordination_are_structured(self):
        r = self.validate("Instrumento Alfa e Instrumento Beta. Destino: Promptária/resultados.")
        c = r["coordination"]
        self.assertTrue(c["writing_coordination"]["multiple_producers_require_role_assignment"])
        self.assertTrue(c["writing_coordination"]["destructive_resolution_requires_integrity_validation"])
        self.assertTrue(c["validation"]["final_validation_is_coordinated"])
        self.assertIn("integridade de ponta a ponta", c["validation"]["checks"])

    def test_nocturna_mention_without_positive_destination_does_not_authorize_write(self):
        r = self.validate("Instrumento Alfa; não use Nocturna como destino.")
        d = r["coordination"]["parameters"]["destination"]
        self.assertEqual(d["status"], "ambiguous")
        self.assertFalse(d["materialization_allowed"])


if __name__ == "__main__":
    unittest.main()
