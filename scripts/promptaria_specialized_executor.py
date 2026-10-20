#!/usr/bin/env python3
"""Execute instrument-specific, deterministic Promptária handlers and emit evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "tests" / "manifest.json"
MAP_PATH = ROOT / "config" / "instrument-execution-map.json"


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c)).casefold()
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"[\s-]+", " ", value).strip()


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"JSON inválido ou inacessível ({path}): {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path} deve conter um objeto JSON.")
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    """Write JSON through a unique same-directory temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temp_path = Path(stream.name)
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def index_catalog_entries(value: dict[str, Any], source_name: str) -> dict[str, dict[str, Any]]:
    entries = value.get("instruments", [])
    if not isinstance(entries, list):
        raise SystemExit(f"Catálogo inválido em {source_name}: 'instruments' deve ser uma lista.")
    indexed: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(entries):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            raise SystemExit(f"Entrada inválida em {source_name} na posição {position}: ID ausente ou inválido.")
        item_id = item["id"]
        if item_id in indexed:
            raise SystemExit(f"ID duplicado em {source_name}: {item_id}. Execução bloqueada.")
        indexed[item_id] = item
    return indexed


def validate_catalog_identity(
    canonical: dict[str, dict[str, Any]],
    mapped: dict[str, dict[str, Any]],
    registry: dict[str, dict[str, Any]],
) -> None:
    sources = {"manifesto": canonical, "mapa de execução": mapped, "registro": registry}
    expected_ids = set(canonical)
    if not expected_ids or any(set(entries) != expected_ids for entries in (mapped, registry)):
        raise SystemExit("Manifesto, mapa de execução e registro não cobrem exatamente os mesmos instrumentos.")
    for item_id in sorted(expected_ids):
        for field in ("title", "path"):
            values = [entries[item_id].get(field) for entries in sources.values()]
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise SystemExit(
                    f"Identidade divergente entre catálogos para {item_id}: campo '{field}' inconsistente."
                )
            if len(set(values)) != 1:
                raise SystemExit(
                    f"Identidade divergente entre catálogos para {item_id}: campo '{field}' inconsistente."
                )


def load_catalog() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    manifest = read_object(MANIFEST_PATH)
    execution_map = read_object(MAP_PATH)
    registry = read_object(ROOT / "config" / "instrument-registry.json")
    canonical = index_catalog_entries(manifest, "tests/manifest.json")
    mapped = index_catalog_entries(execution_map, "config/instrument-execution-map.json")
    registered = index_catalog_entries(registry, "config/instrument-registry.json")
    validate_catalog_identity(canonical, mapped, registered)
    return canonical, mapped


def resolve_ids(request_text: str, canonical: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Resolve complete normalized titles or registered aliases; collisions remain blocked."""
    normalized_request = normalize(request_text)
    registry_path = ROOT / "config" / "instrument-registry.json"
    registry = read_object(registry_path)
    registry_items = index_catalog_entries(registry, "config/instrument-registry.json")
    active_items = {
        item_id: item
        for item_id, item in registry_items.items()
        if item.get("activation", {}).get("enabled") is True
    }
    candidates: dict[str, list[dict[str, Any]]] = {}
    for item_id, item in canonical.items():
        if item_id not in active_items:
            continue
        registry_item = active_items[item_id]
        terms = [("title", item.get("title", ""))]
        terms.extend(("alias", alias) for alias in registry_item.get("aliases", []) if isinstance(alias, str))
        matched_terms = []
        for kind, value in terms:
            term = normalize(value) if isinstance(value, str) else ""
            if not term:
                continue
            spans = [
                [match.start(), match.end()]
                for match in re.finditer(
                    r"(?<!\w)" + re.escape(term) + r"(?!\w)",
                    normalized_request,
                    flags=re.UNICODE,
                )
            ]
            if spans:
                matched_terms.append({"kind": kind, "normalized": term, "spans": spans})
        if matched_terms:
            candidates[item_id] = matched_terms

    # A shorter title or alias must not independently select an instrument
    # when every occurrence is contained in another instrument's longer term.
    # A separate occurrence remains valid, preserving cumulative selection.
    filtered: dict[str, list[dict[str, Any]]] = {}
    for item_id, terms in candidates.items():
        retained = []
        for term in terms:
            shadowed = bool(term["spans"]) and all(
                any(
                    other_id != item_id
                    and len(other_term["normalized"]) > len(term["normalized"])
                    and any(
                        other_span[0] <= span[0]
                        and other_span[1] >= span[1]
                        and other_span != span
                        for other_span in other_term["spans"]
                    )
                    for other_id, other_terms in candidates.items()
                    for other_term in other_terms
                )
                for span in term["spans"]
            )
            if not shadowed:
                retained.append(term)
        if retained:
            filtered[item_id] = retained

    matches = []
    for item_id, matched_terms in filtered.items():
        item = canonical[item_id]
        explicit = any(
            re.search(
                r"(?<![\w-])" + re.escape(value) + r"(?![\w-])",
                request_text,
                flags=re.IGNORECASE | re.UNICODE,
            )
            for value in (item_id, item["path"])
        )
        collision_ids = set()
        for other_id, other_terms in filtered.items():
            if other_id != item_id and {
                term["normalized"] for term in matched_terms
            } & {term["normalized"] for term in other_terms}:
                collision_ids.add(other_id)
        resolved = explicit or not collision_ids
        matches.append({
            "id": item_id,
            "title": item["title"],
            "path": item["path"],
            "matched_terms": [
                {"kind": term["kind"], "normalized": term["normalized"]}
                for term in matched_terms
            ],
            "identity_status": "resolved" if resolved else "ambiguous_registered_term_collision",
            "activation": resolved,
        })
    return matches


def handler_github_operational(context: dict[str, Any]) -> dict[str, Any]:
    # One canonical identity now carries both source-recovery and fixed-prompt
    # envelope responsibilities. Keep the original recovery contract intact.
    envelope_result = handler_fixed_prompt(context)
    return {
        "handler": "recover-and-verify-source",
        "result": "source_recovered",
        "demand": context["demand"],
        "source": context["source"],
        "integrity": {"sha256": context["source_sha256"], "bytes": len(context["source"].encode("utf-8"))},
        "next_step": "handoff_verified_source_to_coordinator",
        "canonical_identity": {
            "instrument_id": "github-operational",
            "registry_path": "config/instrument-registry.json",
            "node_id": "instrument:github-operational",
            "roles": ["title_correspondence", "master_protocol_fixed_instrument", "standard_preconfiguration", "demand_envelope"],
        },
        "demand_envelope": envelope_result["envelope"],
        "cross_segment_relations": [
            "title-correspondence-automation->instrument:github-operational",
            "master-protocol-fixed-instrument->instrument:github-operational",
            "standard-preconfiguration->instrument:github-operational",
        ],
    }


def handler_coordinator(context: dict[str, Any]) -> dict[str, Any]:
    ids = context["selected_ids"]
    return {
        "handler": "coordinate-instrument-bundle",
        "result": "bundle_coordinated",
        "demand": context["demand"],
        "execution_order": list(dict.fromkeys(["coordinator", "github-operational", *ids])),
        "instrument_sources": [
            {"id": item_id, "path": context["catalog"][item_id]["path"], "sha256": context["source_hashes"][item_id]}
            for item_id in ids
        ],
        "validation_gates": ["identity", "source_integrity", "scope", "dependencies", "result_contract"],
    }


def handler_master_activation(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "handler": "activate-master-protocol",
        "result": "activation_plan_built",
        "demand": context["demand"],
        "base_instruments": ["coordinator", "master-activation", "github-operational"],
        "selected_instruments": context["selected_ids"],
        "gates": ["demand_present", "instrument_identity_resolved", "source_verified", "capability_available"],
        "automatic_external_side_effects": False,
    }


def handler_master_execution(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "handler": "execute-first-pass-checklist",
        "result": "execution_checklist_completed",
        "demand": context["demand"],
        "phases": [
            {"phase": "interpret", "check": "demand and expected result are explicit"},
            {"phase": "recover", "check": "all selected source files were recovered and hashed"},
            {"phase": "plan", "check": "dependencies and constraints are listed"},
            {"phase": "execute", "check": "only the instrument-specific operation defined by this handler is run"},
            {"phase": "validate", "check": "output schema and source identity are verified"},
            {"phase": "report", "check": "evidence and limitations are included"},
        ],
        "source_hashes": {key: context["source_hashes"][key] for key in context["selected_ids"]},
    }


def handler_functional_correference(context: dict[str, Any]) -> dict[str, Any]:
    matches = context["matches"]
    return {
        "handler": "resolve-all-functional-references",
        "result": "correference_report_generated",
        "demand": context["demand"],
        "matches": matches,
        "blocked_ambiguous_ids": [m["id"] for m in matches if not m["activation"]],
        "matching_policy": "full-normalized-title-or-explicit-id-or-path; no arbitrary partial-title matching",
    }


def handler_fixed_prompt(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "handler": "build-demand-envelope",
        "result": "demand_envelope_built",
        "demand": context["demand"],
        "instrument_ids": context["selected_ids"],
        "envelope": {
            "goal": context["demand"],
            "sources": [{"id": item_id, "path": context["catalog"][item_id]["path"], "sha256": context["source_hashes"][item_id]} for item_id in context["selected_ids"]],
            "execution_status": "specialized_handler_completed",
            "external_operation_status": "not_requested_by_this_handler",
        },
    }


def handler_future_preconfiguration(context: dict[str, Any]) -> dict[str, Any]:
    structured = context["structured_demand"]
    canonical = json.dumps(structured, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    request_id = structured.get("request_id") or "req-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return {
        "handler": "preserve-and-normalize-future-demand",
        "result": "future_demand_package_built",
        "request_id": request_id,
        "schema_version": structured.get("schema_version", "2.1"),
        "operation_context": structured,
        "instrument_ids": context["selected_ids"],
        "metadata_preservation": "all input fields retained in operation_context",
    }


def handler_catalog_sitemap(context: dict[str, Any]) -> dict[str, Any]:
    legacy_root = ROOT / "Promptária"
    legacy_paths = [legacy_root / "manifest.json", legacy_root / "sitemap.xml", legacy_root / "Index.html"]
    existing = [str(path.relative_to(ROOT)) for path in legacy_paths if path.is_file()]
    canonical_files = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "instruments").glob("*.md"))
    return {
        "handler": "audit-catalog-and-navigation",
        "result": "catalog_audit_completed",
        "canonical_source": "tests/manifest.json + instruments/*.md",
        "canonical_instrument_count": len(context["catalog"]),
        "markdown_files": canonical_files,
        "legacy_catalog_files_found": existing,
        "legacy_tree_available": len(existing) == len(legacy_paths),
        "sitemap_generation": "not_applicable_without_confirmed_legacy_tree_and_url_contract",
        "mutations_performed": [],
        "next_step": "validate_manifest_against_markdown_headings_before_any_catalog_write",
    }



def handler_promptaria_instrument_template(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "handler": "inspect-prepared-instrument-template",
        "result": "template_source_recovered",
        "demand": context["demand"],
        "source_path": context["catalog"][context["current_instrument_id"]]["path"],
        "source_sha256": context["source_hashes"][context["current_instrument_id"]],
        "activation_policy": "not_activated_by_inventory_or_template_presence",
        "external_side_effects": False,
    }


def handler_protocol_update_integrity(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "handler": "build-integrity-preservation-plan",
        "result": "integrity_plan_built",
        "demand": context["demand"],
        "source_sha256": context["source_hashes"][context["current_instrument_id"]],
        "checks": ["canonical_identity", "title_consistency", "aliases", "relations", "catalog_sync", "manifest_sync"],
        "external_side_effects": False,
    }


def handler_nocturna_architecture(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "handler": "recover-nocturna-architecture-source",
        "result": "architecture_source_recovered",
        "demand": context["demand"],
        "source_sha256": context["source_hashes"][context["current_instrument_id"]],
        "provenance_status": "local_markdown_recovered_external_collections_not_verified",
        "external_side_effects": False,
    }


HANDLERS = {
    "github-operational": handler_github_operational,
    "coordinator": handler_coordinator,
    "master-activation": handler_master_activation,
    "master-execution": handler_master_execution,
    "functional-correference-architecture": handler_functional_correference,
    "future-demand-preconfiguration": handler_future_preconfiguration,
    "catalog-sitemap-preconfiguration": handler_catalog_sitemap,
    "promptaria-instrument-template": handler_promptaria_instrument_template,
    "protocol-update-integrity": handler_protocol_update_integrity,
    "nocturna-arquitetura-necessidade-identidade-sistemica": handler_nocturna_architecture,
}


def execute(payload: dict[str, Any], preflight: dict[str, Any] | None = None) -> dict[str, Any]:
    catalog, mapped = load_catalog()
    demand_value = payload.get("request", payload.get("demand", payload))
    if isinstance(demand_value, dict):
        demand_text = json.dumps(demand_value, ensure_ascii=False, sort_keys=True)
    elif isinstance(demand_value, str) and demand_value.strip():
        demand_text = demand_value.strip()
    else:
        raise SystemExit("A demanda deve ser texto não vazio ou objeto JSON estruturado.")

    raw_ids = payload.get("instrument_ids", [])
    if isinstance(raw_ids, str):
        raw_ids = [raw_ids]
    if not isinstance(raw_ids, list) or any(not isinstance(item, str) for item in raw_ids):
        raise SystemExit("instrument_ids deve ser uma lista de IDs textuais.")
    # A supplied preflight file is caller-controlled input, not an authority for
    # instrument identity. Always resolve against the live canonical catalogs.
    matches = resolve_ids(demand_text, catalog)
    if preflight is not None:
        # Some internal callers pass derived preflight metadata without the
        # original request field. When present, that field must still match.
        preflight_request = preflight.get("request")
        if preflight_request is not None and (
            not isinstance(preflight_request, str)
            or normalize(preflight_request) != normalize(demand_text)
        ):
            raise SystemExit("Pré-validação recusada: a demanda não corresponde ao pedido executado.")
        # Deliberately do not use caller-supplied matched_instruments for
        # selection or identity. Canonical matches above are recomputed locally.
    if raw_ids:
        selected_ids = list(dict.fromkeys(raw_ids))
    else:
        selected_ids = list(dict.fromkeys(m["id"] for m in matches if m.get("activation", True)))
    if not selected_ids:
        raise SystemExit("Nenhum instrumento resolvido. Informe um ID explícito ou um título canônico completo.")
    unknown = sorted(set(selected_ids) - set(catalog))
    if unknown:
        raise SystemExit("IDs de instrumento desconhecidos: " + ", ".join(unknown))

    registry = index_catalog_entries(
        read_object(ROOT / "config" / "instrument-registry.json"),
        "config/instrument-registry.json",
    )
    disabled = sorted(
        item_id for item_id in selected_ids
        if not isinstance(registry[item_id].get("activation"), dict)
        or registry[item_id]["activation"].get("enabled") is not True
    )
    if disabled:
        raise SystemExit("Instrumentos não ativados no registro: " + ", ".join(disabled))

    ambiguous = [m["id"] for m in matches if m.get("identity_status") not in (None, "resolved") and m["id"] in selected_ids]
    if ambiguous and not raw_ids:
        raise SystemExit("Título ambíguo; forneça instrument_ids explicitamente para desambiguar: " + ", ".join(ambiguous))

    sources: dict[str, str] = {}
    hashes: dict[str, str] = {}
    for item_id in selected_ids:
        item = catalog[item_id]
        relative_path = Path(item["path"])
        if relative_path.is_absolute():
            raise SystemExit(f"Caminho de fonte deve ser relativo ao repositório para {item_id}: {item['path']}")
        path = (ROOT / relative_path).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise SystemExit(f"Caminho de fonte escapa do repositório para {item_id}: {item['path']}") from exc
        try:
            source_bytes = path.read_bytes()
            source = source_bytes.decode("utf-8")
        except OSError as exc:
            raise SystemExit(f"Fonte indisponível para {item_id}: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise SystemExit(f"Fonte não é UTF-8 válida para {item_id}: {item['path']}") from exc
        first_heading = next((line[2:].strip() for line in source.splitlines() if line.startswith("# ")), None)
        if first_heading != item["title"]:
            raise SystemExit(f"Título físico divergente do manifesto para {item_id}: {item['path']}")
        sources[item_id] = source
        # Hash the exact physical bytes, not decoded/re-encoded text, so CRLF and
        # other byte-level changes cannot be hidden by universal-newline handling.
        hashes[item_id] = hashlib.sha256(source_bytes).hexdigest()

    context = {
        "payload": payload,
        "structured_demand": demand_value if isinstance(demand_value, dict) else payload,
        "demand": demand_text,
        "selected_ids": selected_ids,
        "matches": matches,
        "catalog": catalog,
        "sources": sources,
        "source_hashes": hashes,
        "source": sources[selected_ids[0]],
        "source_sha256": hashes[selected_ids[0]],
    }
    results = []
    for item_id in selected_ids:
        mapped_item = mapped[item_id]
        executor_path = mapped_item.get("specialized_executor")
        if executor_path != "scripts/promptaria_specialized_executor.py" or mapped_item.get("specialized_execution_status") != "implemented":
            raise SystemExit(f"Executor especializado não está habilitado no mapa para {item_id}.")
        handler = HANDLERS.get(item_id)
        if handler is None or mapped_item.get("specialized_handler") != handler.__name__:
            raise SystemExit(f"Handler dedicado ausente ou divergente no mapa para {item_id}.")
        result = handler({**context, "current_instrument_id": item_id})
        results.append({
            "instrument_id": item_id,
            "instrument_title": catalog[item_id]["title"],
            "executor": executor_path,
            "handler": result["handler"],
            "execution_status": "completed",
            "source_path": catalog[item_id]["path"],
            "source_sha256": hashes[item_id],
            "result": result,
            "side_effects": [],
        })

    return {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request_id": payload.get("request_id"),
        "demand": demand_text,
        "selected_instrument_ids": selected_ids,
        "execution_status": "completed",
        "specialized_execution_count": len(results),
        "external_side_effects_performed": False,
        "results": results,
    }


def validate_output_path(output: Path, input_paths: list[Path]) -> Path:
    """Refuse output paths that overwrite inputs or repository source/config files."""
    resolved = output.resolve()
    for input_path in input_paths:
        if input_path is not None and resolved == input_path.resolve():
            raise SystemExit(f"Caminho de saída não pode sobrescrever uma entrada: {output}")

    try:
        relative = resolved.relative_to(ROOT.resolve())
    except ValueError:
        return resolved

    # Repository-local generated artifacts must stay in designated output areas.
    allowed_roots = {"artifacts", "build", "dist", "out"}
    if not relative.parts or relative.parts[0] not in allowed_roots:
        raise SystemExit(
            "Caminho de saída dentro do repositório deve estar em artifacts/, build/, dist/ ou out/: "
            f"{output}"
        )
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path, help="JSON object with request/demand and optional instrument_ids")
    parser.add_argument("--preflight", type=Path, help="Optional output from promptaria_preflight.py")
    parser.add_argument("--output", required=True, type=Path, help="Output JSON path")
    args = parser.parse_args()
    output_path = validate_output_path(
        args.output,
        [args.request, *([args.preflight] if args.preflight else [])],
    )
    payload = read_object(args.request)
    preflight = read_object(args.preflight) if args.preflight else None
    result = execute(payload, preflight)
    atomic_json(output_path, result)
    print(json.dumps({
        "status": result["execution_status"],
        "specialized_execution_count": result["specialized_execution_count"],
        "instrument_ids": result["selected_instrument_ids"],
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
