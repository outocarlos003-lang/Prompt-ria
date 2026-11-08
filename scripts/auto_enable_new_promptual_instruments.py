#!/usr/bin/env python3
"""Classify newly introduced Promptária instruments conservatively.

A new title containing "Instrumento promptual" is recoverable on demand by
default. Continuous automation is only classified when the source Markdown
contains the exact explicit override declaration; that exception remains
inactive and non-executable until separately configured.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

PROMPTUAL_MARKER = "instrumento promptual"
CONTINUOUS_OVERRIDE = "<!-- promptaria: continuous_automation: explicit -->"
MIRRORS = (
    "instrument-registry.json",
    "config/instrument-catalog.json",
    "instrument-catalog.json",
    "manifest.json",
    "tests/manifest.json",
)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).casefold()
    return re.sub(r"[^\w]+", " ", value, flags=re.UNICODE).strip()


def load_base_registry(root: Path, base_sha: str) -> dict[str, Any]:
    raw = subprocess.run(
        ["git", "show", f"{base_sha}:config/instrument-registry.json"],
        cwd=root, check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    data = json.loads(raw)
    if not isinstance(data.get("instruments"), list):
        raise ValueError("Registro da versão-base não contém instruments[] válido.")
    return data


def source_metadata(item: dict[str, Any], root: Path) -> tuple[str, str] | None:
    title = item.get("title")
    source = item.get("path")
    if not isinstance(title, str) or not isinstance(source, str) or not source.startswith("instruments/"):
        return None
    relative = Path(source)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Caminho de instrumento inseguro: {source}")
    path = root / relative
    if not path.is_file():
        raise ValueError(f"Fonte do novo instrumento inacessível: {source}")
    source_text = path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^#\s+(.+?)\s*$", source_text)
    if not match:
        raise ValueError(f"Instrumento sem título H1 canônico: {source}")
    canonical_title = match.group(1).strip()
    if normalize(canonical_title) != normalize(title):
        raise ValueError(f"Título do registro diverge do H1 em {source}")
    if PROMPTUAL_MARKER not in normalize(canonical_title):
        return None
    category = "continuous_automation" if CONTINUOUS_OVERRIDE in source_text else "recoverable_on_demand"
    basis = "explicit_source_declaration" if category == "continuous_automation" else "default_title_rule"
    return category, basis


def apply_classification(item: dict[str, Any], category: str, basis: str) -> None:
    item["category"] = category
    item["classification_basis"] = basis
    activation = item.get("activation")
    if not isinstance(activation, dict):
        activation = {}
        item["activation"] = activation
    ui = item.get("ui")
    if not isinstance(ui, dict):
        ui = {}
        item["ui"] = ui
    if category == "recoverable_on_demand":
        activation.update({"enabled": True, "status": "active", "mode": "on_demand_title"})
        ui["visible"] = True
    else:
        activation.update({"enabled": False, "status": "prepared_no_executor"})
        activation.pop("mode", None)
        ui["visible"] = False
    ui.setdefault("featured", False)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def activate_new_entries(root: Path, base_registry: dict[str, Any]) -> list[str]:
    registry_path = root / "config/instrument-registry.json"
    current = json.loads(registry_path.read_text(encoding="utf-8"))
    entries = current.get("instruments")
    if not isinstance(entries, list):
        raise ValueError("Registro atual não contém instruments[] válido.")
    base_ids = {
        item.get("id") for item in base_registry.get("instruments", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    classified: dict[str, tuple[str, str]] = {}
    by_id: dict[str, dict[str, Any]] = {}
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or item["id"] in base_ids:
            continue
        metadata = source_metadata(item, root)
        if metadata is None:
            continue
        category, basis = metadata
        apply_classification(item, category, basis)
        classified[item["id"]] = metadata
        by_id[item["id"]] = item
    if not classified:
        return []

    write_json(registry_path, current)
    for relative in MIRRORS:
        path = root / relative
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Espelho ausente ou inválido ({relative}): {exc}") from exc
        mirror_entries = payload.get("instruments")
        if not isinstance(mirror_entries, list):
            raise ValueError(f"{relative} não contém instruments[] válido.")
        mirror_by_id = {
            item.get("id"): item for item in mirror_entries
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        is_manifest = relative.endswith("manifest.json")
        for ident, (category, basis) in classified.items():
            mirror_item = mirror_by_id.get(ident)
            if mirror_item is None:
                if not is_manifest:
                    raise ValueError(f"Espelho {relative} não contém o novo instrumento {ident}.")
                source_item = by_id[ident]
                mirror_item = {
                    "id": ident,
                    "title": source_item["title"],
                    "path": source_item["path"],
                    "aliases": source_item.get("aliases", []),
                    "capabilities": [],
                }
                mirror_entries.append(mirror_item)
            mirror_item["category"] = category
            mirror_item["classification_basis"] = basis
            if not is_manifest:
                apply_classification(mirror_item, category, basis)
        write_json(path, payload)
    return sorted(classified)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-sha", required=True, help="SHA da versão-base do PR")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    base = load_base_registry(root, args.base_sha)
    classified = activate_new_entries(root, base)
    print(json.dumps({"classified_new_promptual_instruments": classified}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
