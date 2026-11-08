#!/usr/bin/env python3
"""Build a conservative, reproducible inventory of Promptária instrument automation."""
from __future__ import annotations

import argparse
import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INSTRUMENTS = ROOT / "instruments"
REGISTRY = ROOT / "config" / "instrument-registry.json"
MANIFEST = ROOT / "tests" / "manifest.json"
EXECUTION_MAP = ROOT / "config" / "instrument-execution-map.json"
SPECIALIZED = ROOT / "scripts" / "promptaria_specialized_executor.py"
WORKFLOWS = ROOT / ".github" / "workflows"
TESTS = ROOT / "tests"
CATEGORIES = {"already_automated", "partially_automated", "no_executor"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def title_of(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def activation_enabled(item: dict[str, Any]) -> bool:
    """Treat activation as enabled only when its structure and value are explicit."""
    activation = item.get("activation")
    return isinstance(activation, dict) and activation.get("enabled") is True


def handler_map(source: str) -> dict[str, str]:
    """Read the HANDLERS ID-to-function mapping safely; do not execute repository code."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    def target_mentions_handlers(target: ast.AST) -> bool:
        if isinstance(target, ast.Name):
            return target.id == "HANDLERS"
        if isinstance(target, (ast.Tuple, ast.List)):
            return any(target_mentions_handlers(element) for element in target.elts)
        return False

    def assigns_handlers(node: ast.AST) -> bool:
        if isinstance(node, ast.Assign):
            return any(target_mentions_handlers(target) for target in node.targets)
        if isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
            return target_mentions_handlers(node.target)
        if isinstance(node, (ast.For, ast.AsyncFor)):
            return target_mentions_handlers(node.target)
        if isinstance(node, (ast.With, ast.AsyncWith)):
            return any(
                item.optional_vars is not None and target_mentions_handlers(item.optional_vars)
                for item in node.items
            )
        if isinstance(node, ast.ExceptHandler):
            return node.name == "HANDLERS"
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return any((alias.asname or alias.name.split(".")[0]) == "HANDLERS" for alias in node.names)
        return False

    declarations = [node for node in ast.walk(tree) if assigns_handlers(node)]
    # Only one direct top-level literal assignment is safe to treat as evidence.
    # Conditional, nested, annotated, augmented, or repeated assignments may
    # change the effective mapping at runtime and are intentionally rejected.
    if (
        len(declarations) != 1
        or declarations[0] not in tree.body
        or not isinstance(declarations[0], ast.Assign)
    ):
        return {}
    value_node = declarations[0].value
    if not isinstance(value_node, ast.Dict):
        return {}
    entries = list(zip(value_node.keys, value_node.values))
    key_counts: dict[str, int] = {}
    for key, _value in entries:
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            key_counts[key.value] = key_counts.get(key.value, 0) + 1
    # A duplicate literal key is ambiguous evidence, even though Python
    # would silently keep the last value at runtime.
    return {
        key.value: value.id
        for key, value in entries
        if isinstance(key, ast.Constant)
        and isinstance(key.value, str)
        and key_counts[key.value] == 1
        and isinstance(value, ast.Name)
    }



def catalog_integrity_report(registry: dict[str, Any], manifest: dict[str, Any], execution_map: dict[str, Any]) -> dict[str, Any]:
    """Report identity collisions before dictionary indexing can hide duplicate entries."""
    # Preserve malformed values long enough to report them instead of normalizing
    # them to [] and accidentally hiding the integrity error.
    sources = {
        "registry": registry.get("instruments"),
        "manifest": manifest.get("instruments"),
        "execution_map": execution_map.get("instruments"),
    }
    findings: list[dict[str, Any]] = []
    affected_ids: set[str] = set()
    indexed: dict[str, dict[str, list[dict[str, Any]]]] = {}

    for source_name, entries in sources.items():
        by_id: dict[str, list[dict[str, Any]]] = {}
        by_path: dict[str, list[str]] = {}
        if not isinstance(entries, list):
            findings.append({
                "type": "invalid_catalog_collection",
                "source": source_name,
                "instrument_ids": [],
                "details": f"{source_name}.instruments must be a list",
            })
        for item in entries if isinstance(entries, list) else []:
            if not isinstance(item, dict):
                findings.append({
                    "type": "invalid_catalog_entry",
                    "source": source_name,
                    "instrument_ids": [],
                    "details": f"{source_name} contains a non-object catalog entry",
                })
                continue
            item_id = item.get("id")
            path = item.get("path")
            for field in ("id", "title", "path"):
                if not isinstance(item.get(field), str) or not item.get(field).strip():
                    if isinstance(item_id, str) and item_id:
                        affected_ids.add(item_id)
                    findings.append({
                        "type": "missing_identity_field",
                        "source": source_name,
                        "instrument_ids": [item_id] if isinstance(item_id, str) and item_id else [],
                        "field": field,
                        "details": f"{source_name} entry is missing a non-empty {field}",
                    })
            if isinstance(item_id, str) and item_id:
                by_id.setdefault(item_id, []).append(item)
            if isinstance(path, str) and path:
                by_path.setdefault(path, []).append(item_id if isinstance(item_id, str) else "<missing-id>")
        indexed[source_name] = by_id
        for item_id, items in by_id.items():
            if len(items) > 1:
                affected_ids.add(item_id)
                findings.append({
                    "type": "duplicate_id",
                    "source": source_name,
                    "instrument_ids": [item_id],
                    "details": f"{source_name} contains {len(items)} entries with the same ID",
                })
        for path, ids in by_path.items():
            distinct_ids = sorted(set(ids))
            if len(distinct_ids) > 1:
                affected_ids.update(item_id for item_id in distinct_ids if item_id != "<missing-id>")
                findings.append({
                    "type": "duplicate_path",
                    "source": source_name,
                    "instrument_ids": distinct_ids,
                    "path": path,
                    "details": f"{source_name} maps multiple instrument IDs to one path",
                })

    all_ids = set().union(*(set(items) for items in indexed.values()))
    for item_id in sorted(all_ids):
        observed = {
            source_name: items[item_id]
            for source_name, items in indexed.items()
            if item_id in items
        }
        if len(observed) != len(sources):
            affected_ids.add(item_id)
            findings.append({
                "type": "catalog_presence_mismatch",
                "source": "cross_catalog",
                "instrument_ids": [item_id],
                "details": "instrument ID is not present exactly in registry, manifest, and execution map",
                "missing_sources": sorted(set(sources) - set(observed)),
            })
        for field in ("path", "title"):
            values = {
                item[field]
                for entries in observed.values()
                for item in entries
                if isinstance(item.get(field), str)
            }
            if len(values) > 1:
                affected_ids.add(item_id)
                findings.append({
                    "type": f"{field}_mismatch",
                    "source": "cross_catalog",
                    "instrument_ids": [item_id],
                    "details": f"canonical {field} differs between registry, manifest, and execution map",
                    "values": sorted(values),
                })

    return {
        "status": "clean" if not findings else "conflicts_detected",
        "finding_count": len(findings),
        "findings": findings,
        "affected_instrument_ids": sorted(affected_ids),
    }

def build_inventory(root: Path = ROOT) -> dict[str, Any]:
    registry = read_json(root / "config/instrument-registry.json")
    manifest = read_json(root / "tests/manifest.json")
    execution_map = read_json(root / "config/instrument-execution-map.json")
    specialized_path = root / "scripts/promptaria_specialized_executor.py"
    source = specialized_path.read_text(encoding="utf-8") if specialized_path.is_file() else ""
    handlers = handler_map(source) if source else {}
    catalog_integrity = catalog_integrity_report(registry, manifest, execution_map)
    conflicted_ids = set(catalog_integrity["affected_instrument_ids"])
    registry_items = {
        item.get("id"): item for item in (registry.get("instruments") if isinstance(registry.get("instruments"), list) else [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    manifest_items = {
        item.get("id"): item for item in (manifest.get("instruments") if isinstance(manifest.get("instruments"), list) else [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    mapped_items = {
        item.get("id"): item for item in (execution_map.get("instruments") if isinstance(execution_map.get("instruments"), list) else [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / ".github/workflows").glob("*.yml"))
    ) if (root / ".github/workflows").is_dir() else ""
    test_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "tests").glob("test_*.py"))
    ) if (root / "tests").is_dir() else ""

    records: list[dict[str, Any]] = []
    for path in sorted((root / "instruments").glob("*.md")):
        relative = path.relative_to(root).as_posix()
        title = title_of(path)
        ids = [
            instrument_id for instrument_id, item in registry_items.items()
            if item.get("path") == relative
        ]
        if len(ids) == 1:
            instrument_id = ids[0]
        else:
            manifest_ids = [
                instrument_id for instrument_id, item in manifest_items.items()
                if item.get("path") == relative
            ]
            instrument_id = manifest_ids[0] if len(manifest_ids) == 1 else None

        registry_item = registry_items.get(instrument_id, {})
        manifest_item = manifest_items.get(instrument_id, {})
        map_item = mapped_items.get(instrument_id, {})
        handler_name = map_item.get("specialized_handler")
        has_handler = bool(
            instrument_id and isinstance(handler_name, str)
            and handlers.get(instrument_id) == handler_name
        )
        in_manifest = bool(instrument_id and instrument_id in manifest_items)
        in_registry = bool(instrument_id and instrument_id in registry_items)
        source_consistent = bool(instrument_id not in conflicted_ids and title and (
            not registry_item or registry_item.get("title") == title
        ) and (
            not manifest_item or manifest_item.get("title") == title
        ))
        has_tests = bool(instrument_id and instrument_id in test_text)
        executor_in_workflow = "promptaria_contextual_executor.py" in workflow_text or "promptaria_specialized_executor.py" in workflow_text
        # Full automation is only asserted when the contract explicitly records verified
        # functional execution and source, handler, tests, and workflow integration agree.
        verified_functional = bool(
            map_item.get("functional_execution_verified") is True
            and has_handler and has_tests and executor_in_workflow
            and source_consistent and in_registry and in_manifest
        )
        if verified_functional:
            category = "already_automated"
        elif instrument_id not in conflicted_ids and has_handler and map_item.get("specialized_execution_status") == "implemented":
            category = "partially_automated"
        else:
            category = "no_executor"

        gaps = []
        if not in_registry:
            gaps.append("instrument is absent from canonical registry")
        if not in_manifest:
            gaps.append("instrument is absent from test manifest")
        if not source_consistent:
            gaps.append("canonical identity conflicts with catalog metadata or the physical Markdown heading")
        if not has_handler:
            gaps.append("no matching specialized handler is proven by the handler map")
        elif not verified_functional:
            gaps.append("full functional execution is not explicitly evidenced by the execution contract")
        if not has_tests:
            gaps.append("instrument ID is not referenced by the Python regression tests")
        if not executor_in_workflow:
            gaps.append("specialized executor is not found in the workflow configuration")
        if map_item.get("side_effects_authorized_by_title") is True:
            gaps.append("unsafe contract: title must not authorize side effects")
        if not activation_enabled(registry_item):
            gaps.append("instrument is inactive; inventory does not imply activation")

        records.append({
            "instrument_id": instrument_id,
            "title": title,
            "path": relative,
            "category": category,
            "activation_enabled": activation_enabled(registry_item),
            "registry_present": in_registry,
            "manifest_present": in_manifest,
            "handler_present": has_handler,
            "functional_execution_verified": verified_functional,
            "dependencies": {
                "executor_map": "config/instrument-execution-map.json",
                "specialized_executor": "scripts/promptaria_specialized_executor.py",
                "workflow_integration_observed": executor_in_workflow,
            },
            "permissions": {
                "side_effects_authorized_by_title": map_item.get("side_effects_authorized_by_title", False),
                "note": "Permission and environment requirements must be checked at execution time."
            },
            "success_criteria": [
                "canonical title and ID are consistent",
                "handler is mapped to this instrument",
                "functional behavior is covered by tests and an integrated workflow",
                "execution result is verified rather than inferred from planning"
            ],
            "failure_criteria": [
                "missing or conflicting identity",
                "handler, test, workflow, or required dependency is missing",
                "execution evidence is absent or claims a result not produced"
            ],
            "evidence": {
                "registry": in_registry,
                "manifest": in_manifest,
                "handler_map": bool(map_item),
                "handler_function": has_handler,
                "test_reference": has_tests,
                "workflow_executor_reference": executor_in_workflow,
                "title_consistent": source_consistent,
            },
            "gaps": gaps,
        })

    # Catalog entries without a physical Markdown file are also surfaced as gaps.
    physical_paths = {record["path"] for record in records}
    for instrument_id, item in sorted(registry_items.items()):
        relative = item.get("path")
        if isinstance(relative, str) and relative not in physical_paths:
            records.append({
                "instrument_id": instrument_id,
                "title": item.get("title"),
                "path": relative,
                "category": "no_executor",
                "activation_enabled": activation_enabled(item),
                "registry_present": True,
                "manifest_present": instrument_id in manifest_items,
                "handler_present": handlers.get(instrument_id) == item.get("specialized_handler"),
                "functional_execution_verified": False,
                "evidence": {"physical_source_present": False},
                "gaps": ["registry points to a missing physical instrument file"],
            })

    invalid = [record for record in records if record.get("category") not in CATEGORIES]
    if invalid:
        raise AssertionError("Every inventory record must have exactly one supported category")
    counts = {category: sum(item["category"] == category for item in records) for category in sorted(CATEGORIES)}
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit_type": "conservative_static_operational_audit",
        "repository_root": ".",
        "classification_policy": {
            "already_automated": "Requires an explicit functional_execution_verified contract plus handler, test, source identity and workflow evidence.",
            "partially_automated": "A mapped specialized handler exists, but complete functional execution is not proven.",
            "no_executor": "No mapped specialized handler is proven, or the source/identity contract is missing.",
            "limitations": [
                "Static inspection does not prove runtime execution or external effects.",
                "This report does not execute instrument text or grant permissions.",
                "External services, credentials, branch protections and runtime configuration require separate verification."
            ]
        },
        "summary": {"instrument_count": len(records), "category_counts": counts},
        "catalog_integrity": catalog_integrity,
        "instruments": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/promptaria-operational-audit.json"))
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    report = build_inventory()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "audit_generated", **report["summary"], "output": str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
