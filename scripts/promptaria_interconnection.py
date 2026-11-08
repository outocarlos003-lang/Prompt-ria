#!/usr/bin/env python3
"""Build independent, phase-aware links between semantically related instruments."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "instrument-registry.json"
STOP = {"para", "com", "sem", "entre", "cada", "pela", "pelo", "uma", "um", "das", "dos", "que", "deve", "ser", "como", "quando", "the", "and"}
CONCEPTS = {
    "title_correspondence": {"titulo", "titulos", "correferencia", "correferenciar", "correspondencia", "resolver", "resolucao", "identidade", "alias"},
    "coordination": {"coordenar", "coordenacao", "acionamento", "acionar", "protocolo", "ordenar", "integrar", "integracao"},
    "traceability": {"rastreabilidade", "rastrear", "proveniencia", "evidencia", "validar", "validacao", "verificar", "verificacao", "cadeia"},
    "demand_preparation": {"demanda", "solicitacao", "request", "preconfigurar", "preconfiguracao", "preparar", "envelope", "contexto"},
    "repository_operations": {"github", "repositorio", "arquivo", "inspecionar", "localizar", "executar", "operacao", "operacoes"},
    "catalog_discovery": {"catalogo", "sitemap", "indice", "navegacao", "descoberta", "manifesto"},
    "structural_reconstruction": {"reconstruir", "arquitetura", "estrutura", "derivacao", "fundamento", "funcao", "funcoes"},
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^\\w\\s-]", " ", text, flags=re.UNICODE).replace("-", " ").strip()


def _values(item: dict, field: str) -> set[str]:
    raw = item.get(field, [])
    if not isinstance(raw, list):
        return set()
    return {normalize(value) for value in raw if isinstance(value, str) and normalize(value)}


def tokens(item: dict) -> set[str]:
    values = [item.get("title", ""), *item.get("aliases", []), *item.get("keywords", []), *item.get("functions", [])]
    raw = set()
    for value in values:
        if isinstance(value, str):
            raw.update(re.findall(r"[a-z0-9_]+", normalize(value)))
    return {token for token in raw if len(token) > 2 and token not in STOP}


def concepts(item: dict) -> set[str]:
    words = tokens(item)
    return {name for name, vocabulary in CONCEPTS.items() if words & vocabulary}


def _pair_evidence(left: dict, right: dict) -> dict | None:
    functions = sorted(_values(left, "functions") & _values(right, "functions"))
    operations = sorted(_values(left, "operations") & _values(right, "operations"))
    keywords = sorted(_values(left, "keywords") & _values(right, "keywords"))
    shared_concepts = sorted(concepts(left) & concepts(right))
    # Exact functional/operational correspondence is strongest. Two shared
    # keywords or a common semantic concept also establish a catalogue relation.
    qualifies = bool(functions or operations or len(keywords) >= 2 or shared_concepts)
    if not qualifies:
        return None
    score = 3 * len(functions) + 3 * len(operations) + len(keywords) + 2 * len(shared_concepts)
    return {
        "shared_functions": functions,
        "shared_operations": operations,
        "shared_keywords": keywords,
        "shared_concepts": shared_concepts,
        "evidence_score": score,
        "matching_basis": (
            "exact_shared_function" if functions else
            "exact_shared_operation" if operations else
            "two_or_more_shared_keywords" if len(keywords) >= 2 else
            "shared_semantic_concept"
        ),
    }


def build(registry: dict, selected_on_demand_ids=None, request_id=None) -> dict:
    items = registry.get("instruments", [])
    continuous = [
        item for item in items if isinstance(item, dict)
        and item.get("activation", {}).get("enabled") is True
        and item.get("category") == "continuous_automation"
    ]
    recoverable = [
        item for item in items if isinstance(item, dict)
        and item.get("activation", {}).get("enabled") is True
        and item.get("category") == "recoverable_on_demand"
    ]
    selected = set(selected_on_demand_ids or [])
    links = []
    for continuous_item in continuous:
        for on_demand_item in recoverable:
            evidence = _pair_evidence(continuous_item, on_demand_item)
            if evidence is None:
                continue
            continuous_id = continuous_item["id"]
            on_demand_id = on_demand_item["id"]
            pair_id = f"cross-segment:{continuous_id}:{on_demand_id}"
            digest = hashlib.sha256(pair_id.encode("utf-8")).hexdigest()[:16]
            links.append({
                "link_id": pair_id,
                "pair_id": pair_id,
                "correlation_id": f"corr-{digest}",
                "shared_node_id": f"coordination:cross-segment:{continuous_id}:{on_demand_id}",
                "request_id": request_id,
                "continuous_instrument": {
                    "id": continuous_id,
                    "node_id": continuous_item.get("ui", {}).get("node_id"),
                    "path": continuous_item.get("path"),
                    "title": continuous_item.get("title"),
                    "functions_preserved": list(continuous_item.get("functions", [])),
                    "phase": "phase_1_continuous_preconfiguration",
                },
                "recoverable_instrument": {
                    "id": on_demand_id,
                    "node_id": on_demand_item.get("ui", {}).get("node_id"),
                    "path": on_demand_item.get("path"),
                    "title": on_demand_item.get("title"),
                    "functions_preserved": list(on_demand_item.get("functions", [])),
                    "phase": "phase_2_demand_time_recovery",
                },
                "evidence": evidence,
                "shared_concepts": evidence["shared_concepts"],
                "shared_nodes": [
                    f"correlation:{digest}",
                    f"procedure:{digest}",
                    f"trace:{digest}",
                ],
                "relations": [
                    {"from": f"instrument:{continuous_id}", "to": f"instrument:{on_demand_id}", "type": "continuous_to_on_demand"},
                    {"from": f"instrument:{on_demand_id}", "to": f"instrument:{continuous_id}", "type": "on_demand_to_continuous"},
                    {"from": "phase:continuous_preconfiguration", "to": "phase:on_demand_recovery", "type": "phase_1_precedes_phase_2"},
                    {"from": f"instrument:{continuous_id}", "to": f"instrument:{on_demand_id}", "type": "preserves_independent_identity"},
                ],
                "phase_status": {
                    "continuous_preconfiguration": "context_preconfigured_not_executed",
                    "on_demand_recovery": "selected_for_request" if on_demand_id in selected else "candidate_not_selected",
                },
                "interconnection_status": "interconnected_for_request" if on_demand_id in selected else "catalogue_relation_only",
                "interconnection": [
                    "continuous_preconfiguration->shared_procedure_node",
                    "shared_procedure_node->demand_time_recovery",
                    "demand_time_recovery->shared_trace_node",
                    "shared_trace_node->independent_instrument_results",
                ],
                "preservation": {
                    "instrument_count_unchanged": True,
                    "identities_and_ids_independent": True,
                    "functions_and_operations_independent": True,
                    "source_paths_unchanged": True,
                    "execution_phase_separated": True,
                },
                "procedure": {
                    "phase_1": "O instrumento contínuo prepara contexto, critérios, dependências e referências; não substitui nem executa automaticamente a função do instrumento recuperável.",
                    "phase_2": "Quando a demanda recuperar o instrumento correspondente, o procedimento compartilhado transfere apenas contexto e referências rastreáveis; a função própria do recuperável permanece soberana.",
                    "phase_3": "Os resultados são correlacionados pelo correlation_id, request_id e nós compartilhados, mantendo autoria, estado e evidências separados por instrumento.",
                },
                "identity_merge": False,
                "instrument_count_delta": 0,
            })
    links.sort(key=lambda item: (-item["evidence"]["evidence_score"], item["pair_id"]))
    return {
        "schema_version": 1,
        "algorithm": "deterministic_exact_metadata_and_semantic_concept_intersection",
        "request_id": request_id,
        "phase_order": ["continuous_preconfiguration", "on_demand_recovery", "cross_instrument_trace_reconciliation"],
        "policy": {
            "similarity_is_interconnection_not_merger": True,
            "no_instrument_is_created_deleted_renamed_or_relocated": True,
            "function_and_operation_contracts_remain_independent": True,
            "shared_ids_are_correlation_ids_not_replacement_instrument_ids": True,
            "no_implicit_execution_or_write_authorization": True,
            "unmatched_pairs_remain_independent_without_forced_links": True,
        },
        "continuous_instrument_count": len(continuous),
        "recoverable_instrument_count": len(recoverable),
        "interconnection_count": len(links),
        "selected_interconnection_count": sum(link["interconnection_status"] == "interconnected_for_request" for link in links),
        "independent_instrument_count_preserved": True,
        "independent_ids_and_paths_preserved": True,
        "independent_functions_preserved": True,
        "side_effects_authorized": False,
        "matching_activates_instruments": False,
        "interconnections": links,
    }


if __name__ == "__main__":
    registry_data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    print(json.dumps(build(registry_data), ensure_ascii=False, indent=2))
