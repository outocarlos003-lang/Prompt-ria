import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "scripts" / "promptaria_route_request.py"
REGISTRY = ROOT / "config" / "instrument-registry.json"


class PromptariaRequestRoutingTests(unittest.TestCase):
    def classify(self, request):
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "request.json"
            output_path = Path(tmp) / "routing.json"
            request_path.write_text(json.dumps({"request": request}, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ROUTER), "--request", str(request_path),
                 "--registry", str(REGISTRY), "--output", str(output_path)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            return json.loads(output_path.read_text(encoding="utf-8"))

    def test_explicit_enabled_title_routes_to_coreference(self):
        result = self.classify("Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas.")
        self.assertEqual(result["route"], "title_coreference")
        self.assertIn("github-operational", result["allowed_coreference_ids"])

    def test_automation_preconfiguration_does_not_trigger_coreference(self):
        result = self.classify(
            "Implemente uma atualização de workflow para sincronização e pré-configuração de automação funcional."
        )
        self.assertEqual(result["route"], "automation_preconfiguration")
        self.assertEqual(result["active_title_matches"], [])
        self.assertEqual(result["next_action"], "emit_automation_preconfiguration_plan_only")
        self.assertFalse(result["execution_performed"])

    def test_inactive_title_does_not_become_a_coreference_target(self):
        result = self.classify(
            "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS"
        )
        self.assertEqual(result["route"], "inactive_or_unregistered_reference")
        self.assertEqual(result["active_title_matches"], [])
        self.assertEqual(result["inactive_title_matches"][0]["id"], "coordinator")
        self.assertNotIn("coordinator", result["allowed_coreference_ids"])

    def test_explicit_active_title_plus_automation_intent_routes_as_mixed(self):
        result = self.classify(
            "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas e pré-configure o workflow."
        )
        self.assertEqual(result["route"], "mixed_coreference_and_automation_preconfiguration")
        self.assertIn("github-operational", result["allowed_coreference_ids"])

    def test_unclassified_request_fails_closed(self):
        result = self.classify("Analise isso.")
        self.assertEqual(result["route"], "unclassified_requires_review")
        self.assertEqual(result["allowed_coreference_ids"], [])


if __name__ == "__main__":
    unittest.main()
