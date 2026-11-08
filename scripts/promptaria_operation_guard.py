#!/usr/bin/env python3
"""Enforce Promptária's separation between operational instruments and architecture traceability."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INSTRUMENT = ROOT / "instruments" / "acione-a-promptaria-pelo-github.md"
DEFAULT_REGISTRY = ROOT / "config" / "instrument-registry.json"

# These architecture-specific sections belong in the canonical registry/architecture,
# not inside the operational prompt instrument. Ordinary operational traceability stays valid.
FORBIDDEN_INSTRUMENT_MARKERS = (
    "## Identidade e rastreabilidade canônica",
    "## Interconexão com correspondência por título, protocolo-mestre e pré-configuração padrão",
    "rastreabilidade bidirecional entre segmento, ID, nó, fonte, operação e evidência",
)

REQUIRED_RELATIONS = (
    "functional-correference-architecture->github-operational",
    "github-operational->functional-correference-architecture",
    "future-demand-preconfiguration->github-operational",
    "github-operational->future-demand-preconfiguration",
    "master-activation->github-operational",
    "master-protocol-fixed-instrument->github-operational",
    "master-preconfiguration->github-operational",
)


def check(instrument_path: Path, registry_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        instrument = instrument_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"Não foi possível ler o instrumento operacional: {exc}"]

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Registro canônico ausente ou inválido: {exc}"]

    for marker in FORBIDDEN_INSTRUMENT_MARKERS:
        if marker.casefold() in instrument.casefold():
            errors.append(
                f"O instrumento operacional contém material arquitetônico reservado ao registro: {marker}"
            )

    entries = registry.get("instruments")
    if not isinstance(entries, list):
        return errors + ["O registro canônico precisa conter uma lista 'instruments'."]

    by_id = {
        item.get("id"): item
        for item in entries
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    operational = by_id.get("github-operational")
    if not isinstance(operational, dict):
        errors.append("A identidade canônica 'github-operational' está ausente do registro.")
    else:
        if operational.get("path") != "instruments/acione-a-promptaria-pelo-github.md":
            errors.append("O caminho canônico de 'github-operational' foi alterado inesperadamente.")
        activation = operational.get("activation", {})
        if not isinstance(activation, dict) or activation.get("enabled") is not True:
            errors.append("'github-operational' precisa continuar habilitado para resolução funcional.")

    relations = {
        relation
        for item in entries if isinstance(item, dict)
        for relation in item.get("relations", [])
        if isinstance(relation, str)
    }
    for relation in REQUIRED_RELATIONS:
        if relation not in relations:
            errors.append(f"Relação estrutural de rastreabilidade ausente no registro canônico: {relation}")

    for required_id in ("functional-correference-architecture", "future-demand-preconfiguration", "master-activation"):
        if required_id not in by_id:
            errors.append(f"Identidade arquitetônica/de pré-configuração ausente do registro: {required_id}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instrument", type=Path, default=DEFAULT_INSTRUMENT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()
    errors = check(args.instrument, args.registry)
    if errors:
        print("PROMPTÁRIA OPERATION GUARD: FALHA")
        for error in errors:
            print(f"- {error}")
        print("A alteração deve ser corrigida antes de ser integrada.")
        return 1
    print("PROMPTÁRIA OPERATION GUARD: OK")
    print("Separação operacional/arquitetural preservada; relações canônicas verificadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
