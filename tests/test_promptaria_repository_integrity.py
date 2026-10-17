"""Repository-level integrity checks for Promptária's automatic preconfiguration."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from promptaria_resolver import normalize, read_instruments, resolve
from promptaria_validate_result import validate


class RepositoryIntegrityTests(unittest.TestCase):
    def test_instruments_directory_contains_readable_markdown_instruments(self):
        instruments_dir = ROOT / "instruments"
        self.assertTrue(instruments_dir.is_dir(), "Diretório instruments/ ausente.")
        files = sorted(instruments_dir.rglob("*.md"))
        self.assertTrue(files, "Nenhum instrumento Markdown foi encontrado.")

        for path in files:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                content = path.read_text(encoding="utf-8")
                self.assertTrue(content.strip(), "Instrumento vazio.")
                self.assertRegex(content, r"(?m)^#\s+\S", "Instrumento sem título de primeiro nível.")

    def test_instrument_titles_normalize_and_each_instrument_has_a_distinct_path(self):
        instruments = read_instruments(ROOT / "instruments")
        self.assertTrue(instruments, "O resolvedor não encontrou instrumentos.")
        paths = [item["path"] for item in instruments]
        self.assertEqual(len(paths), len(set(paths)), "Um caminho de instrumento foi incluído mais de uma vez.")
        for item in instruments:
            with self.subTest(path=item["path"]):
                self.assertTrue(normalize(item["title"]), "Título vazio após normalização.")

    def test_duplicate_titles_are_preserved_as_distinct_instruments(self):
        instruments = read_instruments(ROOT / "instruments")
        grouped = {}
        for item in instruments:
            grouped.setdefault(item["normalized_title"], []).append(item)
        aliases = [items for items in grouped.values() if len(items) > 1]
        for items in aliases:
            self.assertEqual(len({item["path"] for item in items}), len(items))
            matches = resolve(items[0]["title"], instruments)
            matched_paths = {item["path"] for item in matches}
            self.assertTrue({item["path"] for item in items}.issubset(matched_paths))

    def test_three_preconfiguration_components_exist_in_repository(self):
        instruments = read_instruments(ROOT / "instruments")
        titles = {item["normalized_title"] for item in instruments}
        required = {
            normalize("ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS"),
            normalize("PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO"),
            normalize("Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"),
        }
        self.assertTrue(required.issubset(titles), f"Componentes-base ausentes: {sorted(required - titles)}")

    def test_resolver_output_contract_rejects_false_execution_claims(self):
        valid = {
            "schema_version": 2,
            "mandatory_components": [{"found": True}, {"found": True}, {"found": True}],
            "missing_mandatory_components": [],
            "matched_instruments": [{
                "content_recovered": True,
                "activation_status": "recognized_not_executed",
            }],
            "write_execution_available": False,
            "status": "plan_created_needs_execution_integration",
        }
        self.assertEqual(validate(valid), [])

        invalid = dict(valid)
        invalid["write_execution_available"] = True
        self.assertTrue(validate(invalid), "O validador aceitou uma alegação de escrita disponível.")

    def test_resolver_does_not_match_partial_titles(self):
        instruments = [{
            "title": "Instrumento Alfa",
            "path": "instruments/alfa.md",
            "content": "# Instrumento Alfa\n",
            "normalized_title": normalize("Instrumento Alfa"),
        }]
        self.assertEqual(resolve("Aplicar Instrumento Alfas agora", instruments), [])
        self.assertEqual(len(resolve("Aplicar Instrumento Alfa agora", instruments)), 1)


if __name__ == "__main__":
    unittest.main()
