#!/usr/bin/env python3
"""Safely register newly added instruments with conservative category defaults."""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

# An explicit source-file declaration is the only opt-out from the title rule.
CONTINUOUS_OVERRIDE = "<!-- promptaria: continuous_automation: explicit -->"
PROMPTUAL_TITLE_MARKER = "instrumento promptual"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def slugify(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", normalize(value))).strip("-")


def classify_new_instrument(title: str, source_text: str) -> tuple[str | None, str | None]:
    """Apply the mandatory on-demand default to new 'Instrumento promptual' titles."""
    if PROMPTUAL_TITLE_MARKER not in normalize(title):
        return None, None
    if CONTINUOUS_OVERRIDE in source_text:
        return "continuous_automation", "explicit_source_declaration"
    return "recoverable_on_demand", "default_title_rule"


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Não foi possível ler {path}: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("instruments"), list):
        raise ValueError(f"Catálogo inválido em {path}: 'instruments' deve ser uma lista.")
    return value


def write_json_pair(registry_path: Path, registry_text: str, manifest_path: Path, manifest_text: str) -> None:
    """Stage both catalog files and roll back the first replacement if the second fails."""
    targets = ((registry_path, registry_text), (manifest_path, manifest_text))
    originals = {path: path.read_bytes() for path, _ in targets}
    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for target, text in targets:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="",
                dir=target.parent, prefix=f".{target.name}.", suffix=".tmp",
                delete=False,
            ) as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
                staged[target] = Path(stream.name)
        for target, _ in targets:
            os.replace(staged[target], target)
            replaced.append(target)
    except OSError:
        for target in reversed(replaced):
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb", dir=target.parent, prefix=f".{target.name}.",
                    suffix=".rollback", delete=False,
                ) as stream:
                    stream.write(originals[target])
                    stream.flush()
                    os.fsync(stream.fileno())
                    rollback = Path(stream.name)
                os.replace(rollback, target)
            except OSError:
                pass
        raise
    finally:
        for temp_path in staged.values():
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


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
        existing_titles = {}
        for item in registry_entries:
            title = item.get("title")
            if isinstance(title, str) and title.strip():
                existing_titles.setdefault(normalize(title), []).append(item)
        discovered = []
        for path in sorted(instruments_dir.glob("*.md")):
            source_text = path.read_text(encoding="utf-8")
            match = re.search(r"(?m)^#\s+(.+?)\s*$", source_text)
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
            category, classification_basis = classify_new_instrument(title, source_text)
            entry = {
                "id": instrument_id,
                "title": title,
                "path": relpath,
                "aliases": [],
                "keywords": [],
                "functions": [],
                "files": [relpath],
                "relations": [],
                "operations": [],
                "ui": {
                    "node_id": f"instrument:{instrument_id}",
                    "visible": category == "recoverable_on_demand",
                    "featured": False,
                },
                "activation": {
                    "enabled": category == "recoverable_on_demand",
                    "status": "active" if category == "recoverable_on_demand" else "prepared_no_executor",
                    **({"mode": "on_demand_title"} if category == "recoverable_on_demand" else {}),
                },
            }
            if category:
                entry["category"] = category
                entry["classification_basis"] = classification_basis
            discovered.append(entry)
        if not discovered:
            print("Nenhum instrumento novo; catálogos já estão sincronizados.")
            return 0
        registry["instruments"] = registry_entries + discovered
        for item in discovered:
            manifest_item = {
                "id": item["id"], "title": item["title"], "path": item["path"],
                "aliases": [], "capabilities": [],
            }
            for field in ("category", "classification_basis"):
                if field in item:
                    manifest_item[field] = item[field]
            manifest_entries.append(manifest_item)
        serialized_registry = json.dumps(registry, ensure_ascii=False, indent=2) + "\n"
        serialized_manifest = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        write_json_pair(registry_path, serialized_registry, manifest_path, serialized_manifest)
        print(
            f"Pré-configurados {len(discovered)} instrumento(s); permanecem não executáveis "
            "até revisão explícita. Títulos com 'Instrumento promptual' foram classificados "
            "como recuperáveis sob demanda, salvo declaração expressa no próprio arquivo."
        )
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
