import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_contextual_executor as contextual


class ContextualAmbiguityGuardTests(unittest.TestCase):
    def setUp(self):
        self.context = {
            "selected_instrument_ids": ["alpha"],
            "task_candidates": [],
            "evidence_chain": [],
        }
        self.preflight = {
            "matched_instruments": [{
                "id": "alpha",
                "identity_status": "ambiguous_title_collision",
                "activation": False,
            }]
        }

    def test_contextual_selection_cannot_silently_resolve_title_collision(self):
        with patch.object(contextual.router, "analyze", return_value=self.context), \
             patch.object(contextual.specialized, "execute") as execute:
            with self.assertRaisesRegex(SystemExit, "Correspondência ambígua bloqueada"):
                contextual.execute({"request": "executar instrumento semelhante"}, self.preflight)
            execute.assert_not_called()

    def test_explicit_instrument_id_is_an_authorized_disambiguator(self):
        expected = {
            "execution_status": "completed",
            "specialized_execution_count": 1,
            "selected_instrument_ids": ["alpha"],
            "external_side_effects_performed": False,
        }
        with patch.object(contextual.router, "analyze", return_value=self.context), \
             patch.object(
                 contextual.specialized,
                 "index_catalog_entries",
                 return_value={"alpha": {"activation": {"enabled": True}}},
             ), \
             patch.object(contextual.specialized, "execute", return_value=expected) as execute:
            result = contextual.execute(
                {"request": "executar instrumento semelhante", "instrument_ids": ["alpha"]},
                self.preflight,
            )
        execute.assert_called_once()
        self.assertEqual(result["execution_status"], "completed")


if __name__ == "__main__":
    unittest.main()
