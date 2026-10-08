#!/usr/bin/env python3
"""Validação técnica da correferência funcional da Promptária."""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path("Promptária")
CONTEXT_RADIUS = 480
DIVERSE_PATTERNS = (
    r"\b(?:usar|use|utilizar|utilize|empregar|empregue|tratar|trate|considerar|considere|fazer|faça|faca)\b.{0,140}\b{TITLE}\b.{0,180}\b(?:como|para|na função de|no papel de|com a finalidade de|com o objetivo de)\b",
    r"\b{TITLE}\b.{0,180}\b(?:como|para|na função de|no papel de|com a finalidade de|com o objetivo de)\b.{0,180}\b(?:em vez de|ao invés de|ao inves de|diferente de|outra finalidade|outra função|outro papel|função diversa|funcao diversa)\b",
    r"\b{TITLE}\b.{0,160}\b(?:não deve|nao deve|não deverá|nao devera|deve ser usado para|deve ser usada para|deve ser utilizado para|deve ser utilizada para|deve atuar como|deve desempenhar|deverá atuar como|devera atuar como|deverá desempenhar|devera desempenhar)\b",
    r"\b{TITLE}\b.{0,160}\b(?:exclusivamente para|somente para|apenas para)\b.{0,140}\b(?:outra|diversa|diferente|substituir|substituta)\b",
    r"\b(?:não acione|nao acione|não acionar|nao acionar|não use a função própria|nao use a funcao propria|não aplicar a função original|nao aplicar a funcao original)\b.{0,180}\b{TITLE}\b",
)


def normalize_with_map(value: str) -> tuple[str, list[int]]:
    """Normaliza texto e conserva a origem de cada caractere normalizado."""
    chars: list[str] = []
    origins: list[int] = []
    for index, original in enumerate(value):
        chunk = unicodedata.normalize("NFKC", original).casefold()
        chunk = "".join(
            c for c in unicodedata.normalize("NFD", chunk)
            if unicodedata.category(c) != "Mn"
        )
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
    normalized = "".join(out)
    left = len(normalized) - len(normalized.lstrip())
    right = len(normalized.rstrip())
    return normalized.strip(), out_origins[left:right]


def norm(value: str) -> str:
    return normalize_with_map(value)[0]


def html_title(raw: str) -> str | None:
    match = re.search(r"<title>\s*(.*?)\s*</title>", raw, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip() if match else None


def instrument_catalog(root: Path = ROOT) -> list[dict]:
    """Lê metadados físicos; nenhum instrumento é alterado."""
    items = []
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
        aliases = [title]
        fallback = directory.name.replace("-", " ")
        if norm(fallback) != norm(title):
            aliases.append(fallback)
        items.append({"title": title, "aliases": aliases, "instrument": str(index)})
    return items


def catalog_consistency(root: Path, catalog: list[dict]) -> list[str]:
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {item["path"]: item["title"] for item in manifest.get("instruments", [])}
    actual = {item["instrument"]: item["title"] for item in catalog}
    errors = []
    if set(expected) != set(actual):
        errors.append("manifest.json e árvore física possuem caminhos diferentes")
    for path, title in expected.items():
        if path in actual and norm(title) != norm(actual[path]):
            errors.append(f"título divergente em {path!r}")
    return errors


def local_context(text: str, start: int, end: int) -> str:
    """Mantém a análise da exceção local à ocorrência."""
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
    c, t = norm(context), re.escape(norm(title))
    if not c:
        return False
    for pattern in DIVERSE_PATTERNS:
        if re.search(pattern.replace("{TITLE}", t), c, re.I):
            return True
    return bool(re.search(
        rf"\b{t}\b\s+(?:não|nao)\s+(?:deve|deverá|devera|será|sera|é|e)\b",
        c, re.I,
    ))


def phrase_pattern(needle: str) -> re.Pattern[str]:
    """Casa a frase inteira, não uma substring de outra palavra."""
    return re.compile(rf"(?<!\w){re.escape(needle)}(?!\w)", re.UNICODE)


FIXED_COORDINATOR_TITLE = "Acionamento Coordenado de Instrumentos Promptuais"
FIXED_GITHUB_INSTRUMENT_TITLE = "Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas"
DESTINATION_PATTERNS = (
    re.compile(r"\b(?:destino|destin[oó]|gravar|escrever|materializar|salvar)\s*[:=]\s*([^\n.;]+)", re.I),
    re.compile(r"\b(?:no|na|em|para o|para a)\s+(diret[oó]rio|pasta|arquivo)\s+([^\n.;]+)", re.I),
)
ORIGIN_PATTERN = re.compile(r"\b(?:origem|origin[aá]rio|proveni[eê]ncia)\s*[:=]\s*([^\n.;]+)", re.I)
EXPLICIT_TITLE_PATTERNS = (
    re.compile(r"\bt[ií]tulo(?:\s+do\s+instrumento(?:\s+promptual)?)?\s*[:=]\s*[“\"]([^”\"]+)[”\"]", re.I),
    re.compile(r"\binstrumento(?:\s+promptual)?\s+denominado\s*[“\"]([^”\"]+)[”\"]", re.I),
    re.compile(r"\binstrumento(?:\s+promptual)?\s+chamado\s*[“\"]([^”\"]+)[”\"]", re.I),
)

def explicit_titles(prompt: str) -> list[str]:
    titles = []
    seen = set()
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
        if any(norm(alias) == target for alias in item["aliases"]):
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
    """Resolve destino conservadoramente; não autoriza escrita por associação temática."""
    explicit = explicit_value(DESTINATION_PATTERNS, prompt)
    normalized_prompt = norm(prompt)
    nocturna = bool(re.search(r"\b(?:destino|destine|destinar|gravar|escrever|materializar|salvar)\b.{0,80}\bnocturna\b|\b(?:em|no|na|para)\s+nocturna\b", normalized_prompt, re.I)) and not bool(re.search(r"\b(?:nao|não)\b.{0,30}\b(?:use|usar|destino|destinar|grave|gravar|escreva|escrever|materializar|salvar)\b.{0,40}\bnocturna\b", normalized_prompt, re.I))
    if explicit:
        value = explicit
        if "nocturna" in norm(value):
            return {
                "value": value,
                "source": "explicit",
                "status": "resolved",
                "is_nocturna": True,
                "materialization_allowed": True,
                "rule": "indicação explícita prevalece",
            }
        return {
            "value": value,
            "source": "explicit",
            "status": "resolved",
            "is_nocturna": False,
            "materialization_allowed": True,
            "rule": "indicação explícita prevalece",
        }
    if nocturna:
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
    additional_by_path = {}
    for match in active:
        if norm(match["title"]) in {norm(FIXED_COORDINATOR_TITLE), norm(FIXED_GITHUB_INSTRUMENT_TITLE)}:
            continue
        additional_by_path.setdefault(match["instrument"], {
            "title": match["title"],
            "instrument": match["instrument"],
            "occurrences": 0,
            "identity_source": "conteúdo recuperado do GitHub",
            "identity_presumed_from_title": False,
        })
        additional_by_path[match["instrument"]]["occurrences"] += 1

    participants = []
    if coordinator:
        participants.append({
            "role": "coordinator",
            "title": coordinator["title"],
            "instrument": coordinator["instrument"],
            "activation": "own_title",
            "recovery": "github",
            "status": "resolved",
        })
    else:
        participants.append({
            "role": "coordinator",
            "title": FIXED_COORDINATOR_TITLE,
            "instrument": None,
            "activation": "own_title",
            "recovery": "github",
            "status": "catalog_missing",
        })

    if fixed:
        participants.append({
            "role": "fixed_github_instrument",
            "title": fixed["title"],
            "instrument": fixed["instrument"],
            "activation": "fixed_title",
            "recovery": "github",
            "status": "resolved",
        })
    else:
        participants.append({
            "role": "fixed_github_instrument",
            "title": FIXED_GITHUB_INSTRUMENT_TITLE,
            "instrument": None,
            "activation": "fixed_title",
            "recovery": "github",
            "status": "catalog_missing",
        })

    participants.extend({
        "role": "additional_instrument",
        "title": item["title"],
        "instrument": item["instrument"],
        "activation": "user_supplied_title",
        "recovery": "github",
        "status": "resolved",
        "occurrences": item["occurrences"],
        "identity_source": item["identity_source"],
        "identity_presumed_from_title": item["identity_presumed_from_title"],
    } for item in sorted(additional_by_path.values(), key=lambda x: norm(x["title"])))

    origin = resolve_origin(prompt)
    destination = resolve_destination(prompt)
    known_titles = {norm(p["title"]) for p in participants}
    unresolved_explicit_titles = []
    for title in explicit_titles(prompt):
        if norm(title) in known_titles:
            continue
        unresolved_explicit_titles.append({
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
    participants.extend(unresolved_explicit_titles)
    unresolved = [p["title"] for p in participants if p["status"] != "resolved"]
    activated_titles = {norm(m["title"]) for m in active}
    for participant in participants:
        participant["activated_by_current_prompt"] = norm(participant["title"]) in activated_titles
    return {
        "architecture_version": "1.1",
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
        "unresolved_explicit_additional_titles": unresolved_explicit_titles,
        "cardinality": {
            "additional_is_unbounded": True,
            "minimum_additional": 0,
            "maximum_additional": None,
            "selection_is_arbitrary": False,
            "all_user_supplied_titles_are_considered": True,
        },
        "participants": participants,
        "activation_unit": {
            "title_and_request_are_joint_entry": True,
            "title_is_point_of_entry": True,
            "custom_request_supplies_demand": True,
            "title_alone_is_not_the_whole_application": True,
        },
        "instrument_application_separation": {
            "instrument_elements": ["identity", "purpose", "function", "essential_instructions", "operational_logic"],
            "application_elements": ["demand", "context", "scope", "parameters", "criteria", "format", "restrictions", "origin", "destination", "adaptation"],
            "identity_is_not_changed_by_contextual_variation": True,
        },
        "demand": {
            "is_external_to_instrument_identity": True,
            "source": "current_prompt",
            "single_concrete_demand": True,
        },
        "context": {
            "source": "current_prompt",
            "is_external_to_instrument_identity": True,
        },
        "parameters": {
            "origin": origin,
            "destination": destination,
            "scope": "current_demand",
            "criteria": "current_demand",
            "format": "current_demand",
            "restrictions": "current_demand",
        },
        "adaptation": {
            "allowed": True,
            "preserve_identity": True,
            "preserve_purpose": True,
            "preserve_instructions": True,
            "preserve_operational_logic": True,
            "may_reorganize_context_dependent_aspects": True,
            "does_not_transfer_specialized_responsibilities": True,
        },
        "coordination": {
            "is_fusion": False,
            "instrument_coordinator_is_reusable": True,
            "specialized_instruments_remain_distinct": True,
            "all_recovered_instruments_are_individually_identified": True,
            "is_cumulative": True,
            "is_simultaneous": True,
            "is_nonexclusive": True,
            "single_concrete_demand": True,
            "coordinator_role": "orientação, coordenação e articulação",
            "specialized_roles_preserved": True,
            "compatibility_is_coordinated": True,
            "conflicts_require_integrity_validation": True,
            "destructive_resolution_is_forbidden_without_validation": True,
        },
        "sequence": [
            "próprio título",
            "própria ativação",
            "títulos dos instrumentos promptuais adicionais fornecidos pelo usuário",
            "ativação dos instrumentos promptuais adicionais",
            "título do instrumento fixo",
            "ativação do instrumento fixo",
            "recuperação individual dos instrumentos pelo GitHub",
            "preservação das identidades",
            "interpretação conjunta",
            "relação entre as instruções",
            "contextualização",
            "parametrização",
            "adaptação",
            "aplicação conjunta",
            "execução",
            "validação",
            "resultado",
        ],
        "multidirectory": {
            "enabled": True,
            "origin_and_destination_are_operational_parameters": True,
            "instrument_storage_location_does_not_define_result_destination": True,
            "cross_directory_operation_allowed": True,
            "nocturna_is_not_default": True,
            "explicit_destination_precedes_contextual_inference": True,
            "ambiguous_destination_blocks_materialization": True,
        },
        "intermediate_results": {
            "allowed": True,
            "must_preserve_origin": True,
            "must_preserve_responsible_instrument": True,
            "must_preserve_stage": True,
            "must_preserve_destination": True,
            "must_preserve_relation_to_final_result": True,
        },
        "traceability": {
            "required": True,
            "fields": [
                "title",
                "instrument",
                "role",
                "activation",
                "recovery",
                "origin",
                "destination",
                "stage",
                "responsible_instrument",
                "result_relation",
                "validation",
            ],
        },
        "destination_resolution": {
            "priority": [
                "indicação explícita",
                "contexto inequivocamente determinante",
                "função original quando realmente aplicável",
                "inferência contextual segura",
            ],
            "weak_thematic_association_is_never_sufficient": True,
            "ambiguous_destination_blocks_materialization": True,
            "explicit_other_destination_precedes_nocturna": True,
        },
        "writing_coordination": {
            "multiple_producers_require_role_assignment": True,
            "avoid_unnecessary_duplication": True,
            "conflicts_preserve_original_rules": True,
            "destructive_resolution_requires_integrity_validation": True,
            "destination_does_not_transfer_specialized_responsibility": True,
        },
        "recovery_policy": {
            "github_is_source_of_truth_for_instrument_content": True,
            "title_is_identifier_and_activation_key": True,
            "title_alone_does_not_define_additional_identity": True,
            "content_must_be_recovered_before_application": True,
            "instrument_content_is_not_invented_or_rewritten": True,
        },
        "output_policy": {
            "full_instrument_reproduction_not_required": True,
            "recovered_content_is_operational_basis": True,
            "final_result_preserves_participant_distinctions": True,
        },
        "status": "ready" if not unresolved else "partial_catalog_resolution",
        "activation": {
            "coordinator_title_present": norm(FIXED_COORDINATOR_TITLE) in activated_titles,
            "fixed_title_present": norm(FIXED_GITHUB_INSTRUMENT_TITLE) in activated_titles,
            "additional_titles_present": [p["title"] for p in participants if p["role"] == "additional_instrument"],
        },
        "validation": {
            "final_validation_is_coordinated": True,
            "checks": [
                "instrumentos recuperados",
                "identidades corretas",
                "sequência",
                "responsabilidades",
                "origem",
                "destino",
                "resultados intermediários",
                "materialização final",
                "referências",
                "relações",
                "integridade de ponta a ponta",
            ],
            "resolved_participants": len([p for p in participants if p["status"] == "resolved"]),
            "unresolved_participants": unresolved,
            "all_additional_titles_represented": True,
            "identities_preserved": True,
            "sequence_preserved": True,
            "responsibilities_preserved": True,
            "origin_destination_tracked": True,
            "end_to_end_integrity_required": True,
        },
    }


def validate(prompt: str, root: Path = ROOT) -> dict:
    catalog = instrument_catalog(root)
    consistency_errors = catalog_consistency(root, catalog)
    normalized_prompt, origin_map = normalize_with_map(prompt)
    matches = []

    for item in catalog:
        seen: set[tuple[int, int]] = set()
        for alias in item["aliases"]:
            needle = norm(alias)
            if not needle:
                continue
            for match in phrase_pattern(needle).finditer(normalized_prompt):
                occurrence = (match.start(), match.end())
                if occurrence in seen:
                    continue
                seen.add(occurrence)
                original_start = origin_map[match.start()]
                original_end = origin_map[match.end() - 1] + 1
                context = local_context(prompt, original_start, original_end)
                diverse = has_diverse_assignment(context, alias)
                matches.append({
                    "title": item["title"],
                    "matched_text": prompt[original_start:original_end],
                    "instrument": item["instrument"],
                    "correferencia": True,
                    "function_status": "diversa_explicitamente_atribuida" if diverse else "propria_preservada",
                    "active": not diverse,
                    "exception_scope": "occurrence" if diverse else None,
                    "context_window": context,
                })

    matches.sort(key=lambda item: (item["instrument"], item["matched_text"].casefold()))
    index = {}
    for match in matches:
        index.setdefault(match["title"], []).append(match)

    active_by_instrument = {}
    for match in matches:
        if match["active"]:
            active_by_instrument[match["instrument"]] = {
                "title": match["title"],
                "instrument": match["instrument"],
            }

    coordination = build_coordination(prompt, catalog, matches)
    status = "ok" if not consistency_errors else "catalog_inconsistente"
    return {
        "schema_version": "3.0",
        "status": status,
        "validation_errors": consistency_errors,
        "activation_rule": {
            "title_plus_custom_request_forms_activation_unit": True,
            "title_identifies_and_activates": True,
            "github_recovers_existing_logic": True,
            "request_defines_concrete_application": True,
        },
        "rule": {
            "generic_mention_establishes_corref": True,
            "generic_mention_preserves_own_function": True,
            "silence_is_not_diverse_function": True,
            "ambiguity_favors_own_function": True,
            "diverse_function_requires_explicit_or_unequivocal_context": True,
            "exception_is_local_to_occurrence": True,
            "multiple_titles_are_independent_cumulative_and_nonexclusive": True,
            "instrument_content_is_not_modified": True,
            "matching_uses_phrase_boundaries": True,
            "context_preserves_original_prompt": True,
            "title_is_not_just_a_label": True,
            "contextualization_does_not_rewrite_instrument_identity": True,
            "parameterization_does_not_replace_operational_logic": True,
            "adaptation_does_not_replace_operational_logic": True,
        },
        "instrument_count": len(catalog),
        "matched_occurrences": len(matches),
        "matched_titles": list(index),
        "active_instruments": list(active_by_instrument.values()),
        "execution_plan": [
            {
                "title": item["title"],
                "instrument": item["instrument"],
                "mode": "preserve_own_function",
                "occurrences": len(index.get(item["title"], [])),
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
