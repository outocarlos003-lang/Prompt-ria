import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVER = REPO_ROOT / "scripts" / "promptaria_resolver.py"


class PromptariaResolverTests(unittest.TestCase):
    def run_resolver(self, request_text, instruments):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            instrument_dir = root / "instruments"
            instrument_dir.mkdir()
            for filename, title in instruments:
                (instrument_dir / filename).write_text(f"# {title}\n\nConteúdo de teste.\n", encoding="utf-8")
            request_path = root / "request.json"
            output_path = root / "result.json"
            request_path.write_text(json.dumps({"request": request_text}, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(RESOLVER), "--request", str(request_path),
                 "--instruments", str(instrument_dir), "--output", str(output_path)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            self.assertTrue(output_path.exists())
            return json.loads(output_path.read_text(encoding="utf-8")), completed.stdout

    def test_includes_all_three_mandatory_components(self):
        instruments = [
            ("coordinator.md", "ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS"),
            ("master.md", "PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO"),
            ("github.md", "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"),
        ]
        result, stdout = self.run_resolver("Demanda genérica de teste.", instruments)
        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(len(result["mandatory_components"]), 3)
        self.assertEqual(result["missing_mandatory_components"], [])
        self.assertEqual(len(result["matched_instruments"]), 3)
        self.assertIn("3/3", stdout)

    def test_preserves_every_explicit_title_match(self):
        instruments = [
            ("alpha.md", "Instrumento Alfa"),
            ("beta.md", "Instrumento Beta"),
            ("gamma.md", "Instrumento Gama"),
        ]
        result, _ = self.run_resolver("Aplicar Instrumento Alfa e Instrumento Beta e Instrumento Gama.", instruments)
        matched = {item["title"] for item in result["matched_instruments"]}
        self.assertTrue({"Instrumento Alfa", "Instrumento Beta", "Instrumento Gama"}.issubset(matched))

    def test_reports_missing_mandatory_components_without_crashing(self):
        result, stdout = self.run_resolver("Pedido de teste.", [("one.md", "Instrumento Único")])
        self.assertEqual(len(result["missing_mandatory_components"]), 3)
        self.assertEqual(result["mandatory_components"], [])
        self.assertIn("0/3", stdout)

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
