import json
import hashlib
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


    def test_concurrent_replay_allows_only_one_successful_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = root / "request.json"
            request.write_text(json.dumps(self.base(dry_run=False, write_authorized=True)), encoding="utf-8")
            command = [
                sys.executable, str(EXECUTOR), "--request", str(request),
                "--repo-root", str(root), "--permissions", str(PERMISSIONS),
                "--confirm-operation", "test-op-001",
            ]
            first = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
            second = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
            outcomes = [first.communicate(timeout=10) + (first.returncode,), second.communicate(timeout=10) + (second.returncode,)]
            self.assertEqual(sum(1 for _, _, code in outcomes if code == 0), 1, outcomes)
            self.assertEqual(sum(1 for _, stderr, code in outcomes if code != 0 and "já concluiu uma escrita" in stderr), 1, outcomes)
            self.assertEqual((root / "artifacts/result.txt").read_text(encoding="utf-8"), "resultado validável\n")
            audit_records = [
                json.loads(line)
                for line in (root / ".promptaria/audit.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(sum(1 for record in audit_records if record.get("status") == "executed"), 1)


    def test_audit_hash_chain_detects_tampering_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = root / "request.json"
            request.write_text(json.dumps(self.base()), encoding="utf-8")
            command = [
                sys.executable, str(EXECUTOR), "--request", str(request),
                "--repo-root", str(root), "--permissions", str(PERMISSIONS),
            ]
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(first.returncode, 0, first.stderr)
            audit = root / ".promptaria/audit.jsonl"
            audit_bytes = audit.read_bytes()
            self.assertTrue(audit_bytes.endswith(bytes([10])), "audit JSONL must end with an actual LF byte")
            record = json.loads(audit_bytes.splitlines()[0].decode("utf-8"))
            self.assertIn("audit_hash", record)
            self.assertEqual(record["audit_prev_hash"], "0" * 64)

            record["destination"] = "artifacts/forged.txt"
            audit.write_bytes(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + bytes([10]))
            request.write_text(json.dumps(self.base(operation_id="test-op-002")), encoding="utf-8")
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("Integridade da cadeia", second.stderr)

    def test_audit_hash_chain_links_sequential_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = root / "request.json"
            command = [
                sys.executable, str(EXECUTOR), "--request", str(request),
                "--repo-root", str(root), "--permissions", str(PERMISSIONS),
            ]
            request.write_text(json.dumps(self.base(operation_id="test-op-101")), encoding="utf-8")
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(first.returncode, 0, first.stderr)
            request.write_text(json.dumps(self.base(operation_id="test-op-102")), encoding="utf-8")
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(second.returncode, 0, second.stderr)
            records = [
                json.loads(line)
                for line in (root / ".promptaria/audit.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(records), 2)
            self.assertEqual(records[1]["audit_prev_hash"], records[0]["audit_hash"])



    def test_write_intent_precedes_mutation_and_truncated_completion_fails_closed(self):
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
            audit = root / ".promptaria/audit.jsonl"
            lines = audit.read_bytes().splitlines(keepends=True)
            self.assertEqual(len(lines), 2)
            intent = json.loads(lines[0])
            completed = json.loads(lines[1])
            self.assertEqual(intent["status"], "write_intent")
            self.assertFalse(intent["executed"])
            self.assertEqual(completed["status"], "executed")
            self.assertTrue(completed["executed"])

            # Simulate loss of the final completion record. The remaining chain
            # is syntactically valid, but the durable intent must block replay.
            audit.write_bytes(lines[0])
            # A changed payload must not replay while completion is unrecorded.
            changed_request = self.base(dry_run=False, write_authorized=True)
            changed_request["content"] = "conteúdo diferente não deve ser gravado\n"
            request.write_text(json.dumps(changed_request), encoding="utf-8")
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("reconciliação manual obrigatória", second.stderr)
            self.assertEqual((root / "artifacts/result.txt").read_text(encoding="utf-8"), "resultado validável\n")
            remaining = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(remaining), 1)
            self.assertEqual(remaining[0]["status"], "write_intent")


    def test_completion_audit_failure_after_replace_blocks_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = root / "request.json"
            request.write_text(json.dumps(self.base(
                dry_run=False, write_authorized=True
            )), encoding="utf-8")
            injected_failure = r"""
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[3])
import promptaria_executor as executor
root = Path(sys.argv[1])
registry = executor.load_json(Path(sys.argv[2]))
payload = {
    "operation_id": "test-op-001",
    "operation": "write_text",
    "destination": "artifacts/result.txt",
    "content": "resultado validável\n",
    "dry_run": False,
    "write_authorized": True,
}
original = executor.append_audit
calls = 0
def fail_completion(state_fd, audit_fd, record):
    global calls
    calls += 1
    if calls == 2:
        raise OSError("injected completion-audit failure")
    return original(state_fd, audit_fd, record)
executor.append_audit = fail_completion
try:
    executor.execute(payload, root, registry, "test-op-001")
except OSError as exc:
    if "injected completion-audit failure" not in str(exc):
        raise
else:
    raise SystemExit("expected injected failure")
"""
            interrupted = subprocess.run(
                [sys.executable, "-c", injected_failure, str(root),
                 str(PERMISSIONS), str(EXECUTOR.parent)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(interrupted.returncode, 0, interrupted.stderr)
            destination = root / "artifacts/result.txt"
            self.assertEqual(destination.read_text(encoding="utf-8"), "resultado validável\n")
            audit = root / ".promptaria/audit.jsonl"
            records = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([record["status"] for record in records], ["write_intent"])

            # A normal retry with the same ID must not overwrite the durable result.
            changed = self.base(
                dry_run=False, write_authorized=True,
                content="novo conteúdo não autorizado por reconciliação\n",
            )
            request.write_text(json.dumps(changed), encoding="utf-8")
            replay = subprocess.run(
                [sys.executable, str(EXECUTOR), "--request", str(request),
                 "--repo-root", str(root), "--permissions", str(PERMISSIONS),
                 "--confirm-operation", "test-op-001"],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(replay.returncode, 0)
            self.assertIn("reconciliação manual obrigatória", replay.stderr)
            self.assertEqual(destination.read_text(encoding="utf-8"), "resultado validável\n")
            records_after = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([record["status"] for record in records_after], ["write_intent"])

    def test_rejects_symlink_in_intermediate_destination_component(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            (root / "artifacts").symlink_to(outside, target_is_directory=True)
            request = root / "request.json"
            request.write_text(json.dumps(self.base()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(EXECUTOR), "--request", str(request),
                 "--repo-root", str(root), "--permissions", str(PERMISSIONS)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse((outside / "result.txt").exists())

    def test_authorized_write_uses_pinned_directory_descriptor(self):
        root, proc = self.run_executor(
            self.base(dry_run=False, write_authorized=True),
            "--confirm-operation", "test-op-001",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "executed")
        self.assertEqual(
            hashlib.sha256((root / "artifacts/result.txt").read_bytes()).hexdigest(),
            result["result_content_sha256"],
        )


    def test_external_audit_anchor_detects_truncation_and_allows_appends(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "repo"
            external = base / "external-store"
            root.mkdir()
            external.mkdir()
            request = root / "request.json"
            audit = root / ".promptaria/audit.jsonl"
            anchor = external / "promptaria-anchor.json"
            anchor_script = ROOT / "scripts" / "promptaria_audit_anchor.py"

            def run_operation(operation_id):
                request.write_text(json.dumps(self.base(operation_id=operation_id)), encoding="utf-8")
                return subprocess.run(
                    [sys.executable, str(EXECUTOR), "--request", str(request),
                     "--repo-root", str(root), "--permissions", str(PERMISSIONS)],
                    capture_output=True, text=True, encoding="utf-8",
                )

            first = run_operation("anchor-op-001")
            self.assertEqual(first.returncode, 0, first.stderr)
            create = subprocess.run(
                [sys.executable, str(anchor_script), "--mode", "create",
                 "--audit", str(audit), "--anchor", str(anchor), "--repo-root", str(root)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            self.assertTrue(anchor.exists())

            second = run_operation("anchor-op-002")
            self.assertEqual(second.returncode, 0, second.stderr)
            verify = subprocess.run(
                [sys.executable, str(anchor_script), "--mode", "verify",
                 "--audit", str(audit), "--anchor", str(anchor), "--repo-root", str(root)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(verify.returncode, 0, verify.stderr)
            self.assertTrue(json.loads(verify.stdout)["verified"])

            audit.write_text("", encoding="utf-8")
            truncated = subprocess.run(
                [sys.executable, str(anchor_script), "--mode", "verify",
                 "--audit", str(audit), "--anchor", str(anchor), "--repo-root", str(root)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(truncated.returncode, 0)
            self.assertIn("vazia", truncated.stderr)

    def test_audit_anchor_tool_rejects_symlink_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "repo"
            external = base / "external-store"
            root.mkdir()
            external.mkdir()
            script = ROOT / "scripts" / "promptaria_audit_anchor.py"
            real_audit = external / "real-audit.jsonl"
            real_audit.write_text("{}\n", encoding="utf-8")
            audit_link = root / "audit-link.jsonl"
            audit_link.symlink_to(real_audit)
            anchor = external / "anchor.json"
            create = subprocess.run(
                [sys.executable, str(script), "--mode", "create",
                 "--audit", str(audit_link), "--anchor", str(anchor), "--repo-root", str(root)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(create.returncode, 0)
            self.assertFalse(anchor.exists())

            anchor_target = external / "anchor-target.json"
            anchor_target.write_text('{"schema_version": 1}', encoding="utf-8")
            anchor_link = external / "anchor-link.json"
            anchor_link.symlink_to(anchor_target)
            verify = subprocess.run(
                [sys.executable, str(script), "--mode", "verify",
                 "--audit", str(real_audit), "--anchor", str(anchor_link), "--repo-root", str(root)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(verify.returncode, 0)
            self.assertIn("link simbólico", verify.stderr)

    def test_external_audit_anchor_must_be_outside_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = root / "request.json"
            request.write_text(json.dumps(self.base()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(EXECUTOR), "--request", str(request),
                 "--repo-root", str(root), "--permissions", str(PERMISSIONS)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "promptaria_audit_anchor.py"),
                 "--mode", "create", "--audit", str(root / ".promptaria/audit.jsonl"),
                 "--anchor", str(root / "anchor.json"), "--repo-root", str(root)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fora do repositório", result.stderr)

    def test_rejects_audit_log_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            external = root / "external-audit.jsonl"
            external.write_text("", encoding="utf-8")
            state = root / ".promptaria"
            state.mkdir()
            (state / "audit.jsonl").symlink_to(external)
            request = root / "request.json"
            request.write_text(json.dumps(self.base()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(EXECUTOR), "--request", str(request),
                 "--repo-root", str(root), "--permissions", str(PERMISSIONS)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("link simbólico", proc.stderr)
            self.assertEqual(external.read_text(encoding="utf-8"), "")

    def test_rejects_state_directory_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            external = root / "external-state"
            external.mkdir()
            (root / ".promptaria").symlink_to(external, target_is_directory=True)
            request = root / "request.json"
            request.write_text(json.dumps(self.base()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(EXECUTOR), "--request", str(request),
                 "--repo-root", str(root), "--permissions", str(PERMISSIONS)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("link simbólico", proc.stderr)


    def test_state_and_audit_permissions_are_restricted(self):
        root, proc = self.run_executor(self.base())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        state = root / ".promptaria"
        audit = state / "audit.jsonl"
        lock = state / "executor.lock"
        self.assertEqual(state.stat().st_mode & 0o777, 0o700)
        self.assertEqual(audit.stat().st_mode & 0o777, 0o600)
        self.assertEqual(lock.stat().st_mode & 0o777, 0o600)

    def test_rejects_lock_file_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / ".promptaria"
            state.mkdir(mode=0o700)
            external = root / "external-lock"
            external.write_text("", encoding="utf-8")
            (state / "executor.lock").symlink_to(external)
            request = root / "request.json"
            request.write_text(json.dumps(self.base()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(EXECUTOR), "--request", str(request),
                 "--repo-root", str(root), "--permissions", str(PERMISSIONS)],
                capture_output=True, text=True, encoding="utf-8",
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(external.read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
