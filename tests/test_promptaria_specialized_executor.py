import hashlib
import json
import sys
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
        self.assertEqual(set(catalog), set(specialized.HANDLERS))
        self.assertEqual(set(mapped), set(specialized.HANDLERS))
        for instrument_id, item in mapped.items():
            with self.subTest(instrument=instrument_id):
                self.assertEqual(item["specialized_executor"], "scripts/promptaria_specialized_executor.py")
                self.assertEqual(item["specialized_execution_status"], "implemented")

    def test_all_registered_handlers_execute_and_emit_source_evidence(self):
        ids = [item["id"] for item in self.manifest["instruments"]]
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
        canonical, _ = specialized.load_catalog()
        original_read_object = specialized.read_object

        def duplicated_aliases(path):
            value = original_read_object(path)
            if path == specialized.ROOT / "config" / "instrument-registry.json":
                first = next(item for item in value["instruments"] if item["id"] == "github-operational")
                second = next(item for item in value["instruments"] if item["id"] == "nocturna-arquitetura-necessidade-identidade-sistemica")
                first["aliases"] = list(first.get("aliases", [])) + ["github operacional"]
                second["aliases"] = list(second.get("aliases", [])) + ["github operacional"]
            return value

        with patch.object(specialized, "read_object", side_effect=duplicated_aliases):
            matches = specialized.resolve_ids("github operacional", canonical)
            embedded_id_matches = specialized.resolve_ids("github operacional github-operationalx", canonical)

        self.assertEqual(
            {item["identity_status"] for item in embedded_id_matches},
            {"ambiguous_registered_term_collision"},
        )
        active = {item["id"]: item for item in matches}
        self.assertFalse(active["github-operational"]["activation"])
        self.assertFalse(active["nocturna-arquitetura-necessidade-identidade-sistemica"]["activation"])
        self.assertEqual(
            {item["identity_status"] for item in matches},
            {"ambiguous_registered_term_collision"},
        )

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
                     "aliases": [], "activation": {"enabled": True}},
                    {"id": "beta", "title": canonical["beta"]["title"], "path": canonical["beta"]["path"],
                     "aliases": [], "activation": {"enabled": True}},
                ]
            return value

        with patch.object(specialized, "read_object", side_effect=registry_with_nested_titles):
            only_long = specialized.resolve_ids(canonical["beta"]["title"], canonical)
            both = specialized.resolve_ids(
                canonical["alpha"]["title"] + "; " + canonical["beta"]["title"], canonical
            )

        self.assertEqual([item["id"] for item in only_long], ["beta"])
        self.assertEqual({item["id"] for item in both}, {"alpha", "beta"})

    def test_title_resolution_only_activates_registered_instruments(self):
        canonical, _ = specialized.load_catalog()
        title = canonical["github-operational"]["title"]
        matches = specialized.resolve_ids(title, canonical)
        self.assertEqual({item["id"] for item in matches}, {"github-operational"})
        self.assertTrue(all(item["activation"] for item in matches))
        result = specialized.execute({"request": title})
        self.assertEqual(result["selected_instrument_ids"], ["github-operational"])

    def test_explicit_id_disambiguates_colliding_title(self):
        canonical, _ = specialized.load_catalog()
        title = canonical["github-operational"]["title"]
        result = specialized.execute({"request": title, "instrument_ids": ["github-operational"]})
        self.assertEqual(result["selected_instrument_ids"], ["github-operational"])
        self.assertEqual(result["results"][0]["result"]["handler"], "recover-and-verify-source")
        self.assertEqual(result["results"][0]["result"]["canonical_identity"]["instrument_id"], "github-operational")
        self.assertIn("demand_envelope", result["results"][0]["result"])
        self.assertEqual(result["results"][0]["result"]["demand_envelope"]["goal"], title)

    def test_unknown_id_is_rejected(self):
        with self.assertRaisesRegex(SystemExit, "IDs de instrumento desconhecidos"):
            specialized.execute({"request": "do work", "instrument_ids": ["not-a-real-instrument"]})

    def test_hash_uses_exact_source_bytes_including_crlf(self):
        instrument_id = "github-operational"
        catalog, _ = specialized.load_catalog()
        source_path = ROOT / catalog[instrument_id]["path"]
        original_read_bytes = Path.read_bytes
        exact_bytes = (
            b"# Acione a Prompt\xc3\xa1ria pelo GitHub para Inserir, Recuperar e Aplicar Demandas\r\n"
            b"Conte\xc3\xbado de teste com finais de linha CRLF.\r\n"
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
            result["results"][0]["result"]["integrity"]["sha256"],
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

        def altered_manifest(path):
            value = original_read_object(path)
            if path == specialized.MANIFEST_PATH:
                value["instruments"][0]["path"] = "../outside.md"
            elif path == specialized.ROOT / "config" / "instrument-registry.json":
                value["instruments"][0]["path"] = "../outside.md"
            elif path == specialized.MAP_PATH:
                value["instruments"][0]["path"] = "../outside.md"
            return value

        with patch.object(specialized, "read_object", side_effect=altered_manifest):
            with self.assertRaisesRegex(SystemExit, "Caminho de fonte escapa do repositório"):
                specialized.execute({
                    "request": "Verificar contenção do caminho.",
                    "instrument_ids": [self.manifest["instruments"][0]["id"]],
                })

    def test_future_demand_handler_preserves_unknown_structured_fields(self):
        structured = {
            "request_id": "req-custom-17",
            "operation": "validate",
            "demand": "Preservar os campos.",
            "custom_future_field": {"nested": [1, 2, 3]},
        }
        result = self.execute_with_all_instruments_activated({
            "request": structured,
            "instrument_ids": ["future-demand-preconfiguration"],
        })
        package = result["results"][0]["result"]
        self.assertEqual(package["request_id"], "req-custom-17")
        self.assertEqual(package["operation_context"]["custom_future_field"], {"nested": [1, 2, 3]})

    def test_catalog_handler_is_read_only_and_reports_legacy_tree_state(self):
        result = self.execute_with_all_instruments_activated({
            "request": "Auditar catálogo e navegação.",
            "instrument_ids": ["catalog-sitemap-preconfiguration"],
        })
        details = result["results"][0]["result"]
        self.assertEqual(details["canonical_source"], "tests/manifest.json + instruments/*.md")
        self.assertEqual(details["mutations_performed"], [])
        self.assertIn("legacy_tree_available", details)

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
        request = "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"
        preflight = {
            "request": request,
            "matched_instruments": [{
                "id": "protocol-update-integrity", "identity_status": "resolved", "activation": True
            }],
        }
        result = specialized.execute({"request": request}, preflight=preflight)
        self.assertIn("github-operational", result["selected_instrument_ids"])
        self.assertNotIn("protocol-update-integrity", result["selected_instrument_ids"])

    def test_explicit_id_cannot_bypass_registry_activation(self):
        with self.assertRaisesRegex(SystemExit, "Instrumentos não ativados no registro: coordinator"):
            specialized.execute({"request": "Executar coordenador.", "instrument_ids": ["coordinator"]})


if __name__ == "__main__":
    unittest.main()
