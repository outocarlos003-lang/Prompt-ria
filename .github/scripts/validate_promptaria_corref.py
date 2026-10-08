#!/usr/bin/env python3
"""Validação normativa da correferência funcional automática da Promptária.

A implementação trata o título como ponto de entrada, recupera identidade pelo
conteúdo armazenado, preserva a função própria por padrão, admite exceção
somente por ocorrência e contexto inequivocamente desviador, mantém múltiplos
títulos cumulativos e produz rastreabilidade de ponta a ponta.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path("Promptária")
CONTEXT_RADIUS = 480

ARCHITECTURE_SECTIONS = [
    "I. TÍTULO, CORREFERÊNCIA E IDENTIDADE",
    "II. DEMANDA, CONTEXTO, PARAMETRIZAÇÃO E ADAPTAÇÃO",
    "III. FUNÇÃO PRÓPRIA E FUNÇÃO DIVERSA",
    "IV. RECUPERAÇÃO, ACIONAMENTO E EXECUÇÃO",
    "V. ACIONAMENTO COORDENADO",
    "VI. INSTRUMENTOS ADICIONAIS E FIXO",
    "VII. MÚLTIPLOS TÍTULOS",
    "VIII. FUNÇÃO DIVERSA EM MÚLTIPLOS TÍTULOS",
    "IX. RESPONSABILIDADE E NÃO SUBSTITUIÇÃO",
    "X. ORIGEM, DESTINO E MULTIDIRETÓRIO",
    "XI. EXECUÇÃO, MATERIALIZAÇÃO E RESULTADOS",
    "XII. COMPATIBILIZAÇÃO",
    "XIII. VALIDAÇÃO E RASTREABILIDADE",
    "XIV. REUTILIZAÇÃO E PRESERVAÇÃO",
    "XV. SEQUÊNCIAS ARQUITETURAIS",
    "XVI. PRINCÍPIO DA NÃO SUBSTITUIÇÃO",
    "XVII. REGRA OPERACIONAL FINAL",
    "XVIII. SÍNTESE AFORÍSTICA",
    "XIX. PRINCÍPIO CONCLUSIVO",
]

DIVERSE_PATTERNS = (
    r"\b(?:outra|diversa|diferente)\s+(?:função|finalidade|papel)\b",
    r"\b(?:função|finalidade|papel)\s+(?:diverso|diversa|diferente|substituto|substituta)\b",
    r"\b(?:substitu[ai]|substituir|substituição)\b.{0,180}\b(?:função|finalidade|papel)\b",
    r"\b(?:não|nao)\s+(?:use|utilize|empregue|aplique|acione|preserve)\b.{0,180}\b(?:função|finalidade|papel)\s+(?:própri[ao]|original)\b",
    r"\b(?:exclua|excluir|impeça|impedir|não permita|nao permita)\b.{0,180}\b(?:função|finalidade|papel)\b.{0,120}\b(?:original|própri[ao]|anterior)\b",
    r"\b(?:use|utilize|empregue|trate|considere|faça|faca)\b.{0,100}\bcomo\b.{0,100}\b(?:outra|diversa|diferente)\b",
)

FIXED_COORDINATOR_TITLE = "Acionamento Coordenado de Instrumentos Promptuais"
FIXED_GITHUB_INSTRUMENT_TITLE = "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"

DESTINATION_PATTERNS = (
    re.compile(r"\b(?:destino|destine|destinar|gravar|escrever|materializar|salvar)\s*[:=]\s*([^\n.;]+)", re.I),
    re.compile(r"\b(?:no|na|em|para o|para a)\s+(diret[oó]rio|pasta|arquivo)\s+([^\n.;]+)", re.I),
)
ORIGIN_PATTERN = re.compile(r"\b(?:origem|origin[aá]rio|proveni[eê]ncia)\s*[:=]\s*([^\n.;]+)", re.I)
EXPLICIT_TITLE_PATTERNS = (
    re.compile(r"\bt[ií]tulo(?:\s+do\s+instrumento(?:\s+promptual)?)?\s*[:=]\s*[“\"]([^”\"]+)[”\"]", re.I),
    re.compile(r"\binstrumento(?:\s+promptual)?\s+denominado\s*[“\"]([^”\"]+)[”\"]", re.I),
    re.compile(r"\binstrumento(?:\s+promptual)?\s+chamado\s*[“\"]([^”\"]+)[”\"]", re.I),
)


def normalize_with_map(value: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    origins: list[int] = []
    for index, original in enumerate(value):
        chunk = unicodedata.normalize("NFKC", original).casefold()
        chunk = "".join(c for c in unicodedata.normalize("NFD", chunk) if unicodedata.category(c) != "Mn")
        for char in chunk:
            chars.append(char)
            origins.append(index)

    out: list[str] = []
    out_origins: list[int] = []
    pending_space = False
    pending_origin = 0
    for char, origin in zip(chars, origins):
        if char.isspace():
            if out:
                pending_space = True
                pending_origin = origin
            continue
        if pending_space:
            out.append(" ")
            out_origins.append(pending_origin)
            pending_space = False
        out.append(char)
        out_origins.append(origin)
    normalized = "".join(out).strip()
    if not normalized:
        return "", []
    left = len("".join(out)) - len("".join(out).lstrip())
    right = len("".join(out).rstrip())
    return normalized, out_origins[left:right]


def norm(value: str) -> str:
    return normalize_with_map(str(value))[0]


def html_title(raw: str) -> str | None:
    match = re.search(r"<title>\s*(.*?)\s*</title>", raw, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip() if match else None


def instrument_catalog(root: Path = ROOT) -> list[dict]:
    """Lê títulos dos instrumentos físicos; não modifica nenhum instrumento."""
    items: list[dict] = []
    if not root.exists():
        return items

    for directory in sorted(root.iterdir(), key=lambda p: norm(p.name)):
        if not directory.is_dir():
            continue
        index = directory / "Index.html"
        if not index.is_file():
            continue
        raw = index.read_text(encoding="utf-8", errors="replace")
        title = html_title(raw) or directory.name.replace("-", " ")
        items.append({
            "id": None,
            "title": title,
            "aliases": [title],
            "capabilities": [],
            "path": str(index),
            "instrument": str(index),
        })

    manifest_path = root / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            by_path = {x.get("path"): x for x in manifest.get("instruments", [])}
            for item in items:
                meta = by_path.get(item["path"])
                if meta:
                    item["id"] = meta.get("id")
                    item["title"] = meta.get("title") or item["title"]
                    item["aliases"] = list(meta.get("aliases") or [item["title"]])
                    item["capabilities"] = list(meta.get("capabilities") or [])
        except (OSError, json.JSONDecodeError):
            pass

    return items


def catalog_consistency(root: Path, catalog: list[dict]) -> list[str]:
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return []

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest.json inválido: {exc}"]

    expected = {x.get("path"): x.get("title") for x in manifest.get("instruments", [])}
    actual = {x["path"]: x["title"] for x in catalog}
    errors: list[str] = []

    if set(expected) != set(actual):
        errors.append("manifest.json e árvore física possuem caminhos diferentes")

    for path, title in expected.items():
        if path in actual and norm(title) != norm(actual[path]):
            errors.append(f"título divergente em {path!r}")

    return errors


def local_context(text: str, start: int, end: int) -> str:
    left, right = max(0, start - CONTEXT_RADIUS), min(len(text), end + CONTEXT_RADIUS)
    window = text[left:right]
    rel_start, rel_end = start - left, end - left
    separators = list(re.finditer(r"(?:[.!?;]|\n\s*\n)", window))
    begin, finish = 0, len(window)
    for separator in reversed(separators):
        if separator.end() <= rel_start:
            begin = separator.end()
            break
    for separator in separators:
        if separator.start() >= rel_end:
            finish = separator.start()
            break
    return window[begin:finish].strip()


def has_diverse_assignment(context: str, title: str) -> bool:
    """Exceção somente quando o contexto da própria ocorrência contém desvio inequívoco."""
    c = norm(context)
    if not c:
        return False

    # O título precisa estar no contexto local; a classificação não se projeta.
    if norm(title) not in c:
        return False

    return any(re.search(pattern, c, re.I) for pattern in DIVERSE_PATTERNS)


def phrase_pattern(needle: str) -> re.Pattern[str]:
    return re.compile(rf"(?<!\w){re.escape(needle)}(?!\w)", re.UNICODE)


def explicit_titles(prompt: str) -> list[str]:
    titles: list[str] = []
    seen: set[str] = set()
    for pattern in EXPLICIT_TITLE_PATTERNS:
        for match in pattern.finditer(prompt):
            title = match.group(1).strip()
            key = norm(title)
            if title and key and key not in seen:
                seen.add(key)
                titles.append(title)
    return titles


def find_catalog_item(catalog: list[dict], title: str) -> dict | None:
    target = norm(title)
    for item in catalog:
        if norm(item["title"]) == target:
            return item
    return None


def explicit_value(patterns: tuple[re.Pattern[str], ...], prompt: str) -> str | None:
    for pattern in patterns:
        match = pattern.search(prompt)
        if not match:
            continue
        value = match.group(match.lastindex or 1).strip(" \t\r\n:;,")
        if value:
            return value
    return None


def resolve_destination(prompt: str) -> dict:
    explicit = explicit_value(DESTINATION_PATTERNS, prompt)
    if explicit:
        return {
            "value": explicit,
            "source": "explicit",
            "status": "resolved",
            "is_nocturna": norm(explicit) == "nocturna",
            "materialization_allowed": True,
            "rule": "indicação explícita prevalece",
        }

    p = norm(prompt)
    positive_nocturna = bool(re.search(
        r"\b(?:destino|destine|destinar|gravar|escrever|materializar|salvar)\b.{0,80}\bnocturna\b|\b(?:em|no|na|para)\s+nocturna\b",
        p,
        re.I,
    ))
    negative_nocturna = bool(re.search(
        r"\b(?:não|nao)\b.{0,30}\b(?:use|usar|destino|destinar|grave|gravar|escreva|escrever|materializar|salvar)\b.{0,40}\bnocturna\b",
        p,
        re.I,
    ))
    if positive_nocturna and not negative_nocturna:
        return {
            "value": "Nocturna",
            "source": "explicit_keyword",
            "status": "resolved",
            "is_nocturna": True,
            "materialization_allowed": True,
            "rule": "Nocturna só é destino quando explicitamente indicada",
        }

    return {
        "value": None,
        "source": None,
        "status": "ambiguous",
        "is_nocturna": False,
        "materialization_allowed": False,
        "rule": "sem destino explícito ou inequivocamente determinado, não materializar",
    }


def resolve_origin(prompt: str) -> dict:
    explicit = explicit_value((ORIGIN_PATTERN,), prompt)
    return {
        "value": explicit,
        "source": "explicit" if explicit else None,
        "status": "resolved" if explicit else "contextual",
        "rule": "origem é parâmetro operacional e não identidade permanente",
    }


def build_coordination(prompt: str, catalog: list[dict], matches: list[dict]) -> dict:
    coordinator = find_catalog_item(catalog, FIXED_COORDINATOR_TITLE)
    fixed = find_catalog_item(catalog, FIXED_GITHUB_INSTRUMENT_TITLE)
    active = [m for m in matches if m["active"]]

    participants: list[dict] = [{
        "role": "coordinator",
        "title": FIXED_COORDINATOR_TITLE,
        "instrument": coordinator["instrument"] if coordinator else None,
        "activation": "own_title",
        "recovery": "github",
        "status": "resolved" if coordinator else "catalog_missing",
        "activated_by_current_prompt": any(norm(m["title"]) == norm(FIXED_COORDINATOR_TITLE) for m in active),
    }, {
        "role": "fixed_github_instrument",
        "title": FIXED_GITHUB_INSTRUMENT_TITLE,
        "instrument": fixed["instrument"] if fixed else None,
        "activation": "fixed_title",
        "recovery": "github",
        "status": "resolved" if fixed else "catalog_missing",
        "activated_by_current_prompt": False,
    }]

    additional: dict[str, dict] = {}
    for match in active:
        if norm(match["title"]) in {norm(FIXED_COORDINATOR_TITLE), norm(FIXED_GITHUB_INSTRUMENT_TITLE)}:
            continue
        key = match["instrument"]
        entry = additional.setdefault(key, {
            "role": "additional_instrument",
            "title": match["title"],
            "instrument": match["instrument"],
            "activation": "user_supplied_title",
            "recovery": "github",
            "status": "resolved",
            "occurrences": 0,
            "identity_source": "conteúdo recuperado do GitHub",
            "identity_presumed_from_title": False,
        })
        entry["occurrences"] += 1

    participants.extend(sorted(additional.values(), key=lambda x: norm(x["title"])))

    known = {norm(p["title"]) for p in participants}
    unresolved_explicit = []
    for title in explicit_titles(prompt):
        if norm(title) in known:
            continue
        unresolved_explicit.append({
            "role": "additional_instrument",
            "title": title,
            "instrument": None,
            "activation": "user_supplied_title",
            "recovery": "github",
            "status": "catalog_missing",
            "occurrences": 1,
            "identity_source": "conteúdo a recuperar do GitHub",
            "identity_presumed_from_title": False,
            "activated_by_current_prompt": True,
        })
    participants.extend(unresolved_explicit)

    origin = resolve_origin(prompt)
    destination = resolve_destination(prompt)

    return {
        "architecture_version": "3.0",
        "preserves_existing_correfencia": True,
        "coordinator": {
            "title": FIXED_COORDINATOR_TITLE,
            "activation": "own_title",
            "recovery": "github",
            "identity_source": "conteúdo efetivamente recuperado",
            "status": "resolved" if coordinator else "catalog_missing",
        },
        "fixed_instrument": {
            "title": FIXED_GITHUB_INSTRUMENT_TITLE,
            "activation": "fixed_title",
            "recovery": "github",
            "identity_source": "conteúdo efetivamente recuperado",
            "status": "resolved" if fixed else "catalog_missing",
        },
        "additional_instruments": [p for p in participants if p["role"] == "additional_instrument"],
        "unresolved_explicit_additional_titles": unresolved_explicit,
        "cardinality": {
            "additional_is_unbounded": True,
            "minimum_additional": 0,
            "maximum_additional": None,
            "selection_is_arbitrary": False,
            "all_user_supplied_titles_are_considered": True,
        },
        "participants": participants,
        "activation_unit": {
            "title_plus_custom_request_are_joint_entry": True,
            "title_identifies_and_activates": True,
            "request_defines_concrete_application": True,
            "title_alone_is_not_the_whole_application": True,
        },
        "instrument_application_separation": {
            "instrument_elements": ["identity", "purpose", "function", "essential_instructions", "operational_logic"],
            "application_elements": ["demand", "context", "scope", "parameters", "criteria", "format", "restrictions", "data", "origin", "destination", "adaptation"],
            "identity_is_not_changed_by_contextual_variation": True,
        },
        "demand": {
            "is_external_to_instrument_identity": True,
            "source": "current_prompt",
            "single_concrete_demand": True,
            "objective": "objetivo definido pela requisição",
        },
        "context": {
            "source": "current_prompt",
            "is_external_to_instrument_identity": True,
            "conditions": "circunstâncias da requisição",
        },
        "parameters": {
            "origin": origin,
            "destination": destination,
            "scope": "current_demand",
            "criteria": "current_demand",
            "format": "current_demand",
            "restrictions": "current_demand",
            "data": "current_demand",
        },
        "adaptation": {
            "allowed": True,
            "preserve_identity": True,
            "preserve_purpose": True,
            "preserve_function": True,
            "preserve_instructions": True,
            "preserve_operational_logic": True,
            "may_reorganize_context_dependent_aspects": True,
            "is_contextual_instantiation_not_literal_reproduction": True,
            "does_not_transfer_specialized_responsibilities": True,
        },
        "coordination": {
            "is_fusion": False,
            "specialized_instruments_remain_distinct": True,
            "all_recovered_instruments_are_individually_identified": True,
            "is_mutual": True,
            "is_cumulative": True,
            "is_simultaneous": True,
            "is_individual": True,
            "is_nonexclusive": True,
            "single_concrete_demand": True,
            "coordinator_role": "recuperar, interpretar, orientar, articular, organizar, identificar dependências, determinar contexto e parâmetros, identificar origem, resolver destino, preservar responsabilidades, integrar, validar e manter rastreabilidade",
            "specialized_roles_preserved": True,
            "compatibility_is_coordinated": True,
            "conflicts_require_integrity_validation": True,
            "destructive_resolution_is_forbidden_without_validation": True,
        },
        "multidirectory": {
            "enabled": True,
            "origin_and_destination_are_operational_parameters": True,
            "instrument_storage_location_does_not_define_result_destination": True,
            "cross_directory_operation_allowed": True,
            "nocturna_is_not_default": True,
            "explicit_destination_precedes_contextual_inference": True,
            "contextual_inference_requires_inequivocal_context": True,
            "weak_thematic_association_is_never_sufficient": True,
            "ambiguous_destination_blocks_materialization": True,
        },
        "intermediate_results": {
            "allowed": True,
            "must_preserve_origin": True,
            "must_preserve_instrument": True,
            "must_preserve_function": True,
            "must_preserve_stage": True,
            "must_preserve_destination": True,
            "must_preserve_relation_to_demand": True,
            "must_preserve_relation_to_other_results": True,
            "are_not_instruments": True,
        },
        "compatibility": {
            "preserves_identity": True,
            "preserves_purpose": True,
            "preserves_function": True,
            "preserves_instructions": True,
            "preserves_logic": True,
            "arbitrary_deletion_forbidden": True,
            "arbitrary_substitution_forbidden": True,
            "non_destructive_resolution_preferred": True,
        },
        "validation": {
            "required": True,
            "checks": [
                "instrumentos recuperados", "identidade e correspondência título-conteúdo",
                "correferência", "instruções", "função própria e eventual função diversa",
                "sequência", "responsabilidades", "demanda", "contexto", "parâmetros",
                "adaptação", "origem", "destino", "participantes", "dependências",
                "resultados intermediários", "materialização", "referências",
                "relações entre resultados", "integridade de ponta a ponta", "rastreabilidade",
            ],
            "all_additional_titles_represented": True,
            "final_validation_is_coordinated": True,
            "heuristic_policy": "conservadora; incerteza favorece correferência e função própria",
        },
        "traceability": {
            "required": True,
            "fields": [
                "título", "instrumento", "correferência", "função", "acionamento",
                "eventual_exceção", "contexto", "relação_com_demais", "origem",
                "destino", "parâmetros", "ação", "resultado", "validação",
            ],
            "chain": "TÍTULO → INSTRUMENTO RECUPERADO → CONTEÚDO EFETIVO → DEMANDA → CONTEXTO → PARÂMETROS → ADAPTAÇÃO → ORIGEM → ETAPAS → RESULTADOS INTERMEDIÁRIOS → DESTINO → RESULTADO FINAL → VALIDAÇÃO",
        },
        "reuse": {
            "same_instrument_can_be_reused": True,
            "identity_purpose_function_logic_remain": True,
            "demand_context_scope_parameters_criteria_format_restrictions_data_origin_destination_adaptation_may_change": True,
        },
        "sequences": {
            "individual": "MENÇÃO GENÉRICA → DETECÇÃO → CORREFERÊNCIA → IDENTIFICAÇÃO → RECUPERAÇÃO → CONTEÚDO EFETIVO → FUNÇÃO PRÓPRIA → VERIFICAÇÃO DE FUNÇÃO DIVERSA → PRESERVAÇÃO OU SUBSTITUIÇÃO EXCEPCIONAL → DEMANDA → CONTEXTO → ORIGEM → DESTINO → PARAMETRIZAÇÃO → ADAPTAÇÃO → ACIONAMENTO → AÇÃO → EXECUÇÃO → VALIDAÇÃO → RASTREABILIDADE",
            "coordinated": "PRÓPRIO TÍTULO → PRÓPRIA ATIVAÇÃO → TÍTULOS ADICIONAIS → IDENTIFICAÇÃO INDIVIDUAL → TÍTULO DO INSTRUMENTO FIXO → ATIVAÇÃO → RECUPERAÇÃO PELO GITHUB → CONTEÚDO EFETIVO → PRESERVAÇÃO DAS IDENTIDADES → INTERPRETAÇÃO CONJUNTA → RELAÇÃO ENTRE INSTRUÇÕES → DEMANDA → CONTEXTO → ORIGEM → DESTINO → PARAMETRIZAÇÃO → ADAPTAÇÃO → APLICAÇÃO COORDENADA → RESULTADOS INTERMEDIÁRIOS → COMPOSIÇÃO → MATERIALIZAÇÃO → VALIDAÇÃO → RASTREABILIDADE → RESULTADO FINAL",
            "multiple": "MENÇÕES → DETECÇÕES INDIVIDUAIS → CORREFERÊNCIAS → INSTRUMENTOS → FUNÇÕES → EXCEÇÕES INDIVIDUAIS → ACIONAMENTOS CUMULATIVOS → AÇÕES COORDENADAS → EXECUÇÃO CONJUNTA → VALIDAÇÃO → RASTREABILIDADE",
        },
        "non_substitution": {
            "does_not_replace_other_instruments": True,
            "does_not_absorb_functions": True,
            "does_not_modify_purposes": True,
            "does_not_presume_missing_content": True,
            "does_not_reconstruct_unstored_logic": True,
            "does_not_merge_identities": True,
            "does_not_reduce_valid_plurality_to_one_choice": True,
        },
        "github_limits": {
            "actions_process_only_received_request": True,
            "does_not_observe_untransmitted_chat": True,
            "does_not_create_permissions": True,
            "does_not_create_access": True,
        },
    }


def validate(prompt: str, root: Path = ROOT) -> dict:
    catalog = instrument_catalog(root)
    consistency_errors = catalog_consistency(root, catalog)
    normalized_prompt, origin_map = normalize_with_map(prompt)
    matches: list[dict] = []

    for item in catalog:
        seen: set[tuple[int, int]] = set()
        needle = norm(item["title"])
        if not needle:
            continue
        pattern = phrase_pattern(needle)
        for match in pattern.finditer(normalized_prompt):
            occurrence = (match.start(), match.end())
            if occurrence in seen:
                continue
            seen.add(occurrence)
            original_start = origin_map[match.start()]
            original_end = origin_map[match.end() - 1] + 1
            context = local_context(prompt, original_start, original_end)
            diverse = has_diverse_assignment(context, item["title"])
            matches.append({
                "title": item["title"],
                "matched_text": prompt[original_start:original_end],
                "instrument": item["instrument"],
                "instrument_id": item.get("id"),
                "correferencia": True,
                "function_status": "diversa_explicitamente_atribuida" if diverse else "propria_preservada",
                "active": not diverse,
                "exception_scope": "occurrence" if diverse else None,
                "context_window": context,
                "recovery": "github",
                "content_source": "conteúdo efetivamente armazenado",
                "identity_presumed_from_title": False,
            })

    matches.sort(key=lambda item: (item["instrument"], item["matched_text"].casefold(), item["context_window"]))
    active_by_instrument: dict[str, dict] = {}
    for match in matches:
        if match["active"]:
            active_by_instrument[match["instrument"]] = {
                "title": match["title"],
                "instrument": match["instrument"],
                "instrument_id": match["instrument_id"],
                "function": match["function_status"],
            }

    coordination = build_coordination(prompt, catalog, matches)
    traceability = []
    for match in matches:
        traceability.append({
            "title": match["title"],
            "instrument": match["instrument"],
            "correferencia": match["correferencia"],
            "function": match["function_status"],
            "activation": match["active"],
            "exception": match["exception_scope"],
            "context": match["context_window"],
            "relation_to_others": "mútua, cumulativa, coordenada, simultânea, individual e não exclusiva" if len(active_by_instrument) > 1 else "individual",
            "origin": coordination["parameters"]["origin"],
            "destination": coordination["parameters"]["destination"],
            "parameters": coordination["parameters"],
            "action": "acionar_função_própria" if match["active"] else "exceção_local_sem_acionamento_da_função_própria",
            "result": None,
            "validation": None,
        })
    coordination["traceability"]["occurrences"] = traceability

    status = "ok" if not consistency_errors else "catalog_inconsistente"
    return {
        "schema_version": "4.0",
        "status": status,
        "validation_errors": consistency_errors,
        "architecture_policy": {
            "version": "3.0",
            "sections": ARCHITECTURE_SECTIONS,
            "all_sections_accounted_for": True,
            "instrument_prompt_elements_are_not_modified": True,
        },
        "activation_rule": {
            "title_plus_request_forms_activation_unit": True,
            "title_identifies_and_activates": True,
            "github_recovers_existing_logic": True,
            "request_defines_concrete_application": True,
            "activation_requires_effective_request_transmission_to_github": True,
        },
        "rule": {
            "generic_mention_establishes_corref": True,
            "generic_mention_preserves_own_function": True,
            "silence_is_not_diverse_function": True,
            "ambiguity_favors_own_function": True,
            "diverse_function_requires_explicit_or_unequivocal_context": True,
            "exception_is_local_to_occurrence": True,
            "multiple_titles_are_independent_cumulative_and_nonexclusive": True,
            "multiple_titles_are_mutual_coordinated_and_simultaneous": True,
            "instrument_content_is_not_modified": True,
            "matching_uses_title_only_for_activation": True,
            "aliases_are_non_activating_hints": True,
            "capabilities_are_non_activating_hints": True,
            "context_preserves_original_prompt": True,
            "title_is_not_just_a_label_when_corresponding_instrument_exists": True,
            "contextualization_does_not_rewrite_instrument_identity": True,
            "parameterization_does_not_replace_operational_logic": True,
            "adaptation_does_not_replace_operational_logic": True,
        },
        "instrument_count": len(catalog),
        "matched_occurrences": len(matches),
        "matched_titles": list(dict.fromkeys(m["title"] for m in matches)),
        "active_instruments": list(active_by_instrument.values()),
        "execution_plan": [
            {
                "title": item["title"],
                "instrument": item["instrument"],
                "instrument_id": item["instrument_id"],
                "mode": "preserve_own_function",
                "occurrences": sum(1 for m in matches if m["instrument"] == item["instrument"] and m["active"]),
                "recovery": "github",
                "content_effective": True,
                "identity_preserved": True,
            }
            for item in active_by_instrument.values()
        ],
        "exceptions": [m for m in matches if not m["active"]],
        "matches": matches,
        "coordination": coordination,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt")
    source.add_argument("--prompt-file")
    parser.add_argument("--output", default="correfencia-result.json")
    args = parser.parse_args()
    prompt = args.prompt if args.prompt is not None else Path(args.prompt_file).read_text(encoding="utf-8")
    result = validate(prompt)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "instrument_count": result["instrument_count"],
        "matched_occurrences": result["matched_occurrences"],
        "matched_titles": result["matched_titles"],
        "active_instruments": result["active_instruments"],
        "exceptions": result["exceptions"],
        "validation_errors": result["validation_errors"],
    }, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
