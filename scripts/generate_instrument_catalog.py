#!/usr/bin/env python3
"""Generate the Promptária instrument catalog from the canonical registry."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "instruments"
REGISTRY = ROOT / "config" / "instrument-registry.json"
TARGET = ROOT / "config" / "instrument-catalog.json"


def title_for(path: Path) -> str:
    """Return the first canonical Markdown H1 for a source file."""
    import re
    match = re.search(r"(?m)^#\s+(.+?)\s*$", path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"Missing canonical H1 in {path}")
    return match.group(1).strip()


def validate_registry() -> None:
    """Fail closed unless registry identity is internally consistent."""
    sys.path.insert(0, str(ROOT))
    from scripts.promptaria_registry_audit import audit
    result = audit(REGISTRY, ROOT)
    if not result["valid"]:
        details = "\n".join(f"- {error}" for error in result["errors"])
        raise SystemExit("registry audit failed; catalog generation aborted:\n" + details)


def main() -> None:
    validate_registry()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = registry["instruments"]
    physical = {path.relative_to(ROOT).as_posix() for path in SOURCE.glob("*.md")}
    registered = {item["path"] for item in entries}
    if physical != registered:
        missing = sorted(physical - registered)
        stale = sorted(registered - physical)
        raise SystemExit(f"registry/catalog mismatch; missing={missing}; stale={stale}")

    catalog = {
        "schema_version": 2,
        "generated_by": "scripts/generate_instrument_catalog.py",
        "source_glob": "instruments/*.md",
        "registry": "config/instrument-registry.json",
        "repository": "outocarlos003-lang/Prompt-ria",
        "instruments": [
            {
                "id": item["id"],
                "path": item["path"],
                "title": item["title"],
                "aliases": item["aliases"],
                "keywords": item["keywords"],
                "functions": item["functions"],
                "relations": item["relations"],
                "operations": item["operations"],
                "ui": item["ui"],
                "activation": item["activation"],
            }
            for item in sorted(entries, key=lambda entry: entry["path"])
        ],
    }
    TARGET.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(entries)} instruments")


if __name__ == "__main__":
    main()
