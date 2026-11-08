"""Contract tests for explicit auxiliary-protocol recovery in the published UI."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class AuxiliaryProtocolInterfaceTests(unittest.TestCase):
    def test_operational_registry_uses_existing_root_path(self):
        self.assertIn("const registryUrl='./instrument-registry.json", HTML)
        self.assertNotIn("./config/instrument-registry.json", HTML)

    def test_auxiliary_registry_is_loaded_separately(self):
        self.assertIn("const auxiliaryRegistryUrl='./auxiliary-protocols/registry.json", HTML)
        self.assertIn("auxiliaryData.protocols", HTML)
        self.assertIn("let auxiliaryProtocols=[];", HTML)

    def test_auxiliary_resolution_is_explicit_and_non_operational(self):
        self.assertIn("function resolveAuxiliaryProtocolReference(reference)", HTML)
        self.assertIn("normalize(item.id)===normalized || normalize(item.title)===normalized", HTML)
        self.assertIn("item.operational_membership===false", HTML)
        self.assertIn("item.activation?.enabled===true", HTML)
        self.assertIn("item.path.startsWith('auxiliary-protocols/')", HTML)
        self.assertIn("!item.path.split('/').includes('..')", HTML)

    def test_auxiliary_resolution_does_not_add_protocols_to_operational_cards(self):
        self.assertIn("render(registry);", HTML)
        self.assertIn("resolveAuxiliaryProtocolReference(search.value)", HTML)
        self.assertIn("resolveAuxiliaryProtocolReference});", HTML)


if __name__ == "__main__":
    unittest.main()
