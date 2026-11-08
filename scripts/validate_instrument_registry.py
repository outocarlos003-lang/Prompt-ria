#!/usr/bin/env python3
"""Validate the canonical Promptária instrument registry and future-instrument contract."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "instrument-registry.json"
SOURCE = ROOT / "instruments"
REQUIRED = {"id", "title", "path", "aliases", "keywords", "functions", "files", "relations", "operations", "ui"}


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = data.get("instruments", [])
    if data.get("schema_version") != 2:
        raise SystemExit("instrument registry schema_version must be 2")
    if data.get("template_id") not in {item.get("id") for item in entries}:
        raise SystemExit("registry template_id must reference a registered instrument")

    ids = [item.get("id") for item in entries]
    paths = [item.get("path") for item in entries]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate instrument id")
    if len(paths) != len(set(paths)):
        raise SystemExit("duplicate instrument path")

    for item in entries:
        missing = sorted(REQUIRED - set(item))
        if missing:
            raise SystemExit(f"{item.get('id', '<unknown>')}: missing fields: {', '.join(missing)}")
        target = ROOT / item["path"]
        if not target.is_file():
            raise SystemExit(f"{item['id']}: missing instrument file {item['path']}")
        for field in ("aliases", "keywords", "functions", "files", "relations", "operations"):
            if not isinstance(item[field], list) or not item[field]:
                raise SystemExit(f"{item['id']}: {field} must be a non-empty list")
        if not item["ui"].get("node_id"):
            raise SystemExit(f"{item['id']}: ui.node_id is required")

    physical = {path.relative_to(ROOT).as_posix() for path in SOURCE.glob("*.md")}
    registered = set(paths)
    missing = sorted(physical - registered)
    orphaned = sorted(registered - physical)
    if missing:
        raise SystemExit("unregistered instrument files: " + ", ".join(missing))
    if orphaned:
        raise SystemExit("registry paths without files: " + ", ".join(orphaned))

    model = next(item for item in entries if item["id"] == data["template_id"])
    model_file = ROOT / model["path"]
    model_text = model_file.read_text(encoding="utf-8")
    for marker in ("id:", "title:", "aliases:", "keywords:"):
        if marker not in model_text:
            raise SystemExit(f"template is missing frontmatter marker {marker}")

    print(json.dumps({"status": "valid", "instrument_count": len(entries), "template_id": data["template_id"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
