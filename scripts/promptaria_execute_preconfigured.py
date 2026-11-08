#!/usr/bin/env python3
"""Run the generic writer using a matching eligible Promptária preflight plan.

The plan may supply scoped write authorization, but cannot bypass dry_run=false,
the artifacts/ boundary, the permissions registry, or operation confirmation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from promptaria_executor import execute, load_json
from promptaria_preflight import assess_preauthorization, resolve_request


ROOT = Path(__file__).resolve().parents[1]


def authorize_from_preflight(payload: dict, preflight: dict) -> dict:
    request = payload.get("request")
    destination = payload.get("destination")
    if not isinstance(request, str) or preflight.get("request") != request:
        raise SystemExit("Pré-autorização recusada: texto da demanda diverge do plano.")
    if preflight.get("destination") != destination:
        raise SystemExit("Pré-autorização recusada: destino do pedido diverge do plano.")
    reported_assessment = preflight.get("preauthorization", {})
    if reported_assessment.get("write_authorized") is not True or reported_assessment.get("status") != "scoped_preauthorization_eligible":
        raise SystemExit("Pré-autorização recusada: o plano fornecido não está elegível.")
    manifest = load_json(ROOT / "tests" / "manifest.json")
    execution_map = load_json(ROOT / "config" / "instrument-execution-map.json")
    canonical_matches = resolve_request(request, manifest, execution_map)
    assessment = assess_preauthorization(request, canonical_matches, destination)
    if assessment.get("write_authorized") is not True or assessment.get("status") != "scoped_preauthorization_eligible":
        raise SystemExit("Pré-autorização recusada: a revalidação canônica não é elegível.")
    if payload.get("operation") != "write_text":
        raise SystemExit("Pré-autorização recusada: somente write_text é permitido.")
    if payload.get("dry_run", True) is not False:
        raise SystemExit("Para efetuar a escrita, o pedido precisa declarar dry_run=false.")
    if not any(item.get("activation") is True for item in canonical_matches):
        raise SystemExit("Pré-autorização recusada: nenhum instrumento ativo no plano.")
    authorized = dict(payload)
    authorized["write_authorized"] = True
    authorized["authorization_source"] = "eligible_master_protocol_preflight"
    return authorized


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path, help="Pedido do executor em JSON")
    parser.add_argument("--preflight", required=True, type=Path, help="Plano gerado por promptaria_preflight.py")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--permissions", type=Path, default=Path(__file__).resolve().parents[1] / "config" / "promptaria_permissions.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--confirm-operation", required=True)
    args = parser.parse_args()
    payload = load_json(args.request)
    preflight = load_json(args.preflight)
    payload = authorize_from_preflight(payload, preflight)
    registry = load_json(args.permissions)
    result = execute(payload, args.repo_root.resolve(), registry, args.confirm_operation)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
