#!/usr/bin/env python3
"""Controlled, auditable executor for explicitly authorized Promptária operations."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"JSON inválido ou inacessível ({path}): {exc}")
    if not isinstance(value, dict):
        fail(f"JSON inválido: {path} deve conter um objeto.")
    return value


def validate_relative_destination(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        fail("Destino obrigatório: informe um caminho relativo.")
    destination = value.strip()
    if "\\" in destination or destination.startswith("/") or re.match(r"^[A-Za-z]:", destination):
        fail("Destino recusado: use caminho relativo POSIX.")
    if any(ord(c) < 32 or ord(c) == 127 for c in destination):
        fail("Destino recusado: caracteres de controle.")
    parts = destination.split("/")
    if any(p in ("", ".", "..") or p.casefold() == ".git" for p in parts):
        fail("Destino recusado: segmento inválido ou .git.")
    return destination


def canonical_audit_json(record: dict) -> bytes:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def read_and_verify_audit(audit_path: Path) -> tuple[list[dict], str]:
    """Verify the hash chain and refuse symlink/non-regular audit files."""
    if audit_path.is_symlink():
        fail("Registro de auditoria é link simbólico; operação bloqueada.")
    if audit_path.exists() and not audit_path.is_file():
        fail("Registro de auditoria não é arquivo regular; operação bloqueada.")
    if not audit_path.exists():
        return [], "0" * 64
    try:
        raw = audit_path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            fail("Registro de auditoria truncado (última linha sem quebra); operação bloqueada.")
        lines = raw.splitlines(keepends=True)
        records: list[dict] = []
        previous_hash = "0" * 64
        chain_started = False
        for line_number, raw_line in enumerate(lines, start=1):
            if not raw_line.strip():
                fail(f"Registro de auditoria vazio na linha {line_number}; operação bloqueada.")
            record = json.loads(raw_line.decode("utf-8"))
            if not isinstance(record, dict):
                fail(f"Registro de auditoria inválido na linha {line_number}; operação bloqueada.")
            stored_hash = record.get("audit_hash")
            if stored_hash is None:
                if chain_started:
                    fail(f"Registro legado após início da cadeia na linha {line_number}; operação bloqueada.")
                previous_hash = hashlib.sha256(raw_line).hexdigest()
            else:
                chain_started = True
                supplied_previous = record.get("audit_prev_hash")
                body = {key: value for key, value in record.items() if key != "audit_hash"}
                expected_hash = hashlib.sha256(canonical_audit_json(body)).hexdigest()
                if supplied_previous != previous_hash or stored_hash != expected_hash:
                    fail(f"Integridade da cadeia de auditoria inválida na linha {line_number}; operação bloqueada.")
                previous_hash = stored_hash
            records.append(record)
        return records, previous_hash
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"Registro de auditoria ilegível; operação bloqueada por segurança: {exc}")


def append_audit(audit_path: Path, record: dict) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    _, previous_hash = read_and_verify_audit(audit_path)
    chained_record = dict(record)
    chained_record["audit_prev_hash"] = previous_hash
    chained_record["audit_hash"] = hashlib.sha256(canonical_audit_json(chained_record)).hexdigest()
    # O_NOFOLLOW closes the final-component symlink race on platforms that support it.
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(audit_path, flags, 0o600)
    except OSError as exc:
        fail(f"Não foi possível abrir o registro de auditoria com segurança: {exc}")
    with os.fdopen(fd, "ab") as stream:
        if not os.path.isfile(audit_path) or os.path.islink(audit_path):
            fail("Registro de auditoria deixou de ser arquivo regular; operação bloqueada.")
        stream.write(canonical_audit_json(chained_record) + bytes([10]))
        stream.flush()
        os.fsync(stream.fileno())


def reject_replayed_operation(audit_path: Path, operation_id: str) -> None:
    """Fail closed if the ledger is corrupt or this ID already completed a real write."""
    records, _ = read_and_verify_audit(audit_path)
    matching_statuses = {
        record.get("status")
        for record in records
        if record.get("operation_id") == operation_id
    }
    if "executed" in matching_statuses:
        fail("Operação recusada: este operation_id já concluiu uma escrita; use um ID novo.")
    if "write_intent" in matching_statuses:
        fail("Operação recusada: existe uma intenção de escrita sem conclusão auditada; reconciliação manual obrigatória.")


def _execute_locked(payload: dict, repo_root: Path, registry: dict, confirmation_id: str | None) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    operation_id = payload.get("operation_id")
    operation = payload.get("operation")
    dry_run = payload.get("dry_run", True)
    authorized = payload.get("write_authorized", False)
    destination = validate_relative_destination(payload.get("destination"))
    content = payload.get("content")

    if not isinstance(operation_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", operation_id):
        fail("operation_id inválido.")
    audit_path = repo_root / ".promptaria" / "audit.jsonl"
    reject_replayed_operation(audit_path, operation_id)
    if operation != "write_text":
        fail("Operação recusada: somente write_text está implementada.")
    if not isinstance(dry_run, bool) or not isinstance(authorized, bool):
        fail("dry_run e write_authorized devem ser booleanos JSON.")
    if not isinstance(content, str):
        fail("content deve ser texto.")
    encoded = content.encode("utf-8")
    max_bytes = registry.get("max_content_bytes", 0)
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0 or len(encoded) > max_bytes:
        fail("Conteúdo excede o limite permitido pelo registro de permissões.")
    if registry.get("schema_version") != 1 or operation not in registry.get("allowed_operations", []):
        fail("Operação não autorizada pelo registro de permissões.")
    prefixes = registry.get("allowed_destination_prefixes", [])
    if not isinstance(prefixes, list) or not any(
        isinstance(prefix, str) and prefix and destination.startswith(prefix)
        for prefix in prefixes
    ):
        fail("Destino fora dos prefixos autorizados.")
    if not dry_run and (authorized is not True or confirmation_id != operation_id):
        fail("Execução recusada: exige write_authorized=true e --confirm-operation igual ao operation_id.")
    if not dry_run and registry.get("execution_enabled") is not True:
        fail("Execução recusada: executor desabilitado no registro de permissões.")

    target = (repo_root / destination)
    # Reject symlinks in every existing destination component, not only the leaf.
    cursor = root = repo_root.resolve()
    for component in Path(destination).parts:
        cursor = cursor / component
        if cursor.is_symlink():
            fail("Destino recusado: links simbólicos em componentes do caminho não são permitidos.")
    # Resolve the parent to block escapes; path checks assume repository directories are not concurrently writable by an untrusted process.
    parent = target.parent.resolve()
    if parent != root and root not in parent.parents:
        fail("Destino recusado: o caminho resolvido sai do repositório.")
    if target.is_symlink():
        fail("Destino recusado: o arquivo-alvo é um link simbólico.")
    if target.exists() and not target.is_file():
        fail("Destino recusado: o destino existente não é um arquivo regular.")

    existing_hash = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
    result = {
        "schema_version": 1,
        "operation_id": operation_id,
        "operation": operation,
        "created_at": now,
        "destination": destination,
        "dry_run": dry_run,
        "authorized": authorized,
        "status": "simulated" if dry_run else "validated_pending_write",
        "content_sha256": hashlib.sha256(encoded).hexdigest(),
        "previous_content_sha256": existing_hash,
        "bytes": len(encoded),
        "executed": False,
    }

    if not dry_run:
        # Persist intent before mutation. An interrupted operation remains pending and fails closed on replay.
        intent = dict(result)
        intent["status"] = "write_intent"
        intent["executed"] = False
        append_audit(audit_path, intent)
        # Write atomically in the destination directory and avoid following target symlinks.
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=".promptaria-", dir=str(target.parent))
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            if target.is_symlink():
                fail("Destino recusado: o arquivo-alvo tornou-se um link simbólico.")
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        result["executed"] = True
        result["status"] = "executed"
        result["result_content_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        if result["result_content_sha256"] != result["content_sha256"]:
            result["status"] = "result_validation_failed"
            fail("Validação pós-escrita falhou: hash do resultado divergente.")

    append_audit(audit_path, result)
    return result



def execute(payload: dict, repo_root: Path, registry: dict, confirmation_id: str | None) -> dict:
    """Serialize operations so replay checks and audit appends cannot race each other."""
    state_dir = repo_root / ".promptaria"
    if state_dir.is_symlink():
        fail("Diretório de estado é link simbólico; operação bloqueada.")
    state_dir.mkdir(parents=True, exist_ok=True)
    if state_dir.is_symlink() or not state_dir.is_dir():
        fail("Diretório de estado não é um diretório regular; operação bloqueada.")
    lock_path = state_dir / "executor.lock"
    if lock_path.is_symlink():
        fail("Arquivo de bloqueio é link simbólico; operação bloqueada.")
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(lock_fd, "a+", encoding="utf-8") as lock_stream:
        fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
        try:
            return _execute_locked(payload, repo_root, registry, confirmation_id)
        finally:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--permissions", type=Path, default=Path(__file__).resolve().parents[1] / "config" / "promptaria_permissions.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--confirm-operation")
    args = parser.parse_args()

    payload = load_json(args.request)
    registry = load_json(args.permissions)
    result = execute(payload, args.repo_root.resolve(), registry, args.confirm_operation)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
