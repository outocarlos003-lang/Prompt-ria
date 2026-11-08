#!/usr/bin/env python3
"""Audit instrument files against the manifest and registry; never activates instruments."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char)).casefold()
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"[\s-]+", " ", value).strip()


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Não foi possível ler JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} deve conter um objeto JSON.")
    return value


def entries_by_path(payload: dict, source: str, errors: list[str]) -> dict[str, dict]:
    entries = payload.get("instruments", [])
    if not isinstance(entries, list):
        errors.append(f"{source}: 'instruments' deve ser uma lista.")
        return {}
    result: dict[str, dict] = {}
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{source}: entrada {index} não é objeto.")
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"{source}: entrada {index} sem path válido.")
            continue
        if path in result:
            errors.append(f"{source}: path duplicado: {path}")
        result[path] = entry
        item_id = entry.get("id")
        if isinstance(item_id, str) and item_id:
            if item_id in seen_ids:
                errors.append(f"{source}: id duplicado: {item_id}")
            seen_ids.add(item_id)
    return result


def audit(instruments_dir: Path, manifest_path: Path, registry_path: Path) -> dict:
    errors: list[str] = []
    manifest = load_json(manifest_path)
    registry = load_json(registry_path)
    manifest_entries = entries_by_path(manifest, "manifest", errors)
    registry_entries = entries_by_path(registry, "registry", errors)

    files = []
    for path in sorted(instruments_dir.rglob("*.md")):
        relative = path.relative_to(instruments_dir.parent).as_posix()
        content = path.read_text(encoding="utf-8")
        match = re.search(r"(?m)^#\s+(.+?)\s*$", content)
        title = match.group(1).strip() if match else ""
        if not title:
            errors.append(f"{relative}: título ausente (esperado cabeçalho Markdown #).")
        manifest_entry = manifest_entries.get(relative)
        registry_entry = registry_entries.get(relative)
        if manifest_entry is None:
            errors.append(f"{relative}: arquivo não registrado em tests/manifest.json.")
        elif title and normalize(str(manifest_entry.get("title", ""))) != normalize(title):
            errors.append(f"{relative}: título do manifesto diverge do título do arquivo.")
        if registry_entry is None:
            errors.append(f"{relative}: arquivo não registrado em config/instrument-registry.json.")
        elif title and normalize(str(registry_entry.get("title", ""))) != normalize(title):
            errors.append(f"{relative}: título do registry diverge do título do arquivo.")
        files.append({
            "path": relative,
            "title": title or None,
            "manifest_status": "registered" if manifest_entry else "missing",
            "registry_status": "registered" if registry_entry else "missing",
            "activation_enabled": (
                registry_entry.get("activation", {}).get("enabled") is True
                if isinstance(registry_entry, dict) and isinstance(registry_entry.get("activation"), dict)
                else False
            ),
        })

    actual_paths = {item["path"] for item in files}
    for source, entries in (("manifest", manifest_entries), ("registry", registry_entries)):
        for registered_path in sorted(set(entries) - actual_paths):
            errors.append(f"{source}: caminho registrado sem arquivo Markdown: {registered_path}")

    return {
        "schema_version": 1,
        "classification_policy": {
            "registered": "arquivo existe e está referenciado no manifesto e no registry",
            "activation": "informativa; inventário não ativa nem executa instrumentos",
        },
        "summary": {
            "markdown_files": len(files),
            "manifest_entries": len(manifest_entries),
            "registry_entries": len(registry_entries),
            "errors": len(errors),
            "complete": not errors,
        },
        "instruments": files,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instruments", type=Path, default=Path("instruments"))
    parser.add_argument("--manifest", type=Path, default=Path("tests/manifest.json"))
    parser.add_argument("--registry", type=Path, default=Path("config/instrument-registry.json"))
    parser.add_argument("--output", type=Path, help="Arquivo JSON de saída; stdout se omitido.")
    parser.add_argument("--strict", action="store_true", help="Retorna código 1 se houver qualquer lacuna.")
    args = parser.parse_args()
    try:
        result = audit(args.instruments, args.manifest, args.registry)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 1 if args.strict and result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
