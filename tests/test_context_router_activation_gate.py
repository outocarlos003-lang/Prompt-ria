"""Ensure contextual routing never selects instruments disabled in the canonical registry."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_context_router as router


class ContextRouterActivationGateTests(unittest.TestCase):
    def test_contextual_rules_report_but_do_not_select_disabled_instruments(self):
        request = "Atualizar arquivo no repositório para corrigir rastreabilidade e catálogo."
        result = router.analyze(request)

        registry = router.json.loads(router.REGISTRY.read_text(encoding="utf-8"))
        enabled_ids = {
            item["id"] for item in registry["instruments"]
            if item.get("activation", {}).get("enabled") is True
        }
        selected = set(result["selected_instrument_ids"])

        self.assertTrue(selected)
        self.assertTrue(selected.issubset(enabled_ids))
        for candidate in result["task_candidates"]:
            self.assertTrue(set(candidate["selected_instrument_ids"]).issubset(enabled_ids))
            if candidate["blocked_inactive_instrument_ids"]:
                self.assertEqual(candidate["status"], "contextual_candidate" if candidate["selected_instrument_ids"] else "blocked_inactive_registry")

    def test_disabled_task_candidates_are_visible_as_blocked_evidence(self):
        result = router.analyze("Atualizar arquivo no repositório para corrigir rastreabilidade e catálogo.")
        blocked = {
            instrument_id
            for candidate in result["task_candidates"]
            for instrument_id in candidate["blocked_inactive_instrument_ids"]
        }
        self.assertTrue({"master-execution", "coordinator", "catalog-sitemap-preconfiguration"}.issubset(blocked))
        self.assertFalse(blocked.intersection(result["selected_instrument_ids"]))


if __name__ == "__main__":
    unittest.main()
