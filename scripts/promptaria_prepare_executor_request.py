#!/usr/bin/env python3
"""Prepare an explicitly supplied executor request for CI simulation only."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


def atomic_json(path: Path, payload: dict) -> None:
    """Write generated workflow data atomically in the destination directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def prepare(raw: str) -> dict | None:
    if not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"executor_request_json não é JSON válido: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("executor_request_json deve ser um objeto JSON.")
    required = {"operation_id", "operation", "destination", "content"}
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError("Campos obrigatórios ausentes: " + ", ".join(missing))
    # CI is intentionally validation-only. Never accept authorization flags from input.
    return {
        "operation_id": payload["operation_id"],
        "operation": payload["operation"],
        "destination": payload["destination"],
        "content": payload["content"],
        "dry_run": True,
        "write_authorized": False,
    }


def main() -> None:
    raw = os.environ.get("EXECUTOR_REQUEST_JSON", "")
    try:
        payload = prepare(raw)
    except ValueError as exc:
        raise SystemExit(str(exc))
    output = Path("executor-request.json")
    if payload is None:
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
                stream.write("enabled=false\n")
        print("Nenhuma operação estruturada solicitada; executor ignorado.")
        return
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
            stream.write("enabled=true\n")
    print("Pedido estruturado preparado para simulação; autorização real removida.")


if __name__ == "__main__":
    main()
