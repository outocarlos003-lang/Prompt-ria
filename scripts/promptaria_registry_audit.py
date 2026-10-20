#!/usr/bin/env python3
"""Audit Promptária instrument identity, title resolution and traceability.

The registry is the canonical identity source. This audit deliberately separates
identity/resolution from execution authorization: a title can resolve an
instrument, but a title alone never grants permission for side effects.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

REQUIRED = (
    "id", "title", "path", "aliases", "keywords", "functions", "files",
    "relations", "operations", "ui", "activation",
)
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c)).casefold()
    value = re.sub(r"[\u200b-\u200f\ufeff]", "", value)
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"[\s-]+", " ", value).strip()


def canonical_title(path: Path) -> str | None:
    if not path.is_file():
        return None
    match = re.search(r"(?m)^#\s+(.+?)\s*$", path.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else None


def audit(registry_path: Path, root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    instruments: list[dict] = []
    terms: dict[str, list[dict]] = {}
    ids: set[str] = set()
    paths: set[str] = set()
    registry = None

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [f"Registry unreadable/invalid JSON: {exc}"],
                "warnings": [], "instruments": []}

    if not isinstance(registry, dict) or not isinstance(registry.get("instruments"), list):
        return {"valid": False, "errors": ["Registry must be an object with an instruments array."],
                "warnings": [], "instruments": []}

    contract = registry.get("identity_contract")
    if not isinstance(contract, dict):
        errors.append("identity_contract is required and must be an object.")
    else:
        declared_required = contract.get("required")
        if declared_required != list(REQUIRED):
            errors.append("identity_contract.required must exactly declare the canonical instrument fields.")
        if not isinstance(contract.get("matching"), str) or not contract.get("matching"):
            errors.append("identity_contract.matching must declare the deterministic matching policy.")

    for index, item in enumerate(registry["instruments"]):
        prefix = f"instruments[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: entry must be an object.")
            continue

        missing = [key for key in REQUIRED if key not in item]
        if missing:
            errors.append(f"{prefix}: missing fields: {', '.join(missing)}")

        ident, title, path = item.get("id"), item.get("title"), item.get("path")
        if not isinstance(ident, str) or not ident.strip() or not ID_RE.fullmatch(ident):
            errors.append(f"{prefix}: invalid id; use lowercase [a-z0-9._-] and start with alphanumeric.")
        elif ident in ids:
            errors.append(f"{prefix}: duplicate id {ident!r}.")
        else:
            ids.add(ident)

        if not isinstance(title, str) or not title.strip():
            errors.append(f"{prefix}: invalid title.")

        file_exists = False
        canonical = None
        if not isinstance(path, str) or not path.strip():
            errors.append(f"{prefix}: invalid path.")
        else:
            p = Path(path)
            if p.is_absolute() or ".." in p.parts or "\\" in path or not path.startswith("instruments/"):
                errors.append(f"{prefix}: unsafe/non-instrument path {path!r}.")
            if path in paths:
                errors.append(f"{prefix}: duplicate path {path!r}.")
            else:
                paths.add(path)
            file_exists = (root / path).is_file()
            if not file_exists:
                warnings.append(f"{ident or prefix}: instrument file missing: {path}")
            else:
                canonical = canonical_title(root / path)
                if not canonical:
                    errors.append(f"{prefix}: canonical instrument file has no H1 title.")
                elif isinstance(title, str) and normalize(canonical) != normalize(title):
                    errors.append(
                        f"{prefix}: registry title does not match canonical H1 in {path!r}: "
                        f"registry={title!r}; h1={canonical!r}"
                    )

        activation = item.get("activation", {})
        enabled = isinstance(activation, dict) and activation.get("enabled") is True
        status = activation.get("status", "unspecified") if isinstance(activation, dict) else "invalid"
        if not isinstance(activation, dict) or not isinstance(activation.get("enabled"), bool):
            errors.append(f"{prefix}: activation.enabled must be boolean.")

        aliases = item.get("aliases")
        if not isinstance(aliases, list) or not all(isinstance(x, str) and x.strip() for x in aliases):
            errors.append(f"{prefix}: aliases must be a non-empty-string array (empty array allowed).")
            aliases = aliases if isinstance(aliases, list) else []

        for field in ("keywords", "functions", "relations", "operations"):
            if not isinstance(item.get(field), list):
                errors.append(f"{prefix}: {field} must be an array.")

        ui = item.get("ui")
        if not isinstance(ui, dict):
            errors.append(f"{prefix}: ui must be an object.")
        elif ident and ui.get("node_id") != f"instrument:{ident}":
            errors.append(f"{prefix}: ui.node_id must equal instrument:{ident}.")

        declared_files = item.get("files")
        if not isinstance(declared_files, list):
            errors.append(f"{prefix}: files must be an array.")
            declared_files = []
        for file_index, file_path in enumerate(declared_files):
            file_prefix = f"{prefix}.files[{file_index}]"
            if not isinstance(file_path, str) or not file_path.strip():
                errors.append(f"{file_prefix}: invalid file path.")
                continue
            referenced_path = Path(file_path)
            if referenced_path.is_absolute() or ".." in referenced_path.parts or "\\" in file_path or file_path.startswith("/"):
                errors.append(f"{file_prefix}: unsafe referenced file path {file_path!r}.")
                continue
            if not (root / referenced_path).is_file():
                warnings.append(f"{ident or prefix}: declared referenced file missing: {file_path}")

        if enabled and not declared_files:
            warnings.append(f"{ident}: enabled but no implementation files declared.")
        if enabled and isinstance(path, str) and not file_exists:
            warnings.append(f"{ident}: enabled without its canonical instrument file; execution claim is unverified.")

        identity_terms = [(title, "title")] + [(alias, "alias") for alias in aliases]
        for term, kind in identity_terms:
            if isinstance(term, str) and normalize(term):
                terms.setdefault(normalize(term), []).append({"id": ident, "term": term, "kind": kind})

        instruments.append({
            "id": ident, "title": title, "path": path, "enabled": enabled,
            "activation_status": status, "file_exists": file_exists,
            "canonical_h1": canonical,
            "classification": "partially_automated" if enabled else "without_active_executor",
        })

    enabled_by_id = {item["id"]: item["enabled"] for item in instruments}
    collisions = []
    for term, matches in sorted(terms.items()):
        unique_ids = {m["id"] for m in matches if m.get("id")}
        if len(unique_ids) <= 1:
            continue
        enabled_matches = sorted(ident for ident in unique_ids if enabled_by_id.get(ident, False))
        collision = {
            "normalized_term": term,
            "matches": matches,
            "enabled_match_ids": enabled_matches,
            "severity": "blocking" if len(enabled_matches) > 1 else "warning",
            "resolution": "explicit_id_or_path_required" if len(enabled_matches) > 1 else "unique_enabled_match_only",
        }
        collisions.append(collision)
        if collision["severity"] == "blocking":
            errors.append("Ambiguous normalized title/alias among enabled instruments: " + term)
        else:
            warnings.append("Normalized title/alias collision includes disabled entries: " + term)

    # Physical inventory is authoritative for preventing orphaned definitions.
    physical = {
        p.relative_to(root).as_posix()
        for p in (root / "instruments").glob("*.md")
    } if (root / "instruments").is_dir() else set()
    registered_paths = {p for p in paths if isinstance(p, str)}
    for orphan in sorted(physical - registered_paths):
        errors.append(f"Unregistered instrument definition: {orphan}")
    for stale in sorted(registered_paths - physical):
        warnings.append(f"Registered instrument has no physical definition: {stale}")

    # Optional generated maps are checked when present, so registry identity cannot silently diverge.
    execution_map_path = root / "config" / "instrument-execution-map.json"
    execution_map_checked = False
    if execution_map_path.is_file():
        execution_map_checked = True
        try:
            execution_map = json.loads(execution_map_path.read_text(encoding="utf-8"))
            mapped = {x.get("id"): x for x in execution_map.get("instruments", []) if isinstance(x, dict)}
            for item in instruments:
                if item["id"] not in mapped:
                    errors.append(f"{item['id']}: missing execution-map identity entry.")
                else:
                    mapping = mapped[item["id"]]
                    if normalize(mapping.get("title", "")) != normalize(item["title"] or ""):
                        errors.append(f"{item['id']}: execution-map title diverges from registry.")
                    if mapping.get("path") != item["path"]:
                        errors.append(f"{item['id']}: execution-map path diverges from registry.")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Execution map unreadable/invalid JSON: {exc}")

    return {
        "valid": not errors,
        "registry": str(registry_path),
        "schema_version": registry.get("schema_version"),
        "instrument_count": len(instruments),
        "enabled_count": sum(i["enabled"] for i in instruments),
        "normalized_title_collisions": collisions,
        "execution_map_checked": execution_map_checked,
        "instruments": instruments,
        "errors": errors,
        "warnings": warnings,
        "resolution_index": {
            "precedence": ["explicit_instrument_id", "explicit_repository_path", "unique_normalized_title", "unique_normalized_alias"],
            "normalization": "case-insensitive; accents and punctuation folded; whitespace and hyphens normalized",
            "title_rule": "a canonical title resolves to exactly one enabled instrument or resolution is blocked",
            "collision_rule": "two enabled instruments sharing a normalized title/alias are never auto-activated",
            "trace_fields": ["id", "title", "path", "matched_term", "match_kind", "normalized_term"],
            "disabled_rule": "disabled entries never become active through title matching",
        },
        "policy": "Registry identity is canonical; validation must pass before publication/catalog generation.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("config/instrument-registry.json"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.registry, args.root)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
