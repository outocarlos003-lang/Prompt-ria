import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "promptaria_preflight.py"
MANIFEST = ROOT / "tests" / "manifest.json"
EXECUTION_MAP = ROOT / "config" / "instrument-execution-map.json"


class PromptariaPreflightTests(unittest.TestCase):
    def run_preflight(self, request, destination=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            output_path = root / "plan.json"
            payload = {"request": request}
            if destination is not None:
                payload["destination"] = destination
            request_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(PREFLIGHT), "--request", str(request_path),
                 "--manifest", str(MANIFEST), "--execution-map", str(EXECUTION_MAP),
                 "--output", str(output_path)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            return json.loads(output_path.read_text(encoding="utf-8"))

    def test_master_protocol_plus_explicit_write_and_artifacts_destination_is_scoped(self):
        result = self.run_preflight(
            "PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO. "
            "github-operational: crie o resultado solicitado.",
            "artifacts/resultado.txt",
        )
        self.assertTrue(result["preauthorization"]["write_authorized"])
        self.assertEqual(result["preauthorization"]["status"], "scoped_preauthorization_eligible")
        self.assertFalse(result["execution_performed"])

    def test_title_mention_alone_never_authorizes_write(self):
        result = self.run_preflight(
            "PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO. "
            "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas.",
            "artifacts/resultado.txt",
        )
        self.assertFalse(result["preauthorization"]["write_authorized"])

    def test_external_or_source_destination_never_pre_authorized(self):
        request = (
            "PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO. "
            "github-operational: crie arquivo."
        )
        for destination in ("instruments/novo.md", "../outside.txt", "/tmp/out.txt", ".git/config"):
            with self.subTest(destination=destination):
                result = self.run_preflight(request, destination)
                self.assertFalse(result["preauthorization"]["write_authorized"])

    def test_preserves_multiple_instrument_matches(self):
        result = self.run_preflight(
            "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas; "
            "PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO."
        )
        ids = {item["id"] for item in result["matched_instruments"]}
        self.assertIn("github-operational", ids)
        self.assertIn("master-activation", ids)

    def test_unified_canonical_title_resolves_without_duplicate_identity(self):
        title = "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"
        result = self.run_preflight(title)
        matches = [item for item in result["matched_instruments"] if item["id"] == "github-operational"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["identity_status"], "resolved")
        self.assertTrue(matches[0]["activation"])
        self.assertNotIn("fixed-prompt-instrument-part-2", {item["id"] for item in result["matched_instruments"]})

    def test_colliding_title_can_be_resolved_by_explicit_id(self):
        result = self.run_preflight(
            "github-operational: Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas."
        )
        selected = [item for item in result["matched_instruments"] if item["id"] == "github-operational"]
        self.assertTrue(selected)
        self.assertEqual(selected[0]["identity_status"], "resolved")


if __name__ == "__main__":
    unittest.main()
