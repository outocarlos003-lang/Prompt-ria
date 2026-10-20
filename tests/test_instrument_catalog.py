import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "instrument-catalog.json"
INSTRUMENTS = ROOT / "instruments"
sys.path.insert(0, str(ROOT / "scripts"))
from generate_instrument_catalog import title_for  # noqa: E402


class InstrumentCatalogTests(unittest.TestCase):
    def test_catalog_covers_every_markdown_instrument_exactly_once(self):
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        paths = [item["path"] for item in data["instruments"]]
        actual = sorted(p.relative_to(ROOT).as_posix() for p in INSTRUMENTS.glob("*.md"))
        self.assertEqual(paths, sorted(set(paths)))
        self.assertEqual(paths, actual)

    def test_catalog_entries_have_stable_titles(self):
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        for item in data["instruments"]:
            path = ROOT / item["path"]
            self.assertTrue(item["title"].strip())
            self.assertTrue(path.is_file())
            self.assertEqual(item["title"], title_for(path))


if __name__ == "__main__":
    unittest.main()
