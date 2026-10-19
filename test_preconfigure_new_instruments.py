#!/usr/bin/env python3
"""Regression tests for automatic Promptária instrument preconfiguration."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "scripts"
    / "preconfigure_new_instruments.py"
)


class PreconfigureNewInstrumentsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "instruments").mkdir()
        (self.root / "config").mkdir()
        (self.root / "tests").mkdir()
        script_path = self.root / ".github" / "scripts" / "preconfigure_new_instruments.py"
        script_path.parent.mkdir(parents=True)
        shutil.copy2(SOURCE_SCRIPT, script_path)
        self.registry_path = self.root / "config" / "instrument-registry.json"
        self.manifest_path = self.root / "tests" / "manifest.json"
        self.write_json(self.registry_path, {"instruments": []})
        self.write_json(self.manifest_path, {"instruments": []})

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def write_json(path: Path, value: dict) -> None:
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def read_json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def run_preconfigure(self) -> subprocess.CompletedProcess[str]:
        script = self.root / ".github" / "scripts" / "preconfigure_new_instruments.py"
        return subprocess.run(
            [sys.executable, str(script)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_new_instrument_is_registered_but_not_activated_without_executor(self) -> None:
        source = self.root / "instruments" / "novo-instrumento.md"
        source.write_text("# Instrumento Novo\n\nConteúdo de teste.\n", encoding="utf-8")

        result = self.run_preconfigure()

        self.assertEqual(result.returncode, 0, result.stderr)
        registry = self.read_json(self.registry_path)["instruments"]
        manifest = self.read_json(self.manifest_path)["instruments"]
        self.assertEqual(len(registry), 1)
        self.assertEqual(len(manifest), 1)
        self.assertEqual(registry[0]["id"], "novo-instrumento")
        self.assertEqual(registry[0]["title"], "Instrumento Novo")
        self.assertEqual(registry[0]["path"], "instruments/novo-instrumento.md")
        self.assertFalse(registry[0]["activation"]["enabled"])
        self.assertEqual(registry[0]["activation"]["status"], "prepared_no_executor")
        self.assertFalse(registry[0]["ui"]["visible"])
        self.assertIn("não executáveis", result.stdout)
        self.assertEqual(manifest[0]["id"], registry[0]["id"])
        self.assertEqual(manifest[0]["title"], registry[0]["title"])

    def test_second_run_is_idempotent(self) -> None:
        source = self.root / "instruments" / "novo-instrumento.md"
        source.write_text("# Instrumento Novo\n", encoding="utf-8")

        first = self.run_preconfigure()
        second = self.run_preconfigure()

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(len(self.read_json(self.registry_path)["instruments"]), 1)
        self.assertEqual(len(self.read_json(self.manifest_path)["instruments"]), 1)
        entry = self.read_json(self.registry_path)["instruments"][0]
        self.assertFalse(entry["activation"]["enabled"])

    def test_duplicate_canonical_title_blocks_registration(self) -> None:
        (self.root / "instruments" / "existente.md").write_text(
            "# Título Duplicado\n", encoding="utf-8"
        )
        (self.root / "instruments" / "novo.md").write_text(
            "# Título Duplicado\n", encoding="utf-8"
        )
        self.write_json(
            self.registry_path,
            {"instruments": [{
                "id": "existente",
                "title": "Título Duplicado",
                "path": "instruments/existente.md",
            }]},
        )
        self.write_json(
            self.manifest_path,
            {"instruments": [{
                "id": "existente",
                "title": "Título Duplicado",
                "path": "instruments/existente.md",
                "aliases": [],
            }]},
        )

        result = self.run_preconfigure()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Título canônico duplicado", result.stderr)
        self.assertEqual(len(self.read_json(self.registry_path)["instruments"]), 1)

    def test_generated_id_collision_blocks_registration(self) -> None:
        (self.root / "instruments" / "existente.md").write_text(
            "# Instrumento Existente\n", encoding="utf-8"
        )
        (self.root / "instruments" / "novo-instrumento.md").write_text(
            "# Outro Instrumento\n", encoding="utf-8"
        )
        self.write_json(
            self.registry_path,
            {"instruments": [{
                "id": "novo-instrumento",
                "title": "Instrumento Existente",
                "path": "instruments/existente.md",
            }]},
        )
        self.write_json(
            self.manifest_path,
            {"instruments": [{
                "id": "novo-instrumento",
                "title": "Instrumento Existente",
                "path": "instruments/existente.md",
                "aliases": [],
            }]},
        )

        result = self.run_preconfigure()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ID gerado duplicado", result.stderr)
        self.assertEqual(len(self.read_json(self.registry_path)["instruments"]), 1)


if __name__ == "__main__":
    unittest.main()
