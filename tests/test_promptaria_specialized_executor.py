import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_specialized_executor as specialized


class SpecializedExecutorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "tests" / "manifest.json").read_text(encoding="utf-8"))

    def execute_with_all_instruments_activated(self, payload, preflight=None):
        original_read_object = specialized.read_object
        registry_path = specialized.ROOT / "config" / "instrument-registry.json"

        def activated_registry(path):
            value = original_read_object(path)
            if path == registry_path:
                for item in value["instruments"]:
                    item["activation"] = {"enabled": True, "status": "active"}
            return value

        with patch.object(specialized, "read_object", side_effect=activated_registry):
            return specialized.execute(payload, preflight=preflight)

    def test_every_manifest_instrument_has_a_dedicated_handler_and_map_entry(self):
        catalog, mapped = specialized.load_catalog()
        self.assertEqual(set(catalog), set(mapped))
        implemented = {instrument_id for instrument_id, item in mapped.items() if item.get("specialized_execution_status") == "implemented"}
        planning_only = {instrument_id for instrument_id, item in mapped.items() if item.get("specialized_execution_status") == "planning_only"}
        self.assertEqual(implemented, set(specialized.HANDLERS))
        self.assertEqual(planning_only, set())
        for instrument_id, item in mapped.items():
            with self.subTest(instrument=instrument_id):
                self.assertEqual(item["specialized_executor"], "scripts/promptaria_specialized_executor.py")
                self.assertIn(item["specialized_execution_status"], {"implemented", "planning_only"})
                if item["specialized_execution_status"] == "planning_only":
                    self.assertFalse(item.get("specialized_handler"))
                else:
                    self.assertEqual(item["specialized_handler"], specialized.HANDLERS[instrument_id].__name__)

    def test_all_registered_handlers_execute_and_emit_source_evidence(self):
        ids = ["nocturna-arquitetura-necessidade-identidade-sistemica"]
        result = self.execute_with_all_instruments_activated({"request": "Validar a execução especializada.", "instrument_ids": ids})
        self.assertEqual(result["execution_status"], "completed")
        self.assertEqual(result["specialized_execution_count"], len(ids))
        self.assertFalse(result["external_side_effects_performed"])
        self.assertEqual({item["instrument_id"] for item in result["results"]}, set(ids))
        for item in result["results"]:
            with self.subTest(instrument=item["instrument_id"]):
                source_path = ROOT / item["source_path"]
                source_bytes = source_path.read_bytes()
                expected_hash = hashlib.sha256(source_bytes).hexdigest()
                self.assertEqual(item["execution_status"], "completed")
                self.assertEqual(item["source_sha256"], expected_hash)
                self.assertEqual(len(item["source_sha256"]), 64)
                self.assertEqual(item["side_effects"], [])
                self.assertTrue(item["result"]["handler"])
                if "source_sha256" in item["result"]:
                    self.assertEqual(item["result"]["source_sha256"], expected_hash)

    def test_duplicate_manifest_id_fails_closed(self):
        original_read_object = specialized.read_object

        def duplicated_manifest(path):
            value = original_read_object(path)
            if path == specialized.MANIFEST_PATH:
                value["instruments"].append(dict(value["instruments"][0]))
            return value

        with patch.object(specialized, "read_object", side_effect=duplicated_manifest):
            with self.assertRaisesRegex(SystemExit, "ID duplicado em tests/manifest.json"):
                specialized.load_catalog()

    def test_duplicate_execution_map_id_fails_closed(self):
        original_read_object = specialized.read_object

        def duplicated_map(path):
            value = original_read_object(path)
            if path == specialized.MAP_PATH:
                value["instruments"].append(dict(value["instruments"][0]))
            return value

        with patch.object(specialized, "read_object", side_effect=duplicated_map):
            with self.assertRaisesRegex(SystemExit, "ID duplicado em config/instrument-execution-map.json"):
                specialized.load_catalog()

    def test_duplicate_registry_id_fails_closed_during_resolution(self):
        canonical, _ = specialized.load_catalog()
        original_read_object = specialized.read_object

        def duplicated_registry(path):
            value = original_read_object(path)
            if path == specialized.ROOT / "config" / "instrument-registry.json":
                value["instruments"].append(dict(value["instruments"][0]))
            return value

        with patch.object(specialized, "read_object", side_effect=duplicated_registry):
            with self.assertRaisesRegex(SystemExit, "ID duplicado em config/instrument-registry.json"):
                specialized.resolve_ids("github operational", canonical)

    def test_registered_alias_resolves_but_partial_alias_does_not(self):
        canonical, _ = specialized.load_catalog()
        alias_matches = specialized.resolve_ids("Aplicar Nocturna agora.", canonical)
        self.assertEqual(
            [item["id"] for item in alias_matches if item["activation"]],
            ["nocturna-arquitetura-necessidade-identidade-sistemica"],
        )
        partial_matches = specialized.resolve_ids("reconstrução recursiva", canonical)
        embedded_matches = specialized.resolve_ids("xNocturnaY", canonical)
        self.assertEqual(partial_matches, [])
        self.assertEqual(embedded_matches, [])

    def test_duplicate_registered_alias_fails_closed(self):
        canonical = {
            "alpha": {"id": "alpha", "title": "Instrumento Alfa", "path": "instruments/alpha.md"},
            "beta": {"id": "beta", "title": "Instrumento Beta", "path": "instruments/beta.md"},
        }
        original_read_object = specialized.read_object

        def duplicated_aliases(path):
            value = original_read_object(path)
            if path == specialized.ROOT / "config" / "instrument-registry.json":
                value["instruments"] = [
                    {"id": "alpha", "title": "Instrumento Alfa", "path": "instruments/alpha.md",
                     "aliases": ["github operacional"], "activation": {"enabled": True},
                     "ui": {"visible": True}, "category": "recoverable_on_demand"},
                    {"id": "beta", "title": "Instrumento Beta", "path": "instruments/beta.md",
                     "aliases": ["github operacional"], "activation": {"enabled": True},
                     "ui": {"visible": True}, "category": "recoverable_on_demand"},
                ]
            return value

        with patch.object(specialized, "read_object", side_effect=duplicated_aliases):
            matches = specialized.resolve_ids("github operacional", canonical)

        self.assertEqual({item["id"] for item in matches}, {"alpha", "beta"})
        self.assertEqual(
            {item["identity_status"] for item in matches},
            {"ambiguous_registered_term_collision"},
        )
        self.assertFalse(any(item["activation"] for item in matches))

    def test_longer_title_does_not_select_embedded_short_title(self):
        canonical = {
            "alpha": {"id": "alpha", "title": "Arquitetura Unificada", "path": "instruments/alpha.md"},
            "beta": {"id": "beta", "title": "Arquitetura Unificada de Execução Semântica", "path": "instruments/beta.md"},
        }
        original_read_object = specialized.read_object

        def registry_with_nested_titles(path):
            value = original_read_object(path)
            if path == specialized.ROOT / "config" / "instrument-registry.json":
                value["instruments"] = [
                    {"id": "alpha", "title": canonical["alpha"]["title"], "path": canonical["alpha"]["path"],
                     "aliases": [], "activation": {"enabled": True}, "ui": {"visible": True}, "category": "recoverable_on_demand"},
                    {"id": "beta", "title": canonical["beta"]["title"], "path": canonical["beta"]["path"],
                     "aliases": [], "activation": {"enabled": True}, "ui": {"visible": True}, "category": "recoverable_on_demand"},
                ]
            return value

        with patch.object(specialized, "read_object", side_effect=registry_with_nested_titles):
            only_long = specialized.resolve_ids(canonical["beta"]["title"], canonical)
            both = specialized.resolve_ids(
                canonical["alpha"]["title"] + "; " + canonical["beta"]["title"], canonical
            )

        self.assertEqual([item["id"] for item in only_long], ["beta"])
        self.assertEqual({item["id"] for item in both}, {"alpha", "beta"})

    def test_continuous_github_title_is_context_only_not_resolvable(self):
        canonical, _ = specialized.load_catalog()
        title = canonical["github-operational"]["title"]
        self.assertEqual(specialized.resolve_ids(title, canonical), [])
        with self.assertRaisesRegex(SystemExit, "Nenhum instrumento resolvido"):
            specialized.execute({"request": title})

    def test_explicit_recoverable_id_or_path_resolves_shared_title(self):
        canonical, _ = specialized.load_catalog()
        item = canonical["github-operational-demand"]
        title = canonical["github-operational"]["title"]

        by_id = specialized.resolve_ids(f"{title}; {item['id']}", canonical)
        by_path = specialized.resolve_ids(f"{title}; {item['path']}", canonical)

        self.assertEqual([match["id"] for match in by_id], ["github-operational-demand"])
        self.assertTrue(by_id[0]["activation"])
        self.assertEqual([match["id"] for match in by_path], ["github-operational-demand"])
        self.assertTrue(by_path[0]["activation"])

    def test_explicit_continuous_github_id_cannot_activate_specialized_handler(self):
        with self.assertRaisesRegex(SystemExit, "Instrumentos não ativados no registro"):
            specialized.execute({"request": "demanda", "instrument_ids": ["github-operational"]})

    def test_explicit_id_disambiguates_only_recoverable_instrument(self):
        with self.assertRaisesRegex(SystemExit, "Instrumentos não ativados no registro"):
            specialized.execute({
                "request": "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas",
                "instrument_ids": ["github-operational"],
            })

    def test_unknown_id_is_rejected(self):
        with self.assertRaisesRegex(SystemExit, "IDs de instrumento desconhecidos"):
            specialized.execute({"request": "do work", "instrument_ids": ["not-a-real-instrument"]})

    def test_hash_uses_exact_source_bytes_including_crlf(self):
        instrument_id = "nocturna-arquitetura-necessidade-identidade-sistemica"
        catalog, _ = specialized.load_catalog()
        source_path = ROOT / catalog[instrument_id]["path"]
        original_read_bytes = Path.read_bytes
        exact_bytes = (
            ("# " + catalog[instrument_id]["title"] + "\r\nConteúdo de teste com finais de linha CRLF.\r\n").encode("utf-8")
        )

        def read_bytes_with_crlf(path):
            if path == source_path:
                return exact_bytes
            return original_read_bytes(path)

        with patch.object(Path, "read_bytes", read_bytes_with_crlf):
            result = specialized.execute({
                "request": "Verificar hash dos bytes exatos.",
                "instrument_ids": [instrument_id],
            })

        expected_hash = hashlib.sha256(exact_bytes).hexdigest()
        self.assertEqual(result["results"][0]["source_sha256"], expected_hash)
        self.assertEqual(
            result["results"][0]["result"]["source_sha256"],
            expected_hash,
        )


    def test_manifest_title_mismatch_with_other_catalogs_fails_closed(self):
        original_read_object = specialized.read_object

        def altered_manifest(path):
            value = original_read_object(path)
            if path == specialized.MANIFEST_PATH:
                value["instruments"][0]["title"] = "Título alterado apenas no manifesto"
            return value

        with patch.object(specialized, "read_object", side_effect=altered_manifest):
            with self.assertRaisesRegex(SystemExit, "Identidade divergente entre catálogos.*title"):
                specialized.load_catalog()

    def test_manifest_path_escape_fails_closed(self):
        original_read_object = specialized.read_object
        target_id = "nocturna-arquitetura-necessidade-identidade-sistemica"

        def altered_manifest(path):
            value = original_read_object(path)
            if path in (specialized.MANIFEST_PATH, specialized.ROOT / "config" / "instrument-registry.json", specialized.MAP_PATH):
                for item in value["instruments"]:
                    if item.get("id") == target_id:
                        item["path"] = "../outside.md"
            return value

        with patch.object(specialized, "read_object", side_effect=altered_manifest):
            with self.assertRaisesRegex(SystemExit, "Caminho de fonte escapa do repositório"):
                specialized.execute({
                    "request": "Verificar contenção do caminho.",
                    "instrument_ids": [target_id],
                })


    def test_future_demand_handler_preserves_unknown_structured_fields(self):
        structured = {
            "request_id": "req-custom-17",
            "operation": "validate",
            "demand": "Preservar os campos.",
            "custom_future_field": {"nested": [1, 2, 3]},
        }
        with self.assertRaisesRegex(SystemExit, "Instrumentos não ativados no registro"):
            self.execute_with_all_instruments_activated({
                "request": structured,
                "instrument_ids": ["future-demand-preconfiguration"],
            })

    def test_catalog_handler_is_read_only_and_reports_legacy_tree_state(self):
        with self.assertRaisesRegex(SystemExit, "Instrumentos não ativados no registro"):
            self.execute_with_all_instruments_activated({
                "request": "Auditar catálogo e navegação.",
                "instrument_ids": ["catalog-sitemap-preconfiguration"],
            })

    def test_output_path_guard_blocks_source_and_input_overwrites(self):
        source = ROOT / self.manifest["instruments"][0]["path"]
        with self.assertRaisesRegex(SystemExit, "artifacts/"):
            specialized.validate_output_path(source, [])
        with self.assertRaisesRegex(SystemExit, "não pode sobrescrever uma entrada"):
            specialized.validate_output_path(Path("request.json"), [Path("request.json")])
        self.assertEqual(
            specialized.validate_output_path(ROOT / "artifacts" / "result.json", []),
            ROOT / "artifacts" / "result.json",
        )

    def test_output_path_guard_blocks_symlink_aliases_to_inputs_and_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = root / "request.json"
            request.write_text('{"request": "safe"}', encoding="utf-8")
            request_alias = root / "request-alias.json"
            request_alias.symlink_to(request)
            with self.assertRaisesRegex(SystemExit, "não pode sobrescrever uma entrada"):
                specialized.validate_output_path(request_alias, [request])

        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            artifacts = Path(directory) / "artifacts"
            artifacts.mkdir()
            source = ROOT / self.manifest["instruments"][0]["path"]
            source_alias = artifacts / "source-alias.json"
            source_alias.symlink_to(source)
            with self.assertRaisesRegex(SystemExit, "artifacts/"):
                specialized.validate_output_path(source_alias, [])


    def test_preflight_with_mismatched_request_is_rejected(self):
        preflight = {
            "request": "Demanda diferente",
            "matched_instruments": [{
                "id": "master-execution", "identity_status": "resolved", "activation": True
            }],
        }
        with self.assertRaisesRegex(SystemExit, "Pré-validação recusada: a demanda não corresponde"):
            specialized.execute({"request": "Execute checklist."}, preflight=preflight)

    def test_preflight_cannot_inject_a_different_active_instrument(self):
        canonical, _ = specialized.load_catalog()
        request = canonical["nocturna-arquitetura-necessidade-identidade-sistemica"]["title"]
        preflight = {
            "request": request,
            "matched_instruments": [{
                "id": "protocol-update-integrity", "identity_status": "resolved", "activation": True
            }],
        }
        result = specialized.execute({"request": request}, preflight=preflight)
        self.assertIn("nocturna-arquitetura-necessidade-identidade-sistemica", result["selected_instrument_ids"])
        self.assertNotIn("protocol-update-integrity", result["selected_instrument_ids"])

    def test_recoverable_unified_architecture_executes_dedicated_handler(self):
        canonical, mapped = specialized.load_catalog()
        item_id = "functional-correference-architecture-recoverable"
        title = canonical[item_id]["title"]
        payload = {
            "request": title,
            "request_id": "req-architecture-01",
            "origin": "repo/source",
            "destination": "repo/output",
            "parameters": {"mode": "validate", "preserve": True},
        }
        result = specialized.execute(payload)
        self.assertIn(item_id, result["selected_instrument_ids"])
        execution = next(item for item in result["results"] if item["instrument_id"] == item_id)
        self.assertEqual(execution["handler"], "handler_recoverable_unified_architecture")
        detail = execution["result"]
        self.assertEqual(detail["result"], "recoverable_architecture_coordinated")
        self.assertTrue(detail["source_integrity"]["full_source_recovered"])
        self.assertTrue(detail["validation"]["all_selected_sources_recovered"])
        self.assertEqual(detail["application_context"]["origin"], "repo/source")
        self.assertEqual(detail["application_context"]["destination"], "repo/output")
        self.assertEqual(detail["application_context"]["parameters"], payload["parameters"])
        self.assertFalse(detail["execution_boundary"]["external_side_effects_performed"])
        self.assertFalse(detail["execution_boundary"]["title_alone_authorizes_external_side_effects"])
        self.assertEqual(mapped[item_id]["specialized_execution_status"], "implemented")

    def test_recoverable_architecture_rejects_non_object_parameters(self):
        with self.assertRaisesRegex(SystemExit, "parameters.*objeto JSON"):
            specialized.execute({
                "request": "functional-correference-architecture-recoverable",
                "parameters": ["not", "an", "object"],
            })

    def test_shared_title_resolves_recoverable_phase_not_continuous_phase(self):
        canonical, _ = specialized.load_catalog()
        shared_title = canonical["functional-correference-architecture-recoverable"]["title"]
        matches = specialized.resolve_ids(shared_title, canonical)
        self.assertEqual([item["id"] for item in matches if item["activation"]], [
            "functional-correference-architecture-recoverable"
        ])
        self.assertEqual(specialized.resolve_ids(
            "functional-correference-architecture", canonical
        ), [])

    def test_continuous_automation_instrument_is_context_only_not_executable(self):
        with self.assertRaisesRegex(SystemExit, "Instrumentos não ativados no registro"):
            specialized.execute({
                "request": "Executar coordenador.",
                "instrument_ids": ["coordinator"],
            })


    def test_legacy_coordinator_id_cannot_activate_continuous_context(self):
        with self.assertRaisesRegex(SystemExit, "Instrumentos não ativados no registro"):
            self.execute_with_all_instruments_activated({
                "request": "Acionar a arquitetura coordenadora legada.",
                "instrument_ids": ["coordinator"],
            })
        with self.assertRaisesRegex(SystemExit, "Nenhum instrumento resolvido"):
            self.execute_with_all_instruments_activated({
                "request": "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS",
            })


if __name__ == "__main__":
    unittest.main()
