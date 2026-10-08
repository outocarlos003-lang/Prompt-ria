#!/usr/bin/env python3
"""Recupera conteúdo efetivo e produz pacote rastreável de execução."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


def visible_text(raw: str) -> str:
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return " ".join(html.unescape(raw).split())


def build(result: dict) -> dict:
    items = []
    for item in result.get("execution_plan", []):
        path = Path(item["instrument"])
        if not path.is_file():
            raise FileNotFoundError(f"instrumento não recuperável: {path}")
        raw = path.read_text(encoding="utf-8", errors="replace")
        items.append({
            "title": item["title"],
            "instrument_id": item.get("instrument_id"),
            "instrument": item["instrument"],
            "occurrences": item["occurrences"],
            "mode": item["mode"],
            "recovery": item.get("recovery", "github"),
            "identity_preserved": item.get("identity_preserved", True),
            "content_effective": item.get("content_effective", True),
            "content": visible_text(raw),
        })

    coordination = result.get("coordination", {})
    return {
        "schema_version": "2.0",
        "source_status": result.get("status"),
        "architecture_policy": result.get("architecture_policy", {}),
        "activation_rule": result.get("activation_rule", {}),
        "rule": result.get("rule", {}),
        "matched_occurrences": result.get("matched_occurrences", 0),
        "instruments": items,
        "matches": result.get("matches", []),
        "exceptions": result.get("exceptions", []),
        "coordination": coordination,
        "traceability": coordination.get("traceability", {}),
        "origin": coordination.get("parameters", {}).get("origin", {}),
        "destination": coordination.get("parameters", {}).get("destination", {}),
        "parameters": coordination.get("parameters", {}),
        "adaptation": coordination.get("adaptation", {}),
        "sequence": coordination.get("sequences", {}),
        "validation": coordination.get("validation", {}),
        "github_limits": coordination.get("github_limits", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="correfencia-execution-bundle.json")
    args = parser.parse_args()
    result = json.loads(Path(args.input).read_text(encoding="utf-8"))

    if result.get("status") != "ok":
        raise SystemExit("Resultado de correferência inválido; pacote não gerado.")

    bundle = build(result)
    Path(args.output).write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "instruments": len(bundle["instruments"]),
        "matched_occurrences": bundle["matched_occurrences"],
        "exceptions": len(bundle["exceptions"]),
        "traceability_occurrences": len(bundle["traceability"].get("occurrences", [])),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
