import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
TRACE = ROOT / "config" / "interface-traceability-current.json"
GRAPH = ROOT / "config" / "traceability-graph-current.json"


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._ignored = 0
        self._hidden_depth = 0
        self.text_nodes = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style"}:
            self._ignored += 1
        if self._hidden_depth:
            self._hidden_depth += 1
        elif attrs.get("aria-hidden") == "true":
            self._hidden_depth = 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self._ignored = max(0, self._ignored - 1)
        if self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data):
        if not self._ignored and not self._hidden_depth and data.strip():
            self.text_nodes.append(" ".join(data.split()))


class TraceabilityPreconfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.trace = json.loads(TRACE.read_text(encoding="utf-8"))
        cls.graph = json.loads(GRAPH.read_text(encoding="utf-8"))
        parser = VisibleTextParser()
        parser.feed(cls.html)
        cls.visible_text = parser.text_nodes
        cls.elements = cls.trace["elements"]
        cls.nodes = cls.graph["nodes"]
        cls.relations = cls.graph["relations"]

    def test_every_visible_text_node_has_trace_entry(self):
        traced = {item["text"] for item in self.elements}
        for text in self.visible_text:
            self.assertIn(text, traced, f"interface term without trace: {text}")

    def test_every_trace_element_points_to_existing_file_and_selector(self):
        for item in self.elements:
            self.assertTrue((ROOT / item["file"]).is_file(), item["id"])
            selector = item["selector"]
            if selector.startswith("#"):
                identifier = selector.split()[0][1:]
                self.assertRegex(self.html, rf'\bid=["\']{re.escape(identifier)}["\']', item["id"])
            for class_name in re.findall(r"\.([A-Za-z_][\w-]*)", selector):
                self.assertRegex(self.html, rf'class=["\'][^"\']*\b{re.escape(class_name)}\b[^"\']*["\']', item["id"])

    def test_every_trace_element_has_function_and_destination(self):
        for item in self.elements:
            self.assertTrue(item.get("function"), item["id"])
            self.assertTrue(item.get("destination"), item["id"])
            self.assertIn(item.get("status"), {"verified", "pending_verification", "unverified"})

    def test_relations_have_nodes_or_explicit_repository_targets(self):
        node_ids = {item["id"] for item in self.nodes}
        for relation in self.relations:
            relation_id = relation["id"]
            self.assertTrue(relation.get("from"), relation_id)
            self.assertTrue(relation.get("to"), relation_id)
            self.assertTrue(relation.get("type"), relation_id)
            self.assertTrue(relation.get("function"), relation_id)
            self.assertTrue(relation.get("evidence"), relation_id)
            self.assertTrue(relation["from"] in node_ids or relation["from"].startswith("#") or "/" in relation["from"], relation_id)
            self.assertTrue(relation["to"] in node_ids or relation["to"].startswith("#") or "/" in relation["to"] or relation["to"].startswith("http") or relation["to"].endswith(".html"), relation_id)

    def test_graph_nodes_cover_interface_trace_ids(self):
        graph_ids = {item["id"] for item in self.nodes}
        for item in self.elements:
            self.assertIn(item["id"], graph_ids, item["id"])

    def test_policy_requires_future_updates(self):
        self.assertTrue(self.trace["policy"]["every_visible_term"])
        self.assertTrue(self.trace["policy"]["every_actionable_control"])
        self.assertTrue(self.graph["policy"]["every_node_requires_file_and_function"])
        self.assertTrue(self.graph["policy"]["every_relation_requires_evidence"])


if __name__ == "__main__":
    unittest.main()
