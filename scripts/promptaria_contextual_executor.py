#!/usr/bin/env python3
"""Run Promptária's contextual router and specialized handlers as one auditable flow."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_context_router as router
import promptaria_specialized_executor as specialized


def execute(payload: dict, preflight: dict | None = None) -> dict:
    request = payload.get("request", payload.get("demand", payload))
    context = router.analyze(request)
    contextual_ids = list(context["selected_instrument_ids"])

    explicit = payload.get("instrument_ids", [])
    if isinstance(explicit, str):
        explicit = [explicit]
    if not isinstance(explicit, list) or any(not isinstance(item, str) for item in explicit):
        raise SystemExit("instrument_ids deve ser uma lista de IDs textuais.")
    explicit_ids = set(explicit)

    matches = (preflight or {}).get("matched_instruments", [])
    if not isinstance(matches, list):
        matches = []

    # Contextual ranking is not an identity disambiguation mechanism. Do not
    # convert a preflight collision into a resolved match just because the
    # router happened to select the same ID. An explicit instrument ID is the
    # supported way for a caller to disambiguate a known collision.
    unresolved_selected = sorted({
        item.get("id")
        for item in matches
        if isinstance(item, dict)
        and item.get("id") in contextual_ids
        and item.get("identity_status") not in (None, "resolved")
        and item.get("id") not in explicit_ids
    })
    if unresolved_selected:
        raise SystemExit(
            "Correspondência ambígua bloqueada; informe explicitamente instrument_ids "
            "para desambiguar: " + ", ".join(unresolved_selected)
        )

    registry = specialized.index_catalog_entries(
        specialized.read_object(ROOT / "config" / "instrument-registry.json"),
        "config/instrument-registry.json",
    )

    def registry_active(item_id: str) -> bool:
        return (
            item_id in registry
            and isinstance(registry[item_id].get("activation"), dict)
            and registry[item_id]["activation"].get("enabled") is True
        )

    unknown_explicit_ids = sorted(item_id for item_id in explicit_ids if item_id not in registry)
    if unknown_explicit_ids:
        raise SystemExit(
            "IDs de instrumento ausentes do registro canônico: "
            + ", ".join(unknown_explicit_ids)
        )

    active_contextual_ids = [
        item_id for item_id in contextual_ids if registry_active(item_id)
    ]
    active_explicit_ids = [item_id for item_id in explicit if registry_active(item_id)]
    blocked_explicit_ids = {
        item_id for item_id in explicit if not registry_active(item_id)
    }
    blocked_contextual_ids = set(contextual_ids) - set(active_contextual_ids)
    # The router now records inactive rule targets separately instead of
    # placing them in selected_instrument_ids; preserve those blocks in the
    # public routing evidence so callers can distinguish "not selected"
    # from "not selected because the registry disables it".
    for candidate in context.get("task_candidates", []):
        if isinstance(candidate, dict):
            blocked = candidate.get("blocked_inactive_instrument_ids", [])
            if isinstance(blocked, list):
                blocked_contextual_ids.update(
                    item_id for item_id in blocked if isinstance(item_id, str)
                )

    # Context routing is a candidate generator, not an activation grant.
    # Preflight activation flags are also non-authoritative: unresolved or
    # ambiguous identity evidence must never become an implicit selection.
    selected = list(dict.fromkeys([*active_contextual_ids, *active_explicit_ids]))
    for item in matches:
        item_id = item.get("id") if isinstance(item, dict) else None
        if (
            isinstance(item_id, str)
            and registry_active(item_id)
            and isinstance(item, dict)
            and item.get("activation", True)
            and item.get("identity_status") in (None, "resolved")
            and item_id not in selected
        ):
            selected.append(item_id)

    # A preflight's "activation" field is not authoritative. Report references
    # to registry-inactive instruments as blocked even when preflight labels
    # them resolved or activated.
    blocked_preflight_ids = {
        item.get("id")
        for item in matches
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item.get("id") in registry
        and not registry_active(item["id"])
    }
    blocked_inactive_ids = sorted(blocked_contextual_ids | blocked_preflight_ids | blocked_explicit_ids)

    augmented = dict(preflight or {})
    augmented["matched_instruments"] = [
        {"id": item_id, "identity_status": "resolved", "activation": True}
        for item_id in selected
    ] + [
        item for item in matches
        if isinstance(item, dict)
        and (not item.get("activation", True) or item.get("identity_status") not in (None, "resolved"))
    ]
    result = specialized.execute({**payload, "instrument_ids": selected}, preflight=augmented)
    result["contextual_analysis"] = context
    result["routing_evidence"] = {
        "task_candidates": context["task_candidates"],
        "evidence_chain": context["evidence_chain"],
        "selected_instrument_ids": selected,
        "blocked_inactive_instrument_ids": blocked_inactive_ids,
        "routing_status": "contextual_handlers_executed",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--preflight", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.request.read_text(encoding="utf-8"))
    preflight = json.loads(args.preflight.read_text(encoding="utf-8")) if args.preflight else None
    result = execute(payload, preflight)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["execution_status"],
        "specialized_execution_count": result["specialized_execution_count"],
        "selected_instrument_ids": result["selected_instrument_ids"],
        "contextual_tasks": [item["task"] for item in result["contextual_analysis"]["task_candidates"]],
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
