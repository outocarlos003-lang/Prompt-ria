#!/usr/bin/env python3
"""Recupera o conteúdo dos instrumentos acionados e produz um pacote de execução."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path


def visible_text(raw: str) -> str:
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return " ".join(html.unescape(raw).split())


def current_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""

def build(result: dict) -> dict:
    if result.get("status") != "ok":
        raise ValueError("resultado não validado; rastreio não pode ser materializado")
    demand_id = result.get("demand_id")
    manifest_sha256 = result.get("manifest_sha256")
    if not demand_id or not manifest_sha256:
        raise ValueError("demand_id e manifest_sha256 são obrigatórios para rastreio")
    coordination = result.get("coordination", {})
    origin = coordination.get("parameters", {}).get("origin", {})
    destination = coordination.get("parameters", {}).get("destination", {})
    if origin.get("status") != "resolved":
        raise ValueError("origem não determinada; execução bloqueada")
    if destination.get("status") != "resolved":
        raise ValueError("destino não determinado; execução bloqueada")
    source_commit = current_commit()
    if not source_commit:
        raise ValueError("commit de origem indisponível; execução bloqueada")
    trace_id = "TRACE-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12]
    items = []
    for item in result.get("execution_plan", []):
        if not item.get("identity_verified", True):
            raise ValueError(f"identidade não verificada: {item.get('title')}")
        path = Path(item["instrument"])
        raw = path.read_text(encoding="utf-8", errors="replace")
        content_sha256 = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        items.append({
            "instrument_id": item.get("instrument_id"),
            "title": item["title"],
            "instrument": item["instrument"],
            "canonical_path": item.get("canonical_path"),
            "identity_verified": True,
            "content_sha256": content_sha256,
            "occurrences": item["occurrences"],
            "mode": item["mode"],
            "content": visible_text(raw),
        })
    trace = {
        "trace_id": trace_id,
        "demand_id": demand_id,
        "manifest_sha256": manifest_sha256,
        "source_commit": source_commit,
        "state": "identity_verified",
        "operation": "coordinated_promptaria_execution",
        "origin": origin,
        "participants": [
            {
                "instrument_id": item.get("instrument_id"),
                "instrument_title": item["title"],
                "instrument_path": item["canonical_path"],
                "content_sha256": item["content_sha256"],
                "identity_verified": item["identity_verified"],
            }
            for item in items
        ],
        "artifacts": [],
        "destination": destination,
        "references": result.get("coordination", {}).get("references", []),
        "validation": {
            "status": "pending_final_validation",
            "fail_closed": True,
            "identity_verified": all(item["identity_verified"] for item in items),
        },
        "result": {
            "status": "ready",
            "materialized": False,
        },
    }
    return {
        "schema_version": "3.0",
        "source_status": result.get("status"),
        "matched_occurrences": result.get("matched_occurrences", 0),
        "instruments": items,
        "coordination": result.get("coordination", {}),
        "traceability": trace,
        "trace": trace,
        "origin": origin,
        "destination": destination,
        "sequence": result.get("coordination", {}).get("sequence", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="correfencia-execution-bundle.json")
    args = parser.parse_args()
    result = json.loads(Path(args.input).read_text(encoding="utf-8"))
    bundle = build(result)
    Path(args.output).write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "ok",
        "instruments": len(bundle["instruments"]),
        "matched_occurrences": bundle["matched_occurrences"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
