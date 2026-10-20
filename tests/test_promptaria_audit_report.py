import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTRUMENTS = REPO_ROOT / "instruments"
REPORT = REPO_ROOT / "docs" / "auditoria-operacional-inicial.md"


class OperationalAuditReportTests(unittest.TestCase):
    def test_every_markdown_instrument_is_classified_exactly_once(self):
        report = REPORT.read_text(encoding="utf-8")
        section = report.split("## Classificação dos instrumentos promptuais", 1)[1].split(
            "## Inventário de mecanismos de execução", 1
        )[0]
        rows = [
            line for line in section.splitlines()
            if line.startswith("|") and "instruments/" in line and line.endswith("|")
            and not line.startswith("| ID /")
        ]
        recorded_paths = []
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertGreaterEqual(len(cells), 5, msg=row)
            path_match = re.search(r"`(instruments/[^\x60]+\.md)`", cells[1])
            self.assertIsNotNone(path_match, msg=row)
            recorded_paths.append(path_match.group(1))
            self.assertEqual(cells[2], "Parcialmente automatizado")

        actual_paths = sorted(path.relative_to(REPO_ROOT).as_posix() for path in INSTRUMENTS.glob("*.md"))
        self.assertEqual(sorted(recorded_paths), actual_paths)
        self.assertEqual(len(recorded_paths), len(set(recorded_paths)))

    def test_manifest_covers_every_instrument_with_matching_canonical_title(self):
        manifest_path = REPO_ROOT / "tests" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest.get("instruments")
        self.assertIsInstance(entries, list)

        ids = [entry.get("id") for entry in entries]
        paths = [entry.get("path") for entry in entries]
        self.assertEqual(len(ids), len(set(ids)), "instrument IDs must be unique")
        self.assertEqual(len(paths), len(set(paths)), "manifest paths must be unique")

        actual_paths = {
            path.relative_to(REPO_ROOT).as_posix()
            for path in INSTRUMENTS.glob("*.md")
        }
        self.assertEqual(set(paths), actual_paths)

        for entry in entries:
            with self.subTest(path=entry.get("path")):
                self.assertIsInstance(entry.get("title"), str)
                self.assertIsInstance(entry.get("aliases"), list)
                physical = (REPO_ROOT / entry["path"]).read_text(encoding="utf-8")
                title_match = re.search(r"(?m)^#\s+(.+?)\s*$", physical)
                self.assertIsNotNone(title_match)
                self.assertEqual(title_match.group(1).strip(), entry["title"])
                self.assertTrue(all(isinstance(alias, str) and alias.strip() for alias in entry["aliases"]))

    def test_report_explicitly_separates_implementation_integration_and_execution(self):
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Implementado", report)
        self.assertIn("integrado", report.lower())
        self.assertIn("execução", report.lower())
        self.assertIn("Limites desta auditoria", report)


if __name__ == "__main__":
    unittest.main()
