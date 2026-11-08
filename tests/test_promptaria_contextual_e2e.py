"""End-to-end contract test for the preflight → contextual → specialized executor path."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ContextualExecutorEndToEndTests(unittest.TestCase):
    def test_preflight_and_contextual_executor_emit_traceable_local_result(self):
        with tempfile.TemporaryDirectory(prefix="promptaria-e2e-") as temporary:
            work = Path(temporary)
            request_path = work / "request.json"
            preflight_path = work / "preflight.json"
            result_path = work / "execution.json"
            request = {
                "request": "Validar o fluxo integrado de execução especializada da Promptária.",
                "instrument_ids": ["github-operational"],
                "dry_run": True,
            }
            request_path.write_text(
                json.dumps(request, ensure_ascii=False) + "\n", encoding="utf-8"
            )

            preflight = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promptaria_preflight.py"),
                    "--request",
                    str(request_path),
                    "--output",
                    str(preflight_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                preflight.returncode,
                0,
                msg=f"preflight failed:\n{preflight.stdout}\n{preflight.stderr}",
            )
            self.assertTrue(preflight_path.is_file(), "preflight artifact was not created")

            execution = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promptaria_contextual_executor.py"),
                    "--request",
                    str(request_path),
                    "--preflight",
                    str(preflight_path),
                    "--output",
                    str(result_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                execution.returncode,
                0,
                msg=f"contextual execution failed:\n{execution.stdout}\n{execution.stderr}",
            )
            self.assertTrue(result_path.is_file(), "execution artifact was not created")
            result = json.loads(result_path.read_text(encoding="utf-8"))

            self.assertEqual(result["execution_status"], "completed")
            self.assertIn("github-operational", result["selected_instrument_ids"])
            self.assertGreaterEqual(result["specialized_execution_count"], 1)
            self.assertFalse(result["external_side_effects_performed"])
            self.assertEqual(
                result["routing_evidence"]["routing_status"],
                "contextual_handlers_executed",
            )

            matching = [
                item for item in result["results"]
                if item.get("instrument_id") == "github-operational"
            ]
            self.assertEqual(len(matching), 1)
            evidence = matching[0]
            self.assertEqual(evidence["execution_status"], "completed")
            self.assertEqual(evidence["side_effects"], [])
            source = ROOT / evidence["source_path"]
            self.assertEqual(
                evidence["source_sha256"],
                hashlib.sha256(source.read_bytes()).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
