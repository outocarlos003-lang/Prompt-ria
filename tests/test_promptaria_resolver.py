import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVER = REPO_ROOT / "scripts" / "promptaria_resolver.py"


class PromptariaResolverTests(unittest.TestCase):
    def run_resolver(self, request_text, instruments, extra_payload=None, registry_entries=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            instrument_dir = root / "instruments"
            instrument_dir.mkdir()
            for filename, title in instruments:
                (instrument_dir / filename).write_text(f"# {title}\n\nConteúdo de teste.\n", encoding="utf-8")
            if registry_entries is not None:
                config_dir = root / "config"
                config_dir.mkdir()
                (config_dir / "instrument-registry.json").write_text(
                    json.dumps({"schema_version": 2, "instruments": registry_entries}, ensure_ascii=False),
                    encoding="utf-8",
                )
            request_path = root / "request.json"
            output_path = root / "result.json"
            payload = {"request": request_text}
            payload.update(extra_payload or {})
            request_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RESOLVER), "--request", str(request_path),
                 "--instruments", str(instrument_dir), "--output", str(output_path)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            self.assertTrue(output_path.exists())
            return json.loads(output_path.read_text(encoding="utf-8")), completed.stdout

    def test_repository_resolver_ignores_prepared_but_disabled_instruments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            output_path = root / "result.json"
            inactive_title = "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS"
            active_title = "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"
            request_path.write_text(json.dumps({"request": inactive_title + " " + active_title}, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RESOLVER), "--request", str(request_path),
                 "--instruments", str(REPO_ROOT / "instruments"), "--output", str(output_path)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            result = json.loads(output_path.read_text(encoding="utf-8"))
            active_entries = [item for item in result["matched_instruments"] if item.get("title") == active_title]
            self.assertTrue(active_entries)
            self.assertTrue(all(item.get("category") == "continuous_automation" for item in active_entries))
            self.assertFalse(any(item.get("identity") in {"matched_by_title", "matched_by_alias"} for item in active_entries))
            self.assertNotIn(inactive_title, {item["title"] for item in result["matched_instruments"]})
            self.assertIn("github-operational", result["preconfiguration"]["continuous_context_ids"])

    def test_includes_all_three_mandatory_components(self):
        instruments = [
            ("unified-arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md", "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS"),
            ("protocolo-mestre-acionamento-automatico.md", "PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO"),
            ("acione-a-promptaria-pelo-github.md", "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"),
        ]
        result, stdout = self.run_resolver("Demanda genérica de teste.", instruments)
        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(len(result["mandatory_components"]), 3)
        self.assertEqual(result["missing_mandatory_components"], [])
        self.assertEqual(len(result["matched_instruments"]), 3)
        self.assertIn("3/3", stdout)

    def test_registry_loads_github_operational_as_continuous_context_not_recoverable_base(self):
        instruments = [
            ("arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md", "Arquitetura Unificada"),
            ("protocolo-mestre-acionamento-automatico.md", "Protocolo-Mestre"),
            ("acione-a-promptaria-pelo-github.md", "GitHub Operacional"),
        ]
        registry = [
            {"id": "functional-correference-architecture", "title": "Arquitetura Unificada",
             "path": "instruments/arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md", "aliases": ["arquitetura"],
             "activation": {"enabled": True}, "category": "continuous_automation",
             "ui": {"visible": False}},
            {"id": "master-activation", "title": "Protocolo-Mestre",
             "path": "instruments/protocolo-mestre-acionamento-automatico.md", "aliases": ["protocolo"],
             "activation": {"enabled": True}, "category": "continuous_automation",
             "ui": {"visible": False}},
            {"id": "github-operational", "title": "GitHub Operacional",
             "path": "instruments/acione-a-promptaria-pelo-github.md", "aliases": ["github fixo"],
             "activation": {"enabled": True}, "category": "continuous_automation",
             "ui": {"visible": False}},
        ]
        result, _ = self.run_resolver(
            "Demanda genérica sem menção aos componentes-base.",
            instruments,
            registry_entries=registry,
        )
        self.assertEqual(
            {item["id"] for item in result["mandatory_components"]},
            {"functional-correference-architecture", "master-activation", "github-operational"},
            msg=json.dumps(result, ensure_ascii=False, indent=2),
        )
        context = result["preconfiguration"]
        self.assertEqual(
            set(context["continuous_context_ids"]),
            {"functional-correference-architecture", "master-activation", "github-operational"},
        )
        self.assertTrue(all(item["loaded_as_context"] for item in context["continuous_context"]))
        self.assertTrue(all(item["title_resolvable"] is False for item in context["continuous_context"]))
        self.assertTrue(all(item["execution_performed"] is False for item in context["continuous_context"]))
        self.assertEqual(context["fixed_operational_component"]["id"], "github-operational")
        self.assertEqual(context["fixed_operational_component"]["category"], "continuous_automation")
        self.assertTrue(context["complete"])
        self.assertEqual(result["status"], "plan_created_needs_execution_integration")
        self.assertFalse(any(
            item.get("identity") in {"matched_by_title", "matched_by_alias"}
            and item.get("category") == "continuous_automation"
            for item in result["matched_instruments"]
        ))

    def test_disabled_or_divergent_base_component_fails_closed(self):
        instruments = [
            ("arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md", "Arquitetura Unificada"),
            ("protocolo-mestre-acionamento-automatico.md", "Protocolo-Mestre"),
            ("acione-a-promptaria-pelo-github.md", "GitHub Operacional"),
        ]
        base_registry = [
            {"id": "functional-correference-architecture", "title": "Arquitetura Unificada",
             "path": "instruments/arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md", "aliases": ["arquitetura"],
             "activation": {"enabled": True}, "category": "continuous_automation",
             "ui": {"visible": False}},
            {"id": "master-activation", "title": "Protocolo-Mestre",
             "path": "instruments/protocolo-mestre-acionamento-automatico.md", "aliases": ["protocolo"],
             "activation": {"enabled": True}, "category": "continuous_automation",
             "ui": {"visible": False}},
            {"id": "github-operational", "title": "GitHub Operacional",
             "path": "instruments/acione-a-promptaria-pelo-github.md", "aliases": ["github fixo"],
             "activation": {"enabled": True}, "category": "recoverable_on_demand",
             "ui": {"visible": True}},
        ]
        disabled = json.loads(json.dumps(base_registry))
        disabled[1]["activation"]["enabled"] = False
        result, _ = self.run_resolver("Demanda genérica.", instruments, registry_entries=disabled)
        self.assertFalse(result["preconfiguration"]["complete"])
        self.assertEqual(result["status"], "plan_incomplete_missing_preconfiguration_components")
        self.assertTrue(any("master-activation" in item for item in result["missing_mandatory_components"]))

        divergent = json.loads(json.dumps(base_registry))
        divergent[0]["path"] = "instruments/renamed-arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md"
        result, _ = self.run_resolver("Demanda genérica.", instruments, registry_entries=divergent)
        self.assertFalse(result["preconfiguration"]["complete"])
        self.assertTrue(any("functional-correference-architecture" in item for item in result["missing_mandatory_components"]))

    def test_production_registry_preloads_exactly_three_base_components(self):
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "request.json"
            output_path = Path(tmp) / "result.json"
            request_path.write_text(json.dumps({"request": "Demanda genérica de produção."}), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RESOLVER), "--request", str(request_path),
                 "--instruments", str(REPO_ROOT / "instruments"), "--output", str(output_path)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(len(result["mandatory_components"]), 3)
            self.assertEqual(
                {item["id"] for item in result["mandatory_components"]},
                {"functional-correference-architecture", "master-activation", "github-operational"},
            )
            self.assertTrue(result["preconfiguration"]["complete"])
            self.assertTrue(result["preconfiguration"]["continuous_context"])
            self.assertTrue(result["preconfiguration"]["fixed_operational_component"]["content"])
            self.assertEqual(result["preconfiguration"]["fixed_operational_component"]["category"], "continuous_automation")
            self.assertEqual(result["missing_mandatory_components"], [])
            self.assertEqual(result["status"], "plan_created_needs_execution_integration")

    def test_preserves_every_explicit_title_match(self):
        instruments = [
            ("alpha.md", "Instrumento Alfa"),
            ("beta.md", "Instrumento Beta"),
            ("gamma.md", "Instrumento Gama"),
        ]
        result, _ = self.run_resolver("Aplicar Instrumento Alfa e Instrumento Beta e Instrumento Gama.", instruments)
        matched = {item["title"] for item in result["matched_instruments"]}
        self.assertTrue({"Instrumento Alfa", "Instrumento Beta", "Instrumento Gama"}.issubset(matched))

    def test_resolves_explicit_registry_id_and_repository_path(self):
        instruments = [
            ("alpha.md", "Instrumento Alfa"),
            ("beta.md", "Instrumento Beta"),
        ]
        registry = [
            {"id": "alpha-id", "title": "Instrumento Alfa", "path": "instruments/alpha.md",
             "aliases": ["alfa curto"], "activation": {"enabled": True, "status": "active"}},
            {"id": "beta-id", "title": "Instrumento Beta", "path": "instruments/beta.md",
             "aliases": ["beta curto"], "activation": {"enabled": True, "status": "active"}},
        ]
        by_id, _ = self.run_resolver("instrument_id:alpha-id", instruments, registry_entries=registry)
        id_match = next(item for item in by_id["matched_instruments"] if item["identity"] == "matched_by_id")
        self.assertEqual(id_match["id"], "alpha-id")
        self.assertTrue(id_match["activation"])

        by_path, _ = self.run_resolver(
            "instrument_path:instruments/beta.md", instruments, registry_entries=registry
        )
        path_match = next(item for item in by_path["matched_instruments"] if item["identity"] == "matched_by_path")
        self.assertEqual(path_match["repository_path"], "instruments/beta.md")
        self.assertTrue(path_match["activation"])

    def test_structured_request_preserves_explicit_instrument_id_selector(self):
        instruments = [("alpha.md", "Instrumento Alfa")]
        registry = [
            {"id": "alpha-id", "title": "Instrumento Alfa", "path": "instruments/alpha.md",
             "aliases": ["alfa curto"], "activation": {"enabled": True, "status": "active"}},
        ]
        result, _ = self.run_resolver(
            {"operation": "resolve", "instrument_id": "alpha-id"},
            instruments,
            registry_entries=registry,
        )
        explicit = next(item for item in result["matched_instruments"] if item["identity"] == "matched_by_id")
        self.assertEqual(explicit["id"], "alpha-id")
        self.assertTrue(explicit["activation"])

    def test_resolves_unique_enabled_alias_and_never_activates_disabled_entry(self):
        instruments = [
            ("alpha.md", "Instrumento Alfa"),
            ("beta.md", "Instrumento Beta"),
        ]
        registry = [
            {"id": "alpha-id", "title": "Instrumento Alfa", "path": "instruments/alpha.md",
             "aliases": ["alfa curto"], "activation": {"enabled": True, "status": "active"}},
            {"id": "beta-id", "title": "Instrumento Beta", "path": "instruments/beta.md",
             "aliases": ["beta curto"], "activation": {"enabled": False, "status": "prepared"}},
        ]
        result, _ = self.run_resolver("Usar alfa curto.", instruments, registry_entries=registry)
        alias_match = next(item for item in result["matched_instruments"] if item["identity"] == "matched_by_alias")
        self.assertEqual(alias_match["id"], "alpha-id")
        self.assertTrue(alias_match["activation"])

        disabled, _ = self.run_resolver(
            "instrument_id:beta-id", instruments, registry_entries=registry
        )
        disabled_match = next(item for item in disabled["matched_instruments"] if item["identity"] == "matched_by_id")
        self.assertFalse(disabled_match["activation"])
        self.assertEqual(disabled_match["function_status"], "disabled")
        self.assertEqual(disabled_match["activation_status"], "explicit_reference_to_disabled_instrument")

    def test_ambiguous_alias_does_not_activate_any_candidate(self):
        instruments = [
            ("alpha.md", "Instrumento Alfa"),
            ("beta.md", "Instrumento Beta"),
        ]
        registry = [
            {"id": "alpha-id", "title": "Instrumento Alfa", "path": "instruments/alpha.md",
             "aliases": ["nome compartilhado"], "activation": {"enabled": True, "status": "active"}},
            {"id": "beta-id", "title": "Instrumento Beta", "path": "instruments/beta.md",
             "aliases": ["nome compartilhado"], "activation": {"enabled": True, "status": "active"}},
        ]
        result, _ = self.run_resolver("Executar nome compartilhado.", instruments, registry_entries=registry)
        ambiguous = [item for item in result["matched_instruments"] if item["function_status"] == "ambiguous"]
        self.assertEqual({item["id"] for item in ambiguous}, {"alpha-id", "beta-id"})
        self.assertTrue(all(not item["activation"] for item in ambiguous))

    def test_unknown_explicit_id_is_not_guessed_from_title(self):
        instruments = [("alpha.md", "Instrumento Alfa")]
        registry = [
            {"id": "alpha-id", "title": "Instrumento Alfa", "path": "instruments/alpha.md",
             "aliases": [], "activation": {"enabled": True, "status": "active"}},
        ]
        result, _ = self.run_resolver(
            "instrument_id:missing-id Instrumento Alfa", instruments, registry_entries=registry
        )
        unresolved = next(item for item in result["matched_instruments"] if item["identity"] == "unresolved_explicit_id")
        self.assertFalse(unresolved["activation"])
        self.assertEqual(unresolved["activation_status"], "explicit_reference_not_found")
        title_match = next(item for item in result["matched_instruments"] if item["identity"] == "matched_by_title")
        self.assertTrue(title_match["activation"])

    def test_reports_missing_mandatory_components_without_crashing(self):
        result, stdout = self.run_resolver("Pedido de teste.", [("one.md", "Instrumento Único")])
        self.assertEqual(len(result["missing_mandatory_components"]), 3)
        self.assertEqual(result["mandatory_components"], [])
        self.assertIn("0/3", stdout)

    def test_rejects_windows_and_parent_traversal_destinations(self):
        instruments = [("one.md", "Instrumento Único")]
        for destination in ("../outside.txt", "folder/../outside.txt", r"folder\outside.txt", ".git/config", "/tmp/out.txt", "C:/outside.txt"):
            with self.subTest(destination=destination):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    instrument_dir = root / "instruments"
                    instrument_dir.mkdir()
                    (instrument_dir / "one.md").write_text("# Instrumento Único\n", encoding="utf-8")
                    request_path = root / "request.json"
                    request_path.write_text(json.dumps({"request": "teste", "destination": destination}), encoding="utf-8")
                    completed = subprocess.run(
                        [sys.executable, str(RESOLVER), "--request", str(request_path),
                         "--instruments", str(instrument_dir), "--output", str(root / "result.json")],
                        capture_output=True, text=True, encoding="utf-8", check=False,
                    )
                    self.assertNotEqual(completed.returncode, 0, msg=destination)

    def test_rejects_non_boolean_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            instrument_dir = root / "instruments"
            instrument_dir.mkdir()
            (instrument_dir / "one.md").write_text("# Instrumento Único\n", encoding="utf-8")
            request_path = root / "request.json"
            request_path.write_text(json.dumps({"request": "teste", "dry_run": "false"}), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RESOLVER), "--request", str(request_path),
                 "--instruments", str(instrument_dir), "--output", str(root / "result.json")],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("dry_run inválido", completed.stderr.lower())

    def test_non_dry_run_requires_explicit_authorization_and_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            instrument_dir = root / "instruments"
            instrument_dir.mkdir()
            (instrument_dir / "one.md").write_text("# Instrumento Único\n", encoding="utf-8")
            request_path = root / "request.json"
            request_path.write_text(json.dumps({"request": "teste", "dry_run": False}), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RESOLVER), "--request", str(request_path),
                 "--instruments", str(instrument_dir), "--output", str(root / "result.json")],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("execução recusada", completed.stderr.lower())

    def test_accepts_structured_schema_request_and_preserves_operation_context(self):
        instruments = [
            ("unified-arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md", "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS"),
            ("protocolo-mestre-acionamento-automatico.md", "PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO"),
            ("acione-a-promptaria-pelo-github.md", "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"),
            ("alpha.md", "Instrumento Alfa"),
        ]
        structured = {
            "schema_version": "2.3",
            "operation": "incorporar Instrumento Alfa",
            "demand": "Preservar o conteúdo integral de Instrumento Alfa",
            "source": {"repository": "example/repo", "preserved": True},
            "transformation": ["integrar Instrumento Alfa"],
            "destinations": ["instruments/alpha.md"],
            "validation": {"result": "pending"},
            "production_chain": ["recepção", "validação"],
            "navigation_invariants": ["sem órfãos"],
            "status": "planejado",
        }
        result, _ = self.run_resolver(json.dumps(structured, ensure_ascii=False), instruments)
        self.assertEqual(result["source_schema_version"], "2.3")
        self.assertTrue(result["operation_context"]["preserved_as_received"])
        self.assertEqual(result["operation_context"]["source"], structured["source"])
        self.assertEqual(result["operation_context"]["transformation"], structured["transformation"])
        self.assertTrue(result["operation_context"]["review_required_before_mutation"])
        self.assertIn("Instrumento Alfa", {item["title"] for item in result["matched_instruments"]})
        self.assertEqual(result["operation_context"]["original_payload"], structured)

        # Unknown nested fields are part of the source contract and must survive.
        structured["future_extension"] = {
            "opaque": True,
            "nested": {"revision": 4, "notes": ["keep", "all"]},
        }
        result, _ = self.run_resolver(json.dumps(structured, ensure_ascii=False), instruments)
        self.assertEqual(result["operation_context"]["original_payload"], structured)
        self.assertEqual(
            result["operation_context"]["original_payload"]["future_extension"],
            structured["future_extension"],
        )
        self.assertIn("\n", result["request"])

        # The same schema may arrive as a native object, not only encoded JSON.
        direct_result, _ = self.run_resolver(structured, instruments)
        self.assertEqual(direct_result["source_schema_version"], "2.3")
        self.assertEqual(direct_result["operation_context"]["original_payload"], structured)
        self.assertEqual(
            direct_result["operation_context"]["original_payload"]["future_extension"],
            structured["future_extension"],
        )

    def test_python_resolver_matches_javascript_accent_hyphen_and_repeated_mentions(self):
        instruments = [("alpha.md", "Ação-Útil")]
        result, _ = self.run_resolver("Aplicar acao util e AÇÃO-ÚTIL.", instruments)
        occurrences = [item for item in result["matched_instruments"] if item["title"] == "Ação-Útil"]
        self.assertEqual(len(occurrences), 2)
        self.assertTrue(all(item["activation"] for item in occurrences))
        self.assertEqual([item["function_status"] for item in occurrences], ["own", "own"])

    def test_functional_exception_is_scoped_to_its_own_occurrence(self):
        instruments = [
            ("alpha.md", "Instrumento Alfa"),
            ("beta.md", "Instrumento Beta"),
        ]
        request = (
            "Instrumento Alfa deve atuar como uma função diferente, "
            "enquanto Instrumento Beta deve preservar sua função."
        )
        result, _ = self.run_resolver(request, instruments)
        alpha = next(item for item in result["matched_instruments"] if item["title"] == "Instrumento Alfa")
        beta = next(item for item in result["matched_instruments"] if item["title"] == "Instrumento Beta")
        self.assertFalse(alpha["activation"])
        self.assertEqual(alpha["function_status"], "diverse")
        self.assertEqual(alpha["exception_status"], "local")
        self.assertTrue(beta["activation"])
        self.assertEqual(beta["function_status"], "own")

    def test_repeated_title_mentions_keep_independent_exception_decisions(self):
        instruments = [("alpha.md", "Instrumento Alfa")]
        request = (
            "Instrumento Alfa deve atuar como uma função diferente. "
            "Depois, Instrumento Alfa deve preservar sua função própria."
        )
        result, _ = self.run_resolver(request, instruments)
        occurrences = [item for item in result["matched_instruments"] if item["title"] == "Instrumento Alfa"]
        self.assertEqual(len(occurrences), 2)
        self.assertFalse(occurrences[0]["activation"])
        self.assertTrue(occurrences[1]["activation"])

    def test_shared_cross_runtime_parity_fixture(self):
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "correference-parity.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        instrument_files = [(f"{item['id']}.md", item["title"]) for item in fixture["instruments"]]
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                catalog = case.get("instruments", fixture["instruments"])
                instrument_files = [(f"{item['id']}.md", item["title"]) for item in catalog]
                result, _ = self.run_resolver(case["request"], instrument_files)
                actual = [
                    {
                        "title": item["title"],
                        "activation": item["activation"],
                        "function_status": item["function_status"],
                    }
                    for item in result["matched_instruments"]
                ]
                self.assertEqual(actual, case["expected"])

    def test_rejects_empty_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            request_path.write_text(json.dumps({"request": "   "}), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RESOLVER), "--request", str(request_path),
                 "--instruments", str(root / "instruments"), "--output", str(root / "result.json")],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("demanda vazia", completed.stderr.lower())


if __name__ == "__main__":
    unittest.main()
