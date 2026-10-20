#!/usr/bin/env python3
"""Create/verify an external checkpoint for the Promptária audit hash chain."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(message)


def canonical(record: dict) -> bytes:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def read_chain(audit_path: Path) -> tuple[list[dict], list[str]]:
    # Open once with O_NOFOLLOW and validate the opened object, avoiding a
    # check-then-open symlink race on the audit log.
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(audit_path, flags)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                fail("Registro de auditoria ausente ou não regular.")
            with os.fdopen(fd, "rb") as stream:
                fd = -1
                raw = stream.read()
        finally:
            if fd >= 0:
                os.close(fd)
    except OSError as exc:
        fail(f"Não foi possível abrir a auditoria com segurança: {exc}")
    if raw and not raw.endswith(b"\n"):
        fail("Registro de auditoria truncado: última linha incompleta.")
    records: list[dict] = []
    hashes: list[str] = []
    previous = "0" * 64
    for number, line in enumerate(raw.splitlines(), start=1):
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            fail(f"JSON de auditoria inválido na linha {number}: {exc}")
        if not isinstance(record, dict) or not isinstance(record.get("audit_hash"), str):
            fail(f"Registro legado ou inválido na linha {number}; ancore apenas uma cadeia integralmente encadeada.")
        body = {key: value for key, value in record.items() if key != "audit_hash"}
        expected = hashlib.sha256(canonical(body)).hexdigest()
        if record.get("audit_prev_hash") != previous or record["audit_hash"] != expected:
            fail(f"Cadeia de auditoria inválida na linha {number}.")
        previous = record["audit_hash"]
        records.append(record)
        hashes.append(previous)
    if not records:
        fail("Auditoria vazia; não há cadeia para ancorar.")
    return records, hashes


def ensure_external(anchor_path: Path, repo_root: Path) -> Path:
    root = repo_root.resolve()
    parent = anchor_path.parent.resolve()
    resolved = parent / anchor_path.name
    if resolved == root or root in resolved.parents:
        fail("A âncora deve ficar fora do repositório.")
    if resolved.is_symlink():
        fail("Arquivo de âncora é link simbólico; operação bloqueada.")
    if not parent.is_dir():
        fail("O diretório da âncora deve existir e ser administrado separadamente.")
    return resolved


def create_anchor(audit_path: Path, anchor_path: Path, repo_root: Path) -> dict:
    anchor_path = ensure_external(anchor_path, repo_root)
    records, hashes = read_chain(audit_path)
    snapshot = {
        "schema_version": 1,
        "record_count": len(records),
        "audit_hash": hashes[-1],
        "anchored_at": datetime.now(timezone.utc).isoformat(),
    }
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    fd, temp_name = tempfile.mkstemp(prefix=".promptaria-anchor-", dir=str(anchor_path.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, anchor_path)
        dir_fd = os.open(anchor_path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return snapshot


def verify_anchor(audit_path: Path, anchor_path: Path, repo_root: Path) -> dict:
    anchor_path = ensure_external(anchor_path, repo_root)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(anchor_path, flags)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                fail("Âncora externa ausente ou não regular.")
            with os.fdopen(fd, "r", encoding="utf-8") as stream:
                fd = -1
                snapshot = json.load(stream)
        finally:
            if fd >= 0:
                os.close(fd)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Âncora externa ilegível ou insegura: {exc}")
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
        fail("Formato de âncora externa inválido.")
    count = snapshot.get("record_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        fail("Contagem da âncora externa inválida.")
    _, hashes = read_chain(audit_path)
    if len(hashes) < count:
        fail("A auditoria está truncada em relação à âncora externa.")
    if hashes[count - 1] != snapshot.get("audit_hash"):
        fail("A auditoria diverge da âncora externa no prefixo protegido.")
    return {"verified": True, "anchored_records": count, "current_records": len(hashes), "audit_hash": hashes[-1]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("create", "verify"), required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--anchor", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "create":
        result = create_anchor(args.audit, args.anchor, args.repo_root)
    else:
        result = verify_anchor(args.audit, args.anchor, args.repo_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
