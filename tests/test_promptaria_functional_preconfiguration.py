import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = (
    "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E "
    "APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE "
    "INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E "
    "APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL "
    "AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO "
    "GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA "
    "SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, "
    "COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE "
    "MÚLTIPLOS TÍTULOS"
)


class FunctionalCrossReferencePreconfigurationTests(unittest.TestCase):
    def test_preconfiguration_is_added_to_future_plans_without_claiming_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            instruments = root / "instruments"
            instruments.mkdir()
            (instruments / "cross-reference.md").write_text(
                f"# {TITLE}\n\nPreservar correspondência cumulativa.\n",
                encoding="utf-8",
            )
            request = root / "request.json"
            request.write_text(
                json.dumps({"request": "Processar uma demanda futura.", "dry_run": True}),
                encoding="utf-8",
            )
            output = root / "result.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promptaria_resolver.py"),
                    "--request", str(request),
                    "--instruments", str(instruments),
                    "--output", str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(output.read_text(encoding="utf-8"))
            matches = [
                item for item in result["matched_instruments"]
                if item.get("identity") == "mandatory_functional_cross_reference_preconfiguration"
            ]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["title"], TITLE)
            self.assertTrue(matches[0]["content_recovered"])
            self.assertEqual(matches[0]["activation_status"], "included_in_plan_not_executed")
            self.assertEqual(matches[0]["exception_status"], "requires_contextual_review")


if __name__ == "__main__":
    unittest.main()
