#!/usr/bin/env python3
"""Enable only newly introduced Promptária instruments named INSTRUMENTO PROMPTUAL.

The base-branch registry is the historical boundary: disabled instruments already
present there are never changed by this automation.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

PHRASE = "instrumento promptual"
MIRRORS = (
    "config/instrument-registry.json",
    "instrument-registry.json",
    "config/instrument-catalog.json",
    "instrument-catalog.json",
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


def is_named_promptual_instrument(item: dict[str, Any], root: Path) -> bool:
    title = item.get("title", "")
    if isinstance(title, str) and PHRASE in normalize(title):
        return True
    source = item.get("path")
    if not isinstance(source, str) or not source.startswith("instruments/"):
        return False
    path = root / source
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return PHRASE in normalize(line[2:].strip())
    return False


def activate_new_entries(root: Path, base_registry: dict[str, Any]) -> list[str]:
    registry_path = root / "config/instrument-registry.json"
    current = json.loads(registry_path.read_text(encoding="utf-8"))
    base_ids = {
        item.get("id") for item in base_registry.get("instruments", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    new_matches = [
        item for item in current.get("instruments", [])
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item["id"] not in base_ids
        and is_named_promptual_instrument(item, root)
    ]
    if not new_matches:
        return []

    activated_ids: list[str] = []
    for item in new_matches:
        activation = item.get("activation")
        if not isinstance(activation, dict):
            activation = {}
            item["activation"] = activation
        activation["enabled"] = True
        activation["status"] = "active"
        activated_ids.append(item["id"])

    for relative in MIRRORS:
        path = root / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        by_id = {
            item.get("id"): item for item in data.get("instruments", [])
            if isinstance(item, dict)
        }
        for ident in activated_ids:
            mirror_item = by_id.get(ident)
            if mirror_item is None:
                if relative.endswith("instrument-registry.json"):
                    raise ValueError(f"Espelho de registro não contém novo instrumento: {ident}")
                continue
            activation = mirror_item.get("activation")
            if not isinstance(activation, dict):
                activation = {}
                mirror_item["activation"] = activation
            activation["enabled"] = True
            activation["status"] = "active"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sorted(activated_ids)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-sha", required=True, help="SHA da versão-base do PR")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    base = load_base_registry(root, args.base_sha)
    activated = activate_new_entries(root, base)
    print(json.dumps({"automatically_activated_new_promptual_instruments": activated}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
