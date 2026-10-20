#!/usr/bin/env python3
"""Validate the additive extended-identity contract against the canonical registry."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "instrument-reference-contract.json"
REGISTRY_PATH = ROOT / "config" / "instrument-registry.json"

EXPECTED_FIELDS = {
    "id", "title", "path", "aliases", "keywords", "functions", "files",
    "relations", "operations", "ui", "activation",
}
EXPECTED_METADATA = {
    "slug": ("string", None),
    "prompt_markers": ("array", "string"),
    "consumers": ("array", "string"),
    "inputs": ("array", "string"),
    "outputs": ("array", "string"),
    "status": ("string", None),
}
STATUS_VALUES = {"active", "draft", "deprecated", "disabled"}


def validate(contract: dict, registry: dict) -> list[str]:
    errors: list[str] = []
    compatibility = contract.get("compatibility", {})
    identity = contract.get("identity_resolution", {})
    metadata = contract.get("optional_metadata", {})

    if contract.get("schema_version") != 2:
        errors.append("contract schema_version must be 2")
    if registry.get("schema_version") != compatibility.get("registry_schema_version") or registry.get("schema_version") != 2:
        errors.append("contract must declare compatibility with registry schema_version 2")
    if compatibility.get("migration_mode") != "additive":
        errors.append("migration_mode must be additive")
    if compatibility.get("unknown_fields") != "preserve":
        errors.append("unknown_fields must be preserve")
    if set(compatibility.get("required_existing_identity_fields", [])) != EXPECTED_FIELDS:
        errors.append("required_existing_identity_fields must match the canonical identity fields")
    if identity.get("authoritative_id") != "id" or identity.get("canonical_name") != "title":
        errors.append("identity resolution must preserve id and title as authoritative identity fields")
    if identity.get("explicit_aliases") != "aliases":
        errors.append("explicit aliases must resolve from aliases")
    if identity.get("activation_gate") != "activation.enabled must be true for functional resolution":
        errors.append("activation gate must keep activation.enabled authoritative")

    for name, (expected_type, expected_item_type) in EXPECTED_METADATA.items():
        definition = metadata.get(name)
        if not isinstance(definition, dict) or definition.get("type") != expected_type:
            errors.append(f"optional_metadata.{name} must declare type {expected_type}")
            continue
        if expected_item_type and definition.get("items") != expected_item_type:
            errors.append(f"optional_metadata.{name}.items must be {expected_item_type}")
    if metadata.get("status", {}).get("enum") != ["active", "draft", "deprecated", "disabled"]:
        errors.append("optional_metadata.status enum is invalid")

    entries = registry.get("instruments")
    if not isinstance(entries, list) or not entries:
        errors.append("registry instruments must be a non-empty list")
        return errors
    seen_ids: set[str] = set()
    for index, item in enumerate(entries):
        label = item.get("id", f"index {index}") if isinstance(item, dict) else f"index {index}"
        if not isinstance(item, dict):
            errors.append(f"{label}: instrument entry must be an object")
            continue
        missing = EXPECTED_FIELDS - set(item)
        if missing:
            errors.append(f"{label}: missing identity fields: {', '.join(sorted(missing))}")
        instrument_id = item.get("id")
        if not isinstance(instrument_id, str) or not instrument_id.strip():
            errors.append(f"{label}: id must be a non-empty string")
        elif instrument_id in seen_ids:
            errors.append(f"{label}: duplicate id")
        else:
            seen_ids.add(instrument_id)
        activation = item.get("activation")
        if not isinstance(activation, dict) or not isinstance(activation.get("enabled"), bool):
            errors.append(f"{label}: activation.enabled must be boolean")
        for field in ("aliases", "keywords", "functions", "files", "relations", "operations"):
            if field in item and (not isinstance(item[field], list) or not all(isinstance(v, str) for v in item[field])):
                errors.append(f"{label}: {field} must be an array of strings")
        for name, (expected_type, expected_item_type) in EXPECTED_METADATA.items():
            if name not in item:
                continue
            value = item[name]
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"{label}: optional {name} must be a string")
            elif expected_type == "array" and (
                not isinstance(value, list) or not all(isinstance(v, str) for v in value)
            ):
                errors.append(f"{label}: optional {name} must be an array of strings")
        if "status" in item and item["status"] not in STATUS_VALUES:
            errors.append(f"{label}: status must be one of {', '.join(sorted(STATUS_VALUES))}")
    return errors


def main() -> None:
    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot load identity contract or registry: {exc}") from exc
    errors = validate(contract, registry)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print(f"Extended identity contract valid: {len(registry['instruments'])} registered instruments.")


if __name__ == "__main__":
    main()
