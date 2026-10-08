#!/usr/bin/env python3
"""Recupera o conteúdo dos instrumentos acionados e produz um pacote de execução."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def visible_text(raw: str) -> str:
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return " ".join(html.unescape(raw).split())


def build(result: dict) -> dict:
    base = Path(".")
    items = []
    for item in result.get("execution_plan", []):
        path = Path(item["instrument"])
        raw = path.read_text(encoding="utf-8", errors="replace")
        items.append({
            "title": item["title"],
            "instrument": item["instrument"],
            "occurrences": item["occurrences"],
            "mode": item["mode"],
            "content": visible_text(raw),
        })
    return {
        "schema_version": "1.0",
        "source_status": result.get("status"),
        "matched_occurrences": result.get("matched_occurrences", 0),
        "instruments": items,
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
    import re
    raise SystemExit(main())
