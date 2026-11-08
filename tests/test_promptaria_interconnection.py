import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_interconnection as interconnection


class CrossSegmentInterconnectionTests(unittest.TestCase):
    def registry(self):
        return {"instruments": [
            {
                "id": "continuous-a", "title": "Prepare demand",
                "category": "continuous_automation", "path": "continuous/a.md",
                "functions": ["prepare request", "preserve context"],
                "operations": ["prepare"], "keywords": ["request", "traceability"],
                "ui": {"node_id": "instrument:continuous-a"},
                "activation": {"enabled": True},
            },
            {
                "id": "demand-b", "title": "Recover demand",
                "category": "recoverable_on_demand", "path": "recoverable/b.md",
                "functions": ["prepare request", "recover content"],
                "operations": ["recover"], "keywords": ["request", "traceability"],
                "ui": {"node_id": "instrument:demand-b"},
                "activation": {"enabled": True},
            },
        ]}

    def test_procedure_is_linked_but_instrument_identity_is_not_merged(self):
        result = interconnection.build(self.registry(), ["demand-b"], "req-001")
        self.assertEqual(result["interconnection_count"], 1)
        link = result["interconnections"][0]
        self.assertEqual(link["pair_id"], "cross-segment:continuous-a:demand-b")
        self.assertEqual(link["shared_node_id"], "coordination:cross-segment:continuous-a:demand-b")
        self.assertEqual(link["request_id"], "req-001")
        self.assertFalse(link["identity_merge"])
        self.assertEqual(link["instrument_count_delta"], 0)
        self.assertEqual(link["phase_status"]["on_demand_recovery"], "selected_for_request")
        self.assertEqual(link["continuous_instrument"]["path"], "continuous/a.md")
        self.assertEqual(link["recoverable_instrument"]["path"], "recoverable/b.md")
        self.assertEqual(link["continuous_instrument"]["functions_preserved"], ["prepare request", "preserve context"])
        self.assertEqual(link["recoverable_instrument"]["functions_preserved"], ["prepare request", "recover content"])
        self.assertTrue(result["independent_instrument_count_preserved"])
        self.assertTrue(result["independent_ids_and_paths_preserved"])
        self.assertTrue(result["independent_functions_preserved"])

    def test_unmatched_pair_is_not_forced_into_relation(self):
        registry = self.registry()
        registry["instruments"][0]["functions"] = ["prepare"]
        registry["instruments"][0]["operations"] = ["prepare"]
        registry["instruments"][0]["keywords"] = ["alpha"]
        registry["instruments"][1]["functions"] = ["render"]
        registry["instruments"][1]["operations"] = ["render"]
        registry["instruments"][1]["keywords"] = ["omega"]
        registry["instruments"][0]["title"] = "Alpha"
        registry["instruments"][1]["title"] = "Omega"
        self.assertEqual(interconnection.build(registry)["interconnections"], [])

    def test_request_id_is_propagated_without_changing_pair_identity(self):
        first = interconnection.build(self.registry(), request_id="request-one")
        second = interconnection.build(self.registry(), request_id="request-two")
        self.assertEqual(first["interconnections"][0]["pair_id"], second["interconnections"][0]["pair_id"])
        self.assertNotEqual(first["request_id"], second["request_id"])
        self.assertEqual(first["interconnections"][0]["request_id"], "request-one")
        self.assertEqual(second["interconnections"][0]["request_id"], "request-two")

    def test_matching_does_not_authorize_execution_or_side_effects(self):
        result = interconnection.build(self.registry(), ["demand-b"], "req-safe")
        self.assertFalse(result["side_effects_authorized"])
        self.assertFalse(result["matching_activates_instruments"])


if __name__ == "__main__":
    unittest.main()
