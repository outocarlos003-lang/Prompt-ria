import json
import tempfile
import unittest
from pathlib import Path
from scripts.promptaria_registry_audit import REQUIRED, audit, normalize


def registry_payload(entries):
    return {
        "schema_version": 2,
        "identity_contract": {
            "required": list(REQUIRED),
            "matching": "canonical title; only activation.enabled=true instruments are functionally resolvable",
        },
        "instruments": entries,
    }


class RegistryAuditTests(unittest.TestCase):
    def test_normalization_folds_case_accents_and_punctuation(self):
        self.assertEqual(normalize("  PRÉ-configuração: Árvore! "), "pre configuracao arvore")

    def test_detects_missing_file_and_title_collision_without_claiming_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config").mkdir()
            registry = registry_payload([
                {"id":"a","title":"Título Um","path":"instruments/missing.md","aliases":["igual"],
                 "keywords":[],"functions":["x"],"files":["scripts/x.py"],"relations":[],"operations":["resolve"],
                 "ui":{"node_id":"instrument:a"},"activation":{"enabled":True,"status":"active"}},
                {"id":"b","title":"Outro","path":"instruments/other.md","aliases":["IGUAL"],
                 "keywords":[],"functions":["y"],"files":[],"relations":[],"operations":["plan"],
                 "ui":{"node_id":"instrument:b"},"activation":{"enabled":False,"status":"prepared"}}
            ])
            p = root / "config/instrument-registry.json"
            p.write_text(json.dumps(registry), encoding="utf-8")
            result = audit(p, root)
            self.assertTrue(result["valid"])
            self.assertEqual(result["instrument_count"], 2)
            self.assertTrue(result["normalized_title_collisions"])
            self.assertEqual(result["normalized_title_collisions"][0]["severity"], "warning")
            self.assertIn("explicit_instrument_id", result["resolution_index"]["precedence"])
            self.assertTrue(any("instrument file missing" in warning for warning in result["warnings"]))
            self.assertTrue(any("declared referenced file missing: scripts/x.py" in warning for warning in result["warnings"]))
            self.assertEqual(result["instruments"][0]["classification"], "partially_automated")
            self.assertEqual(result["instruments"][1]["classification"], "without_active_executor")

    def test_rejects_duplicate_ids_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "config").mkdir()
            entry = {"id":"same","title":"A","path":"instruments/../secret.md","aliases":[],
                     "keywords":[],"functions":["x"],"files":[],"relations":[],"operations":["x"],
                     "ui":{"node_id":"instrument:same"},"activation":{"enabled":False}}
            p=root/"config/instrument-registry.json"
            p.write_text(json.dumps(registry_payload([entry,entry])),encoding="utf-8")
            result=audit(p,root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("duplicate id" in e for e in result["errors"]))
            self.assertTrue(any("unsafe" in e for e in result["errors"]))

    def test_rejects_unsafe_declared_dependency_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "config").mkdir()
            entry = {"id":"unsafe-dependency","title":"A","path":"instruments/a.md","aliases":[],
                     "keywords":[],"functions":["x"],"files":["scripts/../secret.py"],"relations":[],
                     "operations":["x"],"ui":{"node_id":"instrument:unsafe-dependency"},"activation":{"enabled":False}}
            p = root / "config/instrument-registry.json"
            p.write_text(json.dumps(registry_payload([entry])), encoding="utf-8")
            result = audit(p, root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("unsafe referenced file path" in error for error in result["errors"]))

    def test_blocks_collision_between_two_enabled_instruments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "config").mkdir()
            entries = []
            for ident, title in (("a", "Instrumento Alfa"), ("b", "Instrumento Beta")):
                entries.append({"id":ident,"title":title,"path":f"instruments/{ident}.md",
                                "aliases":["mesmo alias"],"keywords":[],"functions":["x"],"files":[],
                                "relations":[],"operations":["resolve"],"ui":{"node_id":f"instrument:{ident}"},
                                "activation":{"enabled":True,"status":"active"}})
            p = root / "config/instrument-registry.json"
            p.write_text(json.dumps(registry_payload(entries)), encoding="utf-8")
            result = audit(p, root)
            self.assertFalse(result["valid"])
            collision = next(x for x in result["normalized_title_collisions"] if x["normalized_term"] == "mesmo alias")
            self.assertEqual(collision["severity"], "blocking")
            self.assertEqual(collision["resolution"], "explicit_id_or_path_required")

    def test_rejects_registry_title_that_diverges_from_canonical_h1(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "config").mkdir(); (root / "instruments").mkdir()
            (root / "instruments/a.md").write_text("# Título Canônico\n", encoding="utf-8")
            entry = {"id":"a","title":"Título Diferente","path":"instruments/a.md","aliases":[],
                     "keywords":[],"functions":["x"],"files":["instruments/a.md"],"relations":[],
                     "operations":["resolve"],"ui":{"node_id":"instrument:a"},"activation":{"enabled":True,"status":"active"}}
            p = root / "config/instrument-registry.json"
            p.write_text(json.dumps(registry_payload([entry])), encoding="utf-8")
            result = audit(p, root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("does not match canonical H1" in error for error in result["errors"]))

    def test_rejects_orphan_physical_instrument(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "config").mkdir(); (root / "instruments").mkdir()
            (root / "instruments/new.md").write_text("# Novo Instrumento\n", encoding="utf-8")
            p = root / "config/instrument-registry.json"
            p.write_text(json.dumps(registry_payload([])), encoding="utf-8")
            result = audit(p, root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("Unregistered instrument definition" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
