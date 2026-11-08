#!/usr/bin/env python3
"""Recover an auxiliary Promptária protocol by exact canonical title or ID.

Auxiliary protocols remain enabled but are excluded from the operational
registry, catalog, manifest, execution map, and automatic title resolver.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path("auxiliary-protocols/registry.json")

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).casefold()
    return re.sub(r"[\W_]+", " ", value, flags=re.UNICODE).strip()

def recover_protocol(root: Path, *, instrument_id: str | None = None, title: str | None = None) -> dict[str, Any]:
    if bool(instrument_id) == bool(title):
        raise ValueError("Informe exatamente um identificador ou título canônico.")
    data = json.loads((root / REGISTRY_PATH).read_text(encoding="utf-8"))
    protocols = data.get("protocols")
    if not isinstance(protocols, list):
        raise ValueError("Registro auxiliar inválido: protocols deve ser uma lista.")
    if instrument_id:
        matches = [p for p in protocols if p.get("id") == instrument_id]
    else:
        key = normalize(title or "")
        matches = [p for p in protocols if normalize(p.get("title", "")) == key]
    if len(matches) != 1:
        raise LookupError("Protocolo auxiliar não encontrado de forma inequívoca.")
    item = matches[0]
    if item.get("operational_membership") is not False:
        raise ValueError("O registro não declara exclusão da contabilização operacional.")
    if item.get("activation", {}).get("enabled") is not True:
        raise ValueError("O protocolo auxiliar não está habilitado.")
    relative = Path(item.get("path", ""))
    if relative.is_absolute() or ".." in relative.parts or not item.get("path", "").startswith("auxiliary-protocols/"):
        raise ValueError("Caminho auxiliar inválido.")
    content = (root / relative).read_text(encoding="utf-8")
    first_h1 = next((line[2:].strip() for line in content.splitlines() if line.startswith("# ")), None)
    if first_h1 != item.get("title"):
        raise ValueError("O título da fonte integral diverge do registro auxiliar.")
    return {"id": item["id"], "title": item["title"], "path": relative.as_posix(),
            "activation": item["activation"], "operational_membership": False, "content": content}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--id", dest="instrument_id")
    selector.add_argument("--title")
    args = parser.parse_args()
    result = recover_protocol(ROOT, instrument_id=args.instrument_id, title=args.title)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
