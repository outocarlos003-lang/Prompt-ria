#!/usr/bin/env python3
"""Classify incoming Promptária requests before choosing title resolution or automation planning.

This router is deliberately conservative: only enabled registry entries may trigger
functional title coreference. Automation-preconfiguration requests remain a separate
route and do not implicitly activate or resolve inactive/unregistered instruments.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char)).casefold()
    value = re.sub(r"[\u200b-\u200f\ufeff]", "", value)
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"[\s-]+", " ", value).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    term = normalize(phrase)
    return bool(term and re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text))


AUTOMATION_PATTERNS = (
    r"\bpre configur\w*\b",
    r"\bpreconfigur\w*\b",
    r"\bautomatiz\w*\b",
    r"\bautomacao\b",
    r"\bworkflow\b",
    r"\bgithub actions\b",
    r"\bgatilho\w*\b",
    r"\bsincroniz\w*\b",
    r"\bpipeline\b",
    r"\brotina automatica\b",
    r"\bfuncao distinta\b",
    r"\bpreserv\w* func\w*\b",
    r"\bimplementar atualiz\w*\b",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--registry", type=Path, default=Path("config/instrument-registry.json"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.request.read_text(encoding="utf-8"))
    request = payload.get("request", "")
    if not isinstance(request, str) or not request.strip():
        raise SystemExit("Demanda vazia ou inválida para classificação.")
    normalized_request = normalize(request)

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    active_hits = []
    inactive_hits = []
    active_ids = []
    for item in registry.get("instruments", []):
        if not isinstance(item, dict):
            continue
        enabled = item.get("activation", {}).get("enabled") is True
        terms = [item.get("title", ""), *item.get("aliases", [])]
        hits = [term for term in terms if isinstance(term, str) and contains_phrase(normalized_request, term)]
        if hits:
            target = active_hits if enabled else inactive_hits
            target.append({"id": item.get("id"), "title": item.get("title"), "matched_terms": hits})
            if enabled:
                active_ids.append(item.get("id"))

    automation_intent = any(re.search(pattern, normalized_request) for pattern in AUTOMATION_PATTERNS)
    if active_hits and automation_intent:
        route = "mixed_coreference_and_automation_preconfiguration"
        rationale = "Há título(s) ativo(s) explícito(s) e intenção distinta de pré-configuração de automação."
    elif active_hits:
        route = "title_coreference"
        rationale = "A demanda menciona explicitamente pelo menos um instrumento habilitado no registry."
    elif inactive_hits:
        route = "inactive_or_unregistered_reference"
        rationale = "A referência aponta para instrumento desativado; não será resolvida por correferência funcional."
    elif automation_intent:
        route = "automation_preconfiguration"
        rationale = "A demanda solicita automação/pré-configuração; não há título ativo explícito para correferência."
    else:
        route = "unclassified_requires_review"
        rationale = "Não há sinal suficiente para escolher com segurança entre correferência e pré-configuração."

    result = {
        "schema_version": 1,
        "route": route,
        "request": request,
        "rationale": rationale,
        "active_title_matches": active_hits,
        "inactive_title_matches": inactive_hits,
        "automation_preconfiguration_intent": automation_intent,
        "allowed_coreference_ids": sorted(set(active_ids)),
        "policy": {
            "registry_is_authoritative": True,
            "only_activation_enabled_true_can_resolve_by_title": True,
            "inactive_or_unregistered_instruments_keep_separate_automation_functions": True,
            "automation_preconfiguration_does_not_activate_or_resolve_instruments": True,
            "classification_is_a_plan_not_execution": True,
        },
        "next_action": {
            "title_coreference": "run_title_resolver",
            "mixed_coreference_and_automation_preconfiguration": "run_title_resolver_and_emit_separate_automation_plan",
            "automation_preconfiguration": "emit_automation_preconfiguration_plan_only",
            "inactive_or_unregistered_reference": "block_coreference_and_request_explicit_automation_scope",
            "unclassified_requires_review": "request_contextual_classification_before_action",
        }[route],
        "execution_performed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    github_output = __import__("os").environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"route={route}\n")
    print(f"Classificação da demanda: {route}")
    print(rationale)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
