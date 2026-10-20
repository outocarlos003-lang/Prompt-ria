#!/usr/bin/env python3
"""Build a deterministic, auditable plan from Promptária instrument mentions.

This preflight does not mutate repository files. It resolves canonical titles,
aliases, and explicit IDs/paths; preserves all matches; assesses a narrowly
scoped master-protocol preauthorization; and keeps protected-segment integration
closed by default so instrument activation is not confused with structural integration.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
import promptaria_specialized_executor as specialized
SEGMENT_POLICY = ROOT / "config" / "segment-integration-policy.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c)).casefold()
    value = re.sub(r"[\u200b-\u200f\ufeff]", "", value)
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"[\s-]+", " ", value).strip()


def load_object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Não foi possível ler JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path} deve conter um objeto JSON.")
    return value


def occurrences(text: str, phrase: str) -> list[tuple[int, int]]:
    if not phrase:
        return []
    return [(m.start(), m.end()) for m in re.finditer(
        r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text
    )]


def resolve_request(request: str, manifest: dict, execution_map: dict) -> list[dict]:
    normalized_request = normalize(request)
    mapped = {item["id"]: item for item in execution_map.get("instruments", [])}
    catalog = []
    for item in manifest.get("instruments", []):
        if not isinstance(item, dict) or not all(k in item for k in ("id", "title", "path")):
            continue
        terms = [item["title"], *item.get("aliases", []), item["id"], item["path"]]
        normalized_terms = sorted({normalize(term) for term in terms if isinstance(term, str) and normalize(term)}, key=len, reverse=True)
        catalog.append((item, normalized_terms))

    found = []
    for item, terms in catalog:
        hits = []
        for term in terms:
            hits.extend((start, end, term) for start, end in occurrences(normalized_request, term))
        if not hits:
            continue
        hits.sort(key=lambda hit: (hit[0], -(hit[1] - hit[0])))
        distinct_hits = []
        for hit in hits:
            if any(hit[0] < prior[1] and prior[0] < hit[1] for prior in distinct_hits):
                continue
            distinct_hits.append(hit)
        map_item = mapped.get(item["id"], {})
        manifest_title = normalize(item["title"])
        collision_ids = [
            other["id"] for other, _ in catalog
            if normalize(other["title"]) == manifest_title
        ]
        has_qualifier = any(
            normalize(term) in normalized_request
            for term in (item["id"], item["path"])
        )
        sibling_qualified = any(
            other["id"] != item["id"]
            and normalize(other["title"]) == manifest_title
            and any(normalize(term) in normalized_request for term in (other["id"], other["path"]))
            for other, _ in catalog
        )
        if len(collision_ids) > 1 and sibling_qualified and not has_qualifier:
            continue
        title_only_collision = len(collision_ids) > 1 and not has_qualifier
        for start, end, matched_term in distinct_hits:
            qualified_occurrence = matched_term in {normalize(item["id"]), normalize(item["path"])}
            ambiguous = title_only_collision and not qualified_occurrence
            found.append({
                "id": item["id"],
                "title": item["title"],
                "path": item["path"],
                "matched_term": matched_term,
                "start": start,
                "end": end,
                "identity_status": "ambiguous_title_collision" if ambiguous else "resolved",
                "activation": not ambiguous,
                "resolution_status": "blocked_ambiguous_title" if ambiguous else "resolved_by_exact_title_alias_id_or_path",
                "specialized_executor": map_item.get("specialized_executor"),
                "specialized_execution_status": map_item.get("specialized_execution_status", "not_mapped"),
            })
    found.sort(key=lambda item: (item["start"], item["end"], item["id"]))
    merged = {}
    for match in found:
        key = (match["id"], match["identity_status"])
        if key not in merged:
            merged[key] = {**match, "evidence": []}
        merged[key]["evidence"].append({
            "matched_term": match["matched_term"],
            "start": match["start"],
            "end": match["end"],
        })
    return sorted(merged.values(), key=lambda item: (item["start"], item["id"]))


def resolve_segment_exceptions(payload: dict, manifest: dict) -> tuple[list[str], list[dict]]:
    """Allow extra protected-segment integration only by explicit request or justified need."""
    entries = []
    for field, basis in (("segment_integration_request", "explicit_user_request"), ("segment_integration_need", "specific_need")):
        raw = payload.get(field, [])
        if isinstance(raw, (str, dict)):
            raw = [raw]
        if not isinstance(raw, list):
            continue
        for value in raw:
            if isinstance(value, str) and value.strip():
                entries.append((value, "", basis))
            elif isinstance(value, dict):
                reference = value.get("instrument") or value.get("instrument_id") or value.get("title") or value.get("path")
                reason = value.get("reason", "")
                if isinstance(reference, str) and reference.strip():
                    entries.append((reference, reason if isinstance(reason, str) else "", basis))
    resolved, evidence = [], []
    for reference, reason, basis in entries:
        if basis == "specific_need" and not normalize(reason):
            continue
        ref = normalize(reference)
        candidates = []
        for item in manifest.get("instruments", []):
            values = [item.get("id", ""), item.get("path", ""), item.get("title", ""), *item.get("aliases", [])]
            if any(isinstance(value, str) and normalize(value) == ref for value in values):
                candidates.append(item)
        if len(candidates) != 1:
            continue
        item = candidates[0]
        resolved.append(item["id"])
        evidence.append({"instrument_id": item["id"], "reference": reference, "reason": reason, "basis": basis})
    return list(dict.fromkeys(resolved)), evidence


def build_segment_integration(payload: dict, matches: list[dict], manifest: dict) -> dict:
    policy = load_object(SEGMENT_POLICY)
    defaults = list(policy["default_integrated_instrument_ids"])
    extra_ids, evidence = resolve_segment_exceptions(payload, manifest)
    extras = [item_id for item_id in extra_ids if item_id not in defaults]
    integrated = list(dict.fromkeys(defaults + extras))
    matched_ids = {m["id"] for m in matches if m.get("activation")}
    blocked = sorted(matched_ids.difference(integrated))
    return {
        "mode": policy["integration_policy"]["mode"],
        "protected_segments": policy["protected_segments"],
        "default_integrated_instrument_ids": defaults,
        "additional_integrated_instrument_ids": extras,
        "integration_instrument_ids": integrated,
        "integration_evidence": evidence,
        "blocked_automatic_integrations": blocked,
        "activation_remains_independent": True,
        "selection_is_not_integration": True,
        "policy_source": "config/segment-integration-policy.json",
    }


def assess_preauthorization(request: str, matches: list[dict], destination: str | None) -> dict:
    normalized_request = normalize(request)
    master_ids = {"master-activation", "master-execution"}
    master_present = any(m["id"] in master_ids and m["activation"] for m in matches)
    target_matches = [m for m in matches if m["id"] not in master_ids and m["activation"]]
    explicit_write_intent = re.search(
        r"\b(escrev[ae]|grav[ae]|crie|criar|atualiz[ae]|substitu[ae]|salv[ae]|insir[ae]|incorpor[ae]|write|create|update|save)\b",
        normalized_request,
    ) is not None
    destination_ok = (
        isinstance(destination, str)
        and destination.startswith("artifacts/")
        and all(part not in ("", ".", "..") for part in destination.split("/"))
        and "\\" not in destination
        and not destination.startswith("/")
        and ".git" not in {part.casefold() for part in destination.split("/")}
    )
    ambiguity = any(m["identity_status"] != "resolved" for m in matches)
    eligible = bool(master_present and target_matches and explicit_write_intent and destination_ok and not ambiguity)
    return {
        "status": "scoped_preauthorization_eligible" if eligible else "not_authorized",
        "write_authorized": eligible,
        "policy": "master_protocol_plus_unambiguous_instrument_plus_explicit_write_intent_plus_artifacts_destination",
        "requirements": {
            "master_protocol_detected": master_present,
            "at_least_one_unambiguous_target_instrument": bool(target_matches),
            "explicit_write_intent": explicit_write_intent,
            "destination_inside_artifacts": bool(destination_ok),
            "no_unresolved_title_collision": not ambiguity,
        },
        "limitations": [
            "A title mention alone never authorizes a write.",
            "This assessment is scoped to write_text under artifacts/; it grants no external, destructive, or repository-source mutation permission.",
            "The executor still requires dry_run=false and --confirm-operation matching operation_id for a real write.",
            "A plan is not proof that a specialized instrument executor exists or ran.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path, help="JSON object with request and optional destination")
    parser.add_argument("--manifest", type=Path, default=ROOT / "tests" / "manifest.json")
    parser.add_argument("--execution-map", type=Path, default=ROOT / "config" / "instrument-execution-map.json")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = load_object(args.request)
    request = payload.get("request", "")
    if not isinstance(request, str) or not request.strip():
        raise SystemExit("Campo request obrigatório e não vazio.")
    manifest = load_object(args.manifest)
    execution_map = load_object(args.execution_map)
    matches = resolve_request(request, manifest, execution_map)
    preauthorization = assess_preauthorization(request, matches, payload.get("destination"))
    segment_integration = build_segment_integration(payload, matches, manifest)
    result = {
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request": request,
        "destination": payload.get("destination"),
        "matched_instruments": matches,
        "matched_instrument_count": len(matches),
        "preauthorization": preauthorization,
        "segment_integration": segment_integration,
        "execution_performed": False,
        "status": "plan_ready" if matches else "no_instrument_match",
    }
    output_path = specialized.validate_output_path(args.output, [args.request])
    specialized.atomic_json(output_path, result)
    print(f"Instrumentos identificados: {len(matches)}")
    print(f"Pré-autorização delimitada: {preauthorization['status']}")
    print(f"Integração nos segmentos protegidos: {segment_integration['integration_instrument_ids']}")
    print(f"Integrações automáticas bloqueadas: {segment_integration['blocked_automatic_integrations']}")
    print(f"Plano: {args.output}")


if __name__ == "__main__":
    main()
