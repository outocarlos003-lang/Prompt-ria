#!/usr/bin/env python3
"""Explicitly enable a fully registered instrument for site and title resolution."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "instrument-registry.json"
CATALOG = ROOT / "config" / "instrument-catalog.json"
EXECUTION_MAP = ROOT / "config" / "instrument-execution-map.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).casefold()
    return re.sub(r"[\W_]+", " ", value, flags=re.UNICODE).strip()


def validate_executor_evidence(item: dict, root: Path = ROOT) -> list[str]:
    """Require a matching, implemented specialized handler before activation."""
    map_path = root / "config" / "instrument-execution-map.json"
    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"mapa de execução indisponível ou inválido: {exc}"]

    mapped = data.get("instruments")
    if not isinstance(mapped, list):
        return ["mapa de execução inválido: instruments deve ser uma lista."]
    matches = [entry for entry in mapped if isinstance(entry, dict) and entry.get("id") == item.get("id")]
    if len(matches) != 1:
        return ["executor especializado deve estar mapeado exatamente uma vez para o ID."]
    entry = matches[0]
    errors = []
    for field in ("title", "path"):
        if entry.get(field) != item.get(field):
            errors.append(f"identidade do mapa de execução diverge no campo {field}.")
    executor = entry.get("specialized_executor")
    handler = entry.get("specialized_handler")
    if not isinstance(executor, str) or not executor.strip():
        errors.append("executor especializado não declarado.")
    else:
        executor_path = Path(executor)
        if executor_path.is_absolute() or ".." in executor_path.parts:
            errors.append("caminho do executor especializado não é seguro.")
        elif not (root / executor_path).is_file():
            errors.append("arquivo do executor especializado não existe.")
        elif not isinstance(handler, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", handler):
            errors.append("handler especializado não declarado ou inválido.")
        elif not re.search(
            rf"(?m)^def\s+{re.escape(handler)}\s*\(", (root / executor_path).read_text(encoding="utf-8")
        ):
            errors.append("handler declarado não existe no código do executor.")
    if entry.get("specialized_execution_status") != "implemented":
        errors.append("executor especializado não está marcado como implemented.")
    if entry.get("side_effects_authorized_by_title") is not False:
        errors.append("o mapa deve declarar side_effects_authorized_by_title=false.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="ID exato já registrado para o instrumento")
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = registry.get("instruments", [])
    matches = [item for item in entries if item.get("id") == args.id]
    if len(matches) != 1:
        raise SystemExit(f"ID deve existir exatamente uma vez no registro: {args.id}")
    item = matches[0]
    required = ("id", "title", "path", "aliases", "keywords", "functions", "relations", "operations", "ui")
    missing = [field for field in required if field not in item or item[field] in (None, "", [])]
    if missing:
        raise SystemExit("Ativação recusada; metadados ausentes: " + ", ".join(missing))
    source = (ROOT / item["path"]).resolve()
    try:
        source.relative_to(ROOT.resolve())
    except ValueError:
        raise SystemExit("Ativação recusada: caminho fora do repositório.")
    if not source.is_file():
        raise SystemExit(f"Ativação recusada: arquivo não encontrado: {item['path']}")
    text = source.read_text(encoding="utf-8")
    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    if not title_match or normalize(title_match.group(1)) != normalize(item["title"]):
        raise SystemExit("Ativação recusada: título do primeiro H1 diverge do registro.")
    executor_errors = validate_executor_evidence(item)
    if executor_errors:
        raise SystemExit("Ativação recusada; evidência de executor insuficiente: " + " ".join(executor_errors))
    for other in entries:
        if other["id"] != item["id"] and other.get("activation", {}).get("enabled") is True:
            if normalize(other.get("title", "")) == normalize(item["title"]):
                raise SystemExit(f"Ativação recusada: título canônico conflita com {other['id']}.")
    item["activation"] = {"enabled": True, "status": "active"}
    item.setdefault("ui", {})["visible"] = True
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_instrument_catalog.py")], cwd=ROOT, check=True)
    print(f"Instrumento habilitado para o site e correferência por título: {item['id']}")
    print("A alteração deve ser validada e publicada por commit/pull request; a ativação não autoriza execução externa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
