import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
TRACE = ROOT / "config" / "interface-traceability-current.json"


class InterfaceTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.hidden_depth = 0
        self.text_nodes = []
        self.placeholders = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style"}:
            self.skip += 1
        if self.hidden_depth:
            self.hidden_depth += 1
        elif attrs.get("aria-hidden") == "true":
            self.hidden_depth = 1
        if "placeholder" in attrs:
            self.placeholders.append(attrs["placeholder"])

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = max(0, self.skip - 1)
        if self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.skip and not self.hidden_depth and data.strip():
            self.text_nodes.append(" ".join(data.split()))


class InterfaceTraceabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.trace = json.loads(TRACE.read_text(encoding="utf-8"))
        parser = InterfaceTextParser()
        parser.feed(cls.html)
        cls.visible_text = parser.text_nodes
        cls.placeholders = parser.placeholders
        cls.elements = cls.trace["elements"]

    def test_trace_registry_has_unique_ids(self):
        ids = [item["id"] for item in self.elements]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(ids)

    def test_every_declared_source_exists(self):
        for item in self.elements:
            self.assertTrue((ROOT / item["file"]).is_file(), item["id"])

    def test_every_visible_term_is_traced(self):
        traced = {item["text"] for item in self.elements}
        for text in self.visible_text:
            self.assertIn(text, traced, f"interface term without trace: {text}")

    def test_every_placeholder_is_traced(self):
        traced = {item["text"] for item in self.elements}
        for placeholder in self.placeholders:
            self.assertIn(placeholder, traced, f"placeholder without trace: {placeholder}")

    def test_trace_selectors_point_to_real_index_anchors(self):
        for item in self.elements:
            selector = item["selector"]
            if selector.startswith("#"):
                identifier = selector.split()[0][1:]
                self.assertRegex(self.html, rf'\bid=["\']{re.escape(identifier)}["\']', item["id"])
            for class_name in re.findall(r"\.([A-Za-z_][\w-]*)", selector):
                self.assertRegex(self.html, rf'class=["\'][^"\']*\b{re.escape(class_name)}\b[^"\']*["\']', item["id"])

    def test_every_trace_entry_has_function_destination_and_status(self):
        for item in self.elements:
            self.assertTrue(item.get("function"), item["id"])
            self.assertTrue(item.get("destination"), item["id"])
            self.assertIn(item.get("status"), {"verified", "pending_verification", "unverified"})

    def test_interface_is_the_current_entrypoint_and_search_surface(self):
        self.assertIn('id="plataforma"', self.html)
        self.assertIn('id="instrumentos"', self.html)
        self.assertIn('id="instrumentos-title"', self.html)
        self.assertIn('id="instrument-search"', self.html)
        self.assertIn('type="search"', self.html)
        self.assertIn("Instrumentos promptuais", self.html)

    def test_search_trace_matches_the_registry_loaded_by_index(self):
        search_trace = next(item for item in self.elements if item["id"] == "ui.search.placeholder")
        self.assertEqual(search_trace["destination"], "config/instrument-registry.json")
        self.assertIn("config/instrument-registry.json", self.html)
        self.assertIn("fetch(registryUrl", self.html)
        self.assertIn("item.activation?.enabled===true", self.html)
        self.assertIn("search.addEventListener", self.html)
        self.assertEqual(search_trace["status"], "pending_verification")
    def test_old_catalog_card_assumptions_are_not_required(self):
        for removed in ["#filter", "#instrument-list", "#doc-overlay", "#copy-prompt", "renderCatalog"]:
            self.assertNotIn(removed, self.html)


if __name__ == "__main__":
    unittest.main()
