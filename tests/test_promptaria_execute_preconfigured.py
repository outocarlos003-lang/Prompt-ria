import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from promptaria_execute_preconfigured import authorize_from_preflight


class PreconfiguredExecutorAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.request_text = (
            "PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO. "
            "github-operational: crie o resultado solicitado."
        )
        self.payload = {
            "operation_id": "preflight-write-001",
            "operation": "write_text",
            "destination": "artifacts/result.txt",
            "content": "resultado",
            "request": self.request_text,
            "dry_run": False,
            "write_authorized": False,
        }
        self.preflight = {
            "request": self.request_text,
            "destination": "artifacts/result.txt",
            "matched_instruments": [{"id": "github-operational", "activation": True}],
            "preauthorization": {
                "status": "scoped_preauthorization_eligible",
                "write_authorized": True,
            },
        }

    def test_eligible_matching_preflight_supplies_scoped_authorization(self):
        authorized = authorize_from_preflight(self.payload, self.preflight)
        self.assertTrue(authorized["write_authorized"])
        self.assertEqual(authorized["authorization_source"], "eligible_master_protocol_preflight")
        self.assertFalse(self.payload["write_authorized"], "entrada original não deve ser mutada")

    def test_destination_mismatch_is_rejected(self):
        payload = dict(self.payload, destination="artifacts/other.txt")
        with self.assertRaises(SystemExit):
            authorize_from_preflight(payload, self.preflight)

    def test_request_mismatch_is_rejected(self):
        payload = dict(self.payload, request="pedido diferente")
        with self.assertRaises(SystemExit):
            authorize_from_preflight(payload, self.preflight)

    def test_ineligible_plan_is_rejected(self):
        plan = {
            **self.preflight,
            "preauthorization": {"status": "not_authorized", "write_authorized": False},
        }
        with self.assertRaises(SystemExit):
            authorize_from_preflight(self.payload, plan)

    def test_dry_run_must_be_explicitly_disabled_for_real_execution(self):
        payload = dict(self.payload, dry_run=True)
        with self.assertRaises(SystemExit):
            authorize_from_preflight(payload, self.preflight)


if __name__ == "__main__":
    unittest.main()
