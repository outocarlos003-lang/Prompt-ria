import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_context_router as router


class TraceabilityContextRouterTests(unittest.TestCase):
    def test_traceability_request_activates_integrity_rule(self):
        result = router.analyze({
            "request": "Atualize o sistema para que termos da interface possuam rastreabilidade com nós, relações, funções, arquivos, origem, destino e evidências, mantendo correspondência para demandas futuras."
        })
        tasks = {item["task"] for item in result["task_candidates"]}
        self.assertIn("traceability_integrity", tasks)
        self.assertTrue(result["evidence_chain"][-1]["enabled"])
        self.assertTrue(set(router.BASE_IDS).issubset(set(result["selected_instrument_ids"])))
        self.assertFalse(result["external_side_effects_authorized"])


if __name__ == "__main__":
    unittest.main()
