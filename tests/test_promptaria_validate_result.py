import unittest

from scripts.promptaria_validate_result import validate


class PromptariaResultValidationTests(unittest.TestCase):
    def valid_result(self):
        return {
            "schema_version": 2,
            "mandatory_components": [
                {"id": "functional-correference-architecture", "found": True,
                 "path": "instruments/arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md",
                 "category": "continuous_automation"},
                {"id": "master-activation", "found": True,
                 "path": "instruments/protocolo-mestre-acionamento-automatico.md",
                 "category": "continuous_automation"},
                {"id": "github-operational", "found": True,
                 "path": "instruments/acione-a-promptaria-pelo-github.md",
                 "category": "recoverable_on_demand"},
            ],
            "missing_mandatory_components": [],
            "preconfiguration": {
                "complete": True,
                "mandatory_component_ids": [
                    "functional-correference-architecture", "master-activation", "github-operational"
                ],
                "continuous_context_ids": [
                    "functional-correference-architecture", "master-activation"
                ],
                "continuous_context": [
                    {"id": "functional-correference-architecture", "category": "continuous_automation",
                     "loaded_as_context": True, "title_resolvable": False, "execution_performed": False,
                     "content": "# Arquitetura\n"},
                    {"id": "master-activation", "category": "continuous_automation",
                     "loaded_as_context": True, "title_resolvable": False, "execution_performed": False,
                     "content": "# Protocolo\n"},
                ],
                "continuous_context_complete": True,
                "fixed_operational_component": {
                    "id": "github-operational", "category": "recoverable_on_demand",
                    "path": "instruments/acione-a-promptaria-pelo-github.md",
                    "execution_performed": False, "content": "# GitHub\n"
                },
            },
            "matched_instruments": [
                {"content_recovered": True, "activation_status": "recognized_not_executed"},
                {"content_recovered": True, "activation_status": "included_in_plan_not_executed"},
            ],
            "write_execution_available": False,
            "status": "plan_created_needs_execution_integration",
        }

    def test_accepts_complete_traceable_plan(self):
        self.assertEqual(validate(self.valid_result()), [])

    def test_rejects_missing_mandatory_components(self):
        result = self.valid_result()
        result["missing_mandatory_components"] = ["missing"]
        self.assertTrue(validate(result))

    def test_rejects_false_claim_of_execution(self):
        result = self.valid_result()
        result["matched_instruments"][0]["activation_status"] = "executed"
        self.assertTrue(validate(result))

    def test_rejects_claim_that_write_execution_is_available(self):
        result = self.valid_result()
        result["write_execution_available"] = True
        self.assertTrue(validate(result))


if __name__ == "__main__":
    unittest.main()
