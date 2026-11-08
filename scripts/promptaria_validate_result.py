#!/usr/bin/env python3
"""Fail closed when a Promptária resolution artifact is incomplete or misstates execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(result: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(result, dict):
        return ["O resultado deve ser um objeto JSON."]
    if result.get("schema_version") != 2:
        errors.append("schema_version deve ser 2.")
    mandatory = result.get("mandatory_components")
    if not isinstance(mandatory, list):
        errors.append("mandatory_components deve ser uma lista.")
        mandatory = []
    if len(mandatory) != 3 or any(not isinstance(item, dict) or item.get("found") is not True for item in mandatory):
        errors.append("Os três componentes obrigatórios precisam estar presentes.")
    missing = result.get("missing_mandatory_components")
    if not isinstance(missing, list) or missing:
        errors.append("missing_mandatory_components deve estar vazio.")
    matches = result.get("matched_instruments")
    if not isinstance(matches, list):
        errors.append("matched_instruments deve ser uma lista.")
        matches = []
    for index, item in enumerate(matches):
        if not isinstance(item, dict):
            errors.append(f"matched_instruments[{index}] deve ser um objeto.")
            continue
        if item.get("content_recovered") is not True:
            errors.append(f"matched_instruments[{index}] não confirma recuperação do conteúdo.")
        if item.get("activation_status") not in {"recognized_not_executed", "included_in_plan_not_executed"}:
            errors.append(f"matched_instruments[{index}] contém estado de ativação inválido.")
    if result.get("write_execution_available") is not False:
        errors.append("O resolvedor não pode declarar execução de escrita disponível.")
    if result.get("status") != "plan_created_needs_execution_integration":
        errors.append("O estado final do resolvedor é inesperado.")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = json.loads(args.result.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Artefato JSON inválido ou inacessível: {exc}")
    errors = validate(result)
    if errors:
        raise SystemExit("Validação do resultado falhou:\n- " + "\n- ".join(errors))
    print("Resultado validado: 3 componentes obrigatórios, conteúdo recuperado e nenhuma execução alegada.")


if __name__ == "__main__":
    main()
