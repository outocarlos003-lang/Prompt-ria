#!/usr/bin/env python3
"""Explicitly recover an enabled auxiliary protocol without operational selection."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "auxiliary-protocols" / "registry.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char)).casefold()
    value = re.sub(r"[\u200b-\u200f\ufeff]", "", value)
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"[\s-]+", " ", value).strip()


def resolve(reference: str) -> dict:
    raw = reference.strip()
    if not raw:
        raise SystemExit("Referência vazia.")
    selector = "exact_title_or_alias"
    if raw.casefold().startswith("instrument_id:"):
        key, selector = raw.split(":", 1)[1].strip(), "explicit_id"
        field = "id"
    elif raw.casefold().startswith("instrument_path:"):
        key, selector = raw.split(":", 1)[1].strip(), "explicit_path"
        field = "path"
    else:
        key, field = raw, None

    try:
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Registro auxiliar inválido ou inacessível: {exc}") from exc
    if payload.get("scope") != "auxiliary_protocols":
        raise SystemExit("Registro recusado: escopo auxiliar não confirmado.")
    if payload.get("membership_policy", {}).get("operational_member") is not False:
        raise SystemExit("Registro recusado: política de não pertencimento operacional ausente.")

    entries = payload.get("instruments")
    if not isinstance(entries, list):
        raise SystemExit("Registro auxiliar deve conter instruments como lista.")
    normalized = normalize(key)
    matches = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        values = [item.get(field)] if field else [item.get("id"), item.get("title"), item.get("path"), *item.get("aliases", [])]
        if any(isinstance(value, str) and normalize(value) == normalized for value in values):
            matches.append(item)
    if len(matches) != 1:
        raise SystemExit("Referência auxiliar não encontrada." if not matches else "Referência auxiliar ambígua; use instrument_id.")
    item = matches[0]
    activation = item.get("activation")
    if not isinstance(activation, dict) or activation.get("enabled") is not True:
        raise SystemExit("Protocolo auxiliar não está habilitado; recuperação funcional recusada.")
    path = Path(item.get("path", ""))
    if path.is_absolute() or ".." in path.parts or not str(path).startswith("auxiliary-protocols/"):
        raise SystemExit("Caminho auxiliar inválido.")
    source_path = (ROOT / path).resolve()
    try:
        source_path.relative_to((ROOT / "auxiliary-protocols").resolve())
        content = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise SystemExit(f"Fonte auxiliar indisponível ou inválida: {exc}") from exc
    heading = next((line[2:].strip() for line in content.splitlines() if line.startswith("# ")), None)
    if heading != item.get("title"):
        raise SystemExit("Título canônico divergente da fonte auxiliar.")
    return {
        "schema_version": 1,
        "instrument_id": item["id"],
        "title": item["title"],
        "path": item["path"],
        "membership": "auxiliary",
        "operational_member": False,
        "operational_counted": False,
        "automatic_selection": False,
        "explicit_resolution": True,
        "activation": activation,
        "resolution": {"mode": selector, "reference": raw},
        "source_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "content": content,
        "execution_status": "source_recovered_for_explicit_application",
        "external_side_effects": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, help="Exact title, alias, ID, instrument_id:ID or instrument_path:PATH")
    parser.add_argument("--output", type=Path, help="Optional JSON output path; stdout when omitted")
    args = parser.parse_args()
    result = resolve(args.reference)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
