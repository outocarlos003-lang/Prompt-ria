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
    return "".join(c for c in text if not unicodedata.combining(c))

def tokens(item: dict) -> set[str]:
    values = [item.get("title", ""), *item.get("aliases", []), *item.get("keywords", []), *item.get("functions", [])]
    raw = set()
    for value in values:
        if isinstance(value, str):
            raw.update(re.findall(r"[a-z0-9_]+", normalize(value)))
    return {t for t in raw if len(t) > 2 and t not in STOP}

def concepts(item: dict) -> set[str]:
    words = tokens(item)
    found = set()
    for concept, vocabulary in CONCEPTS.items():
        if words & vocabulary:
            found.add(concept)
    return found

def build(registry: dict) -> dict:
    instruments = registry.get("instruments", [])
    continuous = [x for x in instruments if x.get("activation", {}).get("enabled") is True and x.get("category") == "continuous_automation"]
    recoverable = [x for x in instruments if x.get("activation", {}).get("enabled") is True and x.get("category") == "recoverable_on_demand"]
    links = []
    for c in continuous:
        for r in recoverable:
            shared = sorted(concepts(c) & concepts(r))
            if not shared:
                continue
            identity = f"cross-category:{c['id']}:{r['id']}"
            digest = hashlib.sha256(identity.encode()).hexdigest()[:16]
            links.append({
                "link_id": identity,
                "correlation_id": f"corr-{digest}",
                "continuous_instrument": {"id": c["id"], "node_id": c.get("ui", {}).get("node_id"), "path": c["path"], "phase": "phase_1_continuous_preconfiguration"},
                "recoverable_instrument": {"id": r["id"], "node_id": r.get("ui", {}).get("node_id"), "path": r["path"], "phase": "phase_2_demand_time_recovery"},
                "shared_concepts": shared,
                "shared_nodes": [f"correlation:{digest}", f"procedure:{digest}", f"trace:{digest}"],
                "interconnection": [
                    "continuous_preconfiguration->shared_procedure_node",
                    "shared_procedure_node->demand_time_recovery",
                    "demand_time_recovery->shared_trace_node",
                    "shared_trace_node->independent_instrument_results"
                ],
                "preservation": {
                    "instrument_count_unchanged": True,
                    "identities_and_ids_independent": True,
                    "functions_and_operations_independent": True,
                    "source_paths_unchanged": True,
                    "execution_phase_separated": True
                },
                "procedure": {
                    "phase_1": "O instrumento contínuo prepara contexto, critérios, dependências e referências; não substitui nem executa automaticamente a função do instrumento recuperável.",
                    "phase_2": "Quando a demanda recuperar o instrumento correspondente, o procedimento compartilhado transfere apenas contexto e referências rastreáveis; a função própria do recuperável permanece soberana.",
                    "phase_3": "Os resultados são correlacionados pelo correlation_id e pelos nós compartilhados, mantendo autoria, estado e evidências separados por instrumento."
                }
            })
    return {
        "schema_version": 1,
        "algorithm": "deterministic_concept_vocabulary_intersection",
        "phase_order": ["continuous_preconfiguration", "demand_time_recovery", "cross_instrument_trace_reconciliation"],
        "policy": {
            "similarity_is_interconnection_not_merger": True,
            "no_instrument_is_created_deleted_renamed_or_relocated": True,
            "function_and_operation_contracts_remain_independent": True,
            "shared_ids_are_correlation_ids_not_replacement_instrument_ids": True,
            "no_implicit_execution_or_write_authorization": True,
            "unmatched_pairs_remain_independent_without_forced_links": True
        },
        "continuous_instrument_count": len(continuous),
        "recoverable_instrument_count": len(recoverable),
        "interconnection_count": len(links),
        "interconnections": links
    }

if __name__ == "__main__":
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    print(json.dumps(build(registry), ensure_ascii=False, indent=2))
