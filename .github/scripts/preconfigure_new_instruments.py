#!/usr/bin/env python3
"""Safely register newly added instruments as inactive, non-executable entries."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def slugify(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", normalize(value))).strip("-")


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Não foi possível ler {path}: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("instruments"), list):
        raise ValueError(f"Catálogo inválido em {path}: 'instruments' deve ser uma lista.")
    return value


def main() -> int:
    root = Path.cwd()
    instruments_dir = root / "instruments"
    registry_path = root / "config" / "instrument-registry.json"
    manifest_path = root / "tests" / "manifest.json"
    if not instruments_dir.is_dir() or not registry_path.is_file() or not manifest_path.is_file():
        print("Estrutura do repositório incompleta; nenhum arquivo foi alterado.", file=sys.stderr)
        return 2
    try:
        registry = read_json(registry_path)
        manifest = read_json(manifest_path)
        registry_entries = registry["instruments"]
        manifest_entries = manifest["instruments"]
        if any(not isinstance(x, dict) for x in registry_entries + manifest_entries):
            raise ValueError("Catálogos contêm entradas que não são objetos.")
        by_path = {x.get("path"): x for x in registry_entries if isinstance(x.get("path"), str)}
        manifest_by_path = {x.get("path"): x for x in manifest_entries if isinstance(x.get("path"), str)}
        existing_titles = {}
        for item in registry_entries:
            title = item.get("title")
            if isinstance(title, str) and title.strip():
                existing_titles.setdefault(normalize(title), []).append(item)
        discovered = []
        for path in sorted(instruments_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
            if not match:
                continue
            title = match.group(1).strip()
            relpath = path.relative_to(root).as_posix()
            if relpath in by_path:
                continue
            norm_title = normalize(title)
            if norm_title in existing_titles:
                print(f"Título canônico duplicado: {title}", file=sys.stderr)
                return 1
            instrument_id = slugify(path.stem) or slugify(title)
            if any(item.get("id") == instrument_id for item in registry_entries):
                print(f"ID gerado duplicado: {instrument_id}", file=sys.stderr)
                return 1
            discovered.append({
                "id": instrument_id,
                "title": title,
                "path": relpath,
                "aliases": [],
                "keywords": [],
                "functions": [],
                "files": [relpath],
                "relations": [],
                "operations": [],
                "ui": {"node_id": f"instrument:{instrument_id}", "visible": False, "featured": False},
                "activation": {"enabled": False, "status": "prepared_no_executor"},
            })
        if not discovered:
            print("Nenhum instrumento novo; catálogos já estão sincronizados.")
            return 0
        # Validate all collisions before touching either file.
        registry["instruments"] = registry_entries + discovered
        for item in discovered:
            manifest_item = {
                "id": item["id"], "title": item["title"], "path": item["path"],
                "aliases": [], "capabilities": [],
            }
            manifest_entries.append(manifest_item)
        serialized_registry = json.dumps(registry, ensure_ascii=False, indent=2) + "\n"
        serialized_manifest = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        registry_path.write_text(serialized_registry, encoding="utf-8")
        manifest_path.write_text(serialized_manifest, encoding="utf-8")
        print(f"Pré-configurados {len(discovered)} instrumento(s); permanecem não executáveis até revisão explícita.")
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
