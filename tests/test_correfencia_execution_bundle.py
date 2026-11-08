import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_correfencia_execution_bundle",
    REPO_ROOT / ".github" / "scripts" / "build_correfencia_execution_bundle.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExecutionBundleRequestIdTest(unittest.TestCase):
    def test_accepts_python_resolver_output_without_losing_source_fields(self):
        original_occurrence = {
            "title": "Instrumento Alfa",
            "path": "instruments/alpha.md",
            "identity": "matched_by_title",
            "activation_status": "recognized_not_executed",
        }
        result = {
            "schema_version": 2,
            "source_schema_version": "2.3",
            "request": "Aplique Instrumento Alfa",
            "status": "plan_created_needs_execution_integration",
            "matched_instruments": [original_occurrence],
            "operation_context": {
                "preserved_as_received": True,
                "original_payload": {"future_extension": {"keep": ["every", "field"]}},
            },
            "dry_run": True,
            "write_authorized": False,
            "write_execution_available": False,
        }

        bundle = MODULE.build(result, "req-python-resolver")

        self.assertEqual(bundle["source_plan_key"], "matched_instruments")
        self.assertEqual(bundle["instruments"], [original_occurrence])
        self.assertEqual(bundle["matched_instruments"], [original_occurrence])
        self.assertEqual(bundle["source_schema_version"], "2.3")
        self.assertEqual(bundle["operation_context"], result["operation_context"])
        self.assertEqual(bundle["request"], result["request"])
        self.assertTrue(bundle["dry_run"])
        self.assertFalse(bundle["write_authorized"])
        self.assertFalse(bundle["write_execution_available"])
        self.assertFalse(bundle["execution_performed"])

    def test_explicit_activated_list_takes_precedence_over_legacy_execution_plan(self):
        active = {"title": "Instrumento Beta", "activation": True}
        stale_or_legacy = {"title": "Instrumento Alfa", "activation": True}
        result = {
            "execution_plan": [stale_or_legacy],
            "activated": [active],
            "matches": [stale_or_legacy, active],
        }

        bundle = MODULE.build(result, "req-active-precedence")

        self.assertEqual(bundle["source_plan_key"], "activated")
        self.assertEqual(bundle["instruments"], [active])
        # execution_plan is a consumed legacy input field; full mentions remain in matches.
        self.assertEqual(bundle["matches"], [stale_or_legacy, active])
        self.assertFalse(bundle["execution_performed"])

    def test_python_resolver_ambiguous_matches_remain_traceable_but_are_not_packaged_as_active(self):
        active = {
            "title": "Instrumento Beta", "path": "instruments/beta.md",
            "activation": True, "function_status": "own",
        }
        ambiguous_a = {
            "title": "Instrumento Alfa", "path": "instruments/a.md",
            "activation": False, "function_status": "ambiguous",
            "activation_status": "recognized_ambiguous_not_activated",
        }
        ambiguous_b = {
            "title": "Instrumento Alfa", "path": "instruments/b.md",
            "activation": False, "function_status": "ambiguous",
            "activation_status": "recognized_ambiguous_not_activated",
        }
        result = {
            "matched_instruments": [ambiguous_a, active, ambiguous_b],
            "status": "plan_created_needs_execution_integration",
        }

        bundle = MODULE.build(result, "req-ambiguous-canonical-title")

        self.assertEqual(bundle["source_plan_key"], "matched_instruments")
        self.assertEqual(bundle["instruments"], [active])
        self.assertEqual(bundle["matched_instruments"], [ambiguous_a, active, ambiguous_b])
        self.assertFalse(bundle["execution_performed"])

    def test_source_match_counts_are_distinct_from_packaged_active_occurrences(self):
        active = {"title": "Instrumento Beta", "activation": True}
        inactive = {"title": "Instrumento Alfa", "activation": False}
        ambiguous = {"title": "Instrumento Alfa", "function_status": "ambiguous"}
        result = {
            "matched_occurrences": 3,
            "matched_instruments": [active, inactive, ambiguous],
        }

        bundle = MODULE.build(result, "req-count-consistency")

        self.assertEqual(bundle["matched_occurrences"], 3)
        self.assertEqual(bundle["source_matched_occurrences"], 3)
        self.assertEqual(bundle["packaged_instrument_occurrences"], 1)
        self.assertEqual(bundle["instruments"], [active])
        self.assertEqual(bundle["matched_instruments"], [active, inactive, ambiguous])
        self.assertFalse(bundle["execution_performed"])

    def test_rejects_invalid_source_match_count(self):
        for invalid in (-1, 1.5, "3", True):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    MODULE.build({"matched_occurrences": invalid, "matched_instruments": []},
                                 "req-invalid-count")

    def test_execution_plan_explicitly_inactive_entries_are_filtered(self):
        active = {"title": "Instrumento Beta", "activation": True}
        inactive = {"title": "Instrumento Alfa", "activation": False}
        ambiguous = {"title": "Instrumento Alfa", "function_status": "ambiguous"}
        result = {"execution_plan": [active, inactive, ambiguous]}

        bundle = MODULE.build(result, "req-inactive-execution-plan")

        self.assertEqual(bundle["instruments"], [active])

    def test_accepts_javascript_resolver_output_without_losing_mentions(self):
        active = {
            "instrument_id": "alpha", "title": "Instrumento Alfa",
            "path": "instruments/alpha.md", "start": 12, "end": 27,
            "activation": True, "function_status": "own",
            "exception_scope": None, "match_type": "canonical_title",
        }
        diverse = {
            "instrument_id": "beta", "title": "Instrumento Beta",
            "path": "instruments/beta.md", "start": 40, "end": 55,
            "activation": False, "function_status": "diverse",
            "exception_scope": "local", "match_type": "canonical_title",
        }
        result = {
            "transmitted": True,
            "matches": [active, diverse],
            "activated": [active],
            "multiple_titles": False,
            "traceability": [{"instrument_id": "alpha", "title": "Instrumento Alfa"}],
            "coordinator": {"activation": True, "instrument_id": "coord",
                            "title": "Coordenador fixo", "function_status": "own"},
            "operational_fixed": {"activation": True, "instrument_id": "operational-fixed",
                                  "title": "Componente operacional fixo",
                                  "operations": ["inserir", "recuperar", "aplicar"]},
        }

        bundle = MODULE.build(result, "req-js-resolver")

        self.assertEqual(bundle["source_plan_key"], "activated")
        self.assertEqual(bundle["instruments"], [active])
        self.assertEqual(bundle["matches"], [active, diverse])
        self.assertEqual(bundle["activated"], [active])
        self.assertEqual(bundle["traceability"], result["traceability"])
        self.assertEqual(bundle["coordinator"], result["coordinator"])
        self.assertEqual(bundle["operational_fixed"], result["operational_fixed"])
        self.assertFalse(bundle["execution_performed"])

    def test_repeated_active_occurrences_remain_distinct_and_inactive_mentions_stay_traceable(self):
        first = {
            "instrument_id": "alpha", "title": "Instrumento Alfa",
            "path": "instruments/alpha.md", "start": 0, "end": 15,
            "activation": True, "function_status": "own",
        }
        second = {
            "instrument_id": "alpha", "title": "Instrumento Alfa",
            "path": "instruments/alpha.md", "start": 42, "end": 57,
            "activation": True, "function_status": "own",
        }
        inactive = {
            "instrument_id": "beta", "title": "Instrumento Beta",
            "path": "instruments/beta.md", "start": 20, "end": 35,
            "activation": False, "function_status": "diverse",
        }
        result = {
            "matches": [first, inactive, second],
            "activated": [first, second],
            "coordinator": {"activation": True, "instrument_id": "coord"},
            "operational_fixed": {"activation": True, "instrument_id": "operational-fixed"},
            "execution_performed": True,
        }

        bundle = MODULE.build(result, "req-occurrence-invariants")

        self.assertEqual(bundle["instruments"], [first, second])
        self.assertEqual(bundle["matches"], [first, inactive, second])
        self.assertEqual(bundle["activated"], [first, second])
        self.assertEqual(bundle["coordinator"], result["coordinator"])
        self.assertEqual(bundle["operational_fixed"], result["operational_fixed"])
        self.assertFalse(bundle["execution_performed"])

    def test_request_id_is_preserved_in_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            instrument = Path(tmp) / "Index.html"
            instrument.write_text("<html><body><h1>Instrumento Alfa</h1></body></html>", encoding="utf-8")
            result = {
                "status": "ok", "matched_occurrences": 1,
                "execution_plan": [{"title": "Instrumento Alfa", "instrument": str(instrument), "occurrences": 1, "mode": "preserve_own_function"}],
                "coordination": {"traceability": {"required": True}},
            }
            result["source_schema_version"] = "2.3"
            result["operation_context"] = {
                "preserved_as_received": True,
                "original_payload": {"future_extension": {"keep": ["all", "fields"]}},
            }
            bundle = MODULE.build(result, "req-test-123")
            self.assertEqual(bundle["request_id"], "req-test-123")
            # 2.1 is the execution-bundle schema; the originating request schema
            # remains separate metadata and must survive unchanged.
            self.assertEqual(bundle["schema_version"], "2.1")
            self.assertEqual(bundle["source_schema_version"], "2.3")
            self.assertEqual(
                bundle["operation_context"]["original_payload"],
                {"future_extension": {"keep": ["all", "fields"]}},
            )
            self.assertEqual(len(bundle["instruments"]), 1)


if __name__ == "__main__":
    unittest.main()
