#!/usr/bin/env python3
"""Recupera o conteúdo dos instrumentos acionados e produz um pacote de execução."""
from __future__ import annotations

import argparse
import hashlib
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
    return {
        "schema_version": "2.0",
        "source_status": result.get("status"),
        "matched_occurrences": result.get("matched_occurrences", 0),
        "instruments": items,
        "coordination": result.get("coordination", {}),
        "traceability": result.get("coordination", {}).get("traceability", {}),
        "origin": result.get("coordination", {}).get("parameters", {}).get("origin", {}),
        "destination": result.get("coordination", {}).get("parameters", {}).get("destination", {}),
        "sequence": result.get("coordination", {}).get("sequence", []),
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
