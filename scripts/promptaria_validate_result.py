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
    preconfiguration = result.get("preconfiguration")
    if preconfiguration is not None:
        if not isinstance(preconfiguration, dict):
            errors.append("preconfiguration deve ser um objeto.")
        else:
            if preconfiguration.get("complete") is not True:
                errors.append("A pré-configuração não está completa.")
            expected = {
                "functional-correference-architecture": (
                    "instruments/arquitetura-unificada-acionamento-correferencia-recuperacao-aplicacao.md",
                    "continuous_automation",
                ),
                "master-activation": (
                    "instruments/protocolo-mestre-acionamento-automatico.md",
                    "continuous_automation",
                ),
                "github-operational": (
                    "instruments/acione-a-promptaria-pelo-github.md",
                    "recoverable_on_demand",
                ),
            }
            ids = [item.get("id") for item in mandatory if isinstance(item, dict)]
            if len(ids) != 3 or set(ids) != set(expected):
                errors.append("Os componentes-base devem corresponder exatamente aos três IDs canônicos.")
            for item in mandatory:
                if not isinstance(item, dict):
                    continue
                spec = expected.get(item.get("id"))
                if spec is None:
                    continue
                if item.get("path") != spec[0] or item.get("category") != spec[1]:
                    errors.append(f"Componente-base {item.get('id')} diverge de categoria ou caminho canônico.")
            if preconfiguration.get("mandatory_component_ids") is not None and set(preconfiguration.get("mandatory_component_ids", [])) != set(expected):
                errors.append("preconfiguration.mandatory_component_ids diverge dos três componentes-base.")
            continuous = preconfiguration.get("continuous_context")
            if not isinstance(continuous, list):
                errors.append("preconfiguration.continuous_context deve ser uma lista.")
                continuous = []
            continuous_by_id = {}
            for item in continuous:
                if not isinstance(item, dict):
                    errors.append("Cada item do contexto contínuo deve ser um objeto.")
                    continue
                item_id = item.get("id")
                if not isinstance(item_id, str) or item_id in continuous_by_id:
                    errors.append("O contexto contínuo contém ID ausente ou duplicado.")
                    continue
                continuous_by_id[item_id] = item
                if (
                    item.get("category") != "continuous_automation"
                    or item.get("loaded_as_context") is not True
                    or item.get("title_resolvable") is not False
                    or item.get("execution_performed") is not False
                    or not isinstance(item.get("content"), str)
                    or not item.get("content", "").strip()
                ):
                    errors.append(f"Contexto contínuo inválido ou executado indevidamente: {item_id}.")
            if not {"functional-correference-architecture", "master-activation"}.issubset(continuous_by_id):
                errors.append("Arquitetura coordenadora e protocolo-mestre devem estar no contexto contínuo.")
            if preconfiguration.get("continuous_context_complete") is not True:
                errors.append("O contexto contínuo está incompleto.")
            context_ids = preconfiguration.get("continuous_context_ids")
            if not isinstance(context_ids, list) or set(context_ids) != set(continuous_by_id):
                errors.append("continuous_context_ids não corresponde ao contexto carregado.")
            fixed = preconfiguration.get("fixed_operational_component")
            if (
                not isinstance(fixed, dict)
                or fixed.get("id") != "github-operational"
                or fixed.get("category") != "recoverable_on_demand"
                or fixed.get("path") != expected["github-operational"][0]
                or fixed.get("execution_performed") is not False
                or not isinstance(fixed.get("content"), str)
                or not fixed.get("content", "").strip()
            ):
                errors.append("O componente operacional fixo do GitHub está ausente ou inválido.")

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
