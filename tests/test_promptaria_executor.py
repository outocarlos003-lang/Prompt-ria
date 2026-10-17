import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECUTOR = ROOT / "scripts" / "promptaria_executor.py"
PERMISSIONS = ROOT / "config" / "promptaria_permissions.json"


class PromptariaExecutorTests(unittest.TestCase):
    def run_executor(self, payload, *extra):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        request = root / "request.json"
        request.write_text(json.dumps(payload), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(EXECUTOR), "--request", str(request),
             "--repo-root", str(root), "--permissions", str(PERMISSIONS), *extra],
            capture_output=True, text=True, encoding="utf-8",
        )
        return root, proc

    def base(self, **overrides):
        payload = {
            "operation_id": "test-op-001",
            "operation": "write_text",
            "destination": "artifacts/result.txt",
            "content": "resultado validável\n",
        }
        payload.update(overrides)
        return payload

    def test_defaults_to_dry_run_and_does_not_write(self):
        root, proc = self.run_executor(self.base())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["executed"])
        self.assertFalse((root / "artifacts/result.txt").exists())
        self.assertTrue((root / ".promptaria/audit.jsonl").exists())

    def test_real_write_requires_explicit_confirmation(self):
        root, proc = self.run_executor(self.base(dry_run=False, write_authorized=True))
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((root / "artifacts/result.txt").exists())

    def test_authorized_write_is_atomic_and_hash_validated(self):
        root, proc = self.run_executor(
            self.base(dry_run=False, write_authorized=True), "--confirm-operation", "test-op-001"
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertTrue(result["executed"])
        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["content_sha256"], result["result_content_sha256"])
        self.assertEqual((root / "artifacts/result.txt").read_text(encoding="utf-8"), "resultado validável\n")

    def test_rejects_path_traversal_and_absolute_paths(self):
        for path in ("../outside.txt", "artifacts/../../outside", "/tmp/file", r"artifacts\file.txt", ".git/config"):
            with self.subTest(path=path):
                _, proc = self.run_executor(self.base(destination=path))
                self.assertNotEqual(proc.returncode, 0)

    def test_rejects_non_allowlisted_destination_and_operation(self):
        _, proc = self.run_executor(self.base(destination="scripts/new.py"))
        self.assertNotEqual(proc.returncode, 0)
        _, proc = self.run_executor(self.base(operation="run_shell"))
        self.assertNotEqual(proc.returncode, 0)

    def test_rejects_non_boolean_flags_and_non_text_content(self):
        for payload in (self.base(dry_run="false"), self.base(write_authorized=1), self.base(content={"cmd": "unsafe"})):
            with self.subTest(payload=payload):
                _, proc = self.run_executor(payload)
                self.assertNotEqual(proc.returncode, 0)


    def test_rejects_replay_after_successful_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = root / "request.json"
            request.write_text(json.dumps(self.base(dry_run=False, write_authorized=True)), encoding="utf-8")
            command = [
                sys.executable, str(EXECUTOR), "--request", str(request),
                "--repo-root", str(root), "--permissions", str(PERMISSIONS),
                "--confirm-operation", "test-op-001",
            ]
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(first.returncode, 0, first.stderr)
            original = (root / "artifacts/result.txt").read_text(encoding="utf-8")
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("já concluiu uma escrita", second.stderr)
            self.assertEqual((root / "artifacts/result.txt").read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
