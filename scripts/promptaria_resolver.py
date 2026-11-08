#!/usr/bin/env python3
"""Resolve Promptária instrument titles without inventing missing content."""
from __future__ import annotations
import argparse, json, re, unicodedata
from datetime import datetime, timezone
from pathlib import Path

def normalize(value: str) -> str:
    # Match the JavaScript resolver: accents are folded and hyphens behave as
    # word separators, so equivalent canonical titles normalize consistently.
    value = unicodedata.normalize('NFKD', value)
    value = ''.join(char for char in value if not unicodedata.combining(char)).casefold()
    value = re.sub(r'[\u200b-\u200f\ufeff]', '', value)
    value = re.sub(r'[^\w\s-]', ' ', value, flags=re.UNICODE)
    return re.sub(r'[\s-]+', ' ', value).strip()

def validate_destination(value: object) -> str:
    """Validate a proposed repository-relative destination without writing to it."""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise SystemExit("Destino inválido: informe um caminho relativo como texto.")
    destination = value.strip()
    if not destination:
        return ""
    # Treat both POSIX and Windows separators as separators; reject ambiguous paths.
    if "\\" in destination or destination.startswith("/") or re.match(r"^[A-Za-z]:", destination):
        raise SystemExit("Destino recusado: use caminho relativo POSIX dentro do repositório.")
    if any(ord(char) < 32 or ord(char) == 127 for char in destination):
        raise SystemExit("Destino recusado: caracteres de controle não são permitidos.")
    parts = destination.split("/")
    if any(part in ("", ".", "..") for part in parts) or any(part.casefold() == ".git" for part in parts):
        raise SystemExit("Destino recusado: segmentos vazios, . , .. e .git não são permitidos.")
    return destination

def read_instruments(root: Path) -> list[dict]:
    """Only explicitly enabled registry entries can be resolved functionally."""
    items = []
    if not root.exists():
        return items
    registry_path = root.parent / "config" / "instrument-registry.json"
    enabled_paths = None
    registry_by_path = {}
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry_entries = registry.get("instruments", [])
        registry_by_path = {
            item.get("path"): item for item in registry_entries
            if isinstance(item, dict) and isinstance(item.get("path"), str)
        }
        enabled_paths = {
            item.get("path") for item in registry_entries
            if isinstance(item, dict) and isinstance(item.get("activation"), dict)
            and item["activation"].get("enabled") is True
        }
    for path in sorted(root.rglob("*.md")):
        repo_path = path.relative_to(root.parent).as_posix()
        entry = registry_by_path.get(repo_path, {})
        active = enabled_paths is None or repo_path in enabled_paths
        text = path.read_text(encoding="utf-8")
        match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
        if match:
            title = match.group(1).strip()
            items.append({
                "id": entry.get("id"),
                "title": title,
                "path": path.as_posix(),
                "repository_path": repo_path,
                "aliases": entry.get("aliases", []) if isinstance(entry.get("aliases", []), list) else [],
                "content": text,
                "normalized_title": normalize(title),
                "normalized_aliases": [normalize(alias) for alias in entry.get("aliases", []) if isinstance(alias, str) and normalize(alias)],
                "active": active,
            })
    return items

def resolve(request: str, instruments: list[dict]) -> list[dict]:
    """Resolve explicit IDs/paths first, then unique enabled titles and aliases.

    Ambiguous terms never activate any candidate. Disabled registry entries may
    be reported for explicit references, but are never functionally activated.
    Occurrence offsets refer to normalized searchable text.
    """
    normalized_request = normalize(request)
    matches = []
    all_by_id = {item.get("id"): item for item in instruments if item.get("id")}
    all_by_repo_path = {item.get("repository_path"): item for item in instruments if item.get("repository_path")}
    active_catalog = [item for item in instruments if item.get("active", True) and item.get("normalized_title")]

    def make_match(item, identity, start, end, *, ambiguous=False, diverse=False, disabled=False):
        if disabled:
            function_status = "disabled"
            activation_status = "explicit_reference_to_disabled_instrument"
            exception_status = "disabled_registry_entry"
            activation = False
        elif ambiguous:
            function_status = "ambiguous"
            activation_status = "recognized_ambiguous_not_activated"
            exception_status = "catalog_identity"
            activation = False
        elif diverse:
            function_status = "diverse"
            activation_status = "recognized_diverse_function_not_activated"
            exception_status = "local"
            activation = False
        else:
            function_status = "own"
            activation_status = "recognized_not_executed"
            exception_status = "none_detected_requires_contextual_review"
            activation = True
        return {
            "id": item.get("id"),
            "title": item["title"],
            "path": item["path"],
            "repository_path": item.get("repository_path"),
            "identity": identity,
            "content_recovered": True,
            "start": start,
            "end": end,
            "activation": activation,
            "function_status": function_status,
            "activation_status": activation_status,
            "exception_status": exception_status,
        }

    # Explicit selectors are validated against registry identity, not guessed.
    explicit_selectors = []
    for match in re.finditer(r"(?i)\binstrument_id\s*:\s*([a-z0-9][a-z0-9._-]*)", request):
        explicit_selectors.append(("id", match.group(1), "matched_by_id", match.start(), match.end()))
    for match in re.finditer(r"(?i)\binstrument_path\s*:\s*(instruments/[A-Za-z0-9._/-]+)", request):
        explicit_selectors.append(("path", match.group(1).rstrip(".,;:!?"), "matched_by_path", match.start(), match.end()))
    explicit_item_ids = set()
    explicit_item_paths = set()
    for kind, value, identity, start, end in explicit_selectors:
        item = all_by_id.get(value) if kind == "id" else all_by_repo_path.get(value)
        if item is None:
            matches.append({
                "id": value if kind == "id" else None,
                "title": None,
                "path": None,
                "repository_path": value if kind == "path" else None,
                "identity": "unresolved_explicit_id" if kind == "id" else "unresolved_explicit_path",
                "content_recovered": False,
                "start": start,
                "end": end,
                "activation": False,
                "function_status": "unresolved",
                "activation_status": "explicit_reference_not_found",
                "exception_status": "invalid_explicit_reference",
            })
            continue
        disabled = not item.get("active", True)
        matches.append(make_match(item, identity, start, end, disabled=disabled))
        if not disabled:
            explicit_item_ids.add(item.get("id"))
            explicit_item_paths.add(item.get("repository_path"))

    # A normalized term may be a title or alias. Resolve only when all matching
    # enabled terms point to one instrument; title-vs-alias conflicts are ambiguous.
    terms = {}
    for item in active_catalog:
        normalized_aliases = item.get("normalized_aliases")
        if normalized_aliases is None:
            normalized_aliases = [normalize(alias) for alias in item.get("aliases", []) if isinstance(alias, str)]
        for term, kind in [(item["normalized_title"], "title")] + [(alias, "alias") for alias in normalized_aliases]:
            if term:
                terms.setdefault(term, {}).setdefault(item.get("id") or item["path"], {"item": item, "kinds": set()})["kinds"].add(kind)

    term_patterns = []
    for term, candidates in terms.items():
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)")
        for occurrence in pattern.finditer(normalized_request):
            # Prefer the longest matching term at the same start for the same instrument,
            # preventing an alias contained in a canonical title from duplicating it.
            candidate_ids = set(candidates)
            ambiguous = len(candidate_ids) > 1
            for candidate_key, candidate in candidates.items():
                item = candidate["item"]
                if item.get("id") in explicit_item_ids or item.get("repository_path") in explicit_item_paths:
                    continue
                term_patterns.append((occurrence.start(), occurrence.end(), term, candidate_key, candidate, ambiguous))

    # Suppress shorter overlapping terms for the same instrument and start offset.
    filtered = []
    for row in sorted(term_patterns, key=lambda x: (x[0], -(x[1]-x[0]))):
        start, end, term, candidate_key, candidate, ambiguous = row
        if any(old[0] == start and old[3] == candidate_key and old[1] >= end for old in filtered):
            continue
        filtered.append(row)

    filtered = [
        row for row in filtered
        if not (
            "alias" in row[4]["kinds"] and "title" not in row[4]["kinds"]
            and any(
                "title" in other[4]["kinds"]
                and other[0] <= row[0] and other[1] >= row[1]
                and (other[0] < row[0] or other[1] > row[1])
                for other in filtered
            )
        )
    ]
    for start, end, term, candidate_key, candidate, ambiguous in filtered:
        item = candidate["item"]
        after_start = end
        boundary = min(len(normalized_request), after_start + 140)
        for other_term in terms:
            next_match = re.search(r"(?<!\w)" + re.escape(other_term) + r"(?!\w)", normalized_request[after_start:boundary])
            if next_match:
                boundary = min(boundary, after_start + next_match.start())
        local_context = normalized_request[after_start:boundary]
        diverse = re.search(
            r"\b(?:funcao|papel|atribuicao)\s+(?:diferente|diversa|alternativa)\b|\batuar como\b",
            local_context,
        ) is not None
        kinds = candidate["kinds"]
        identity = "matched_by_title" if "title" in kinds else "matched_by_alias"
        matches.append(make_match(item, identity, start, end, ambiguous=ambiguous, diverse=diverse))

    matches.sort(key=lambda item: (item["start"], item["end"], item.get("path") or ""))
    return matches

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--request', required=True, type=Path)
    p.add_argument('--instruments', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    payload = json.loads(a.request.read_text(encoding='utf-8'))
    request_payload = payload.get('request', '')
    operation_context = None
    if isinstance(request_payload, str) and request_payload.lstrip().startswith('{'):
        try:
            parsed_request = json.loads(request_payload)
            if isinstance(parsed_request, dict) and ('schema_version' in parsed_request or 'operation' in parsed_request or 'demand' in parsed_request):
                request_payload = parsed_request
        except json.JSONDecodeError:
            pass
    if isinstance(request_payload, dict):
        # Accept a structured schema request without discarding its fields.
        operation_context = request_payload
        searchable_parts = []
        for key in ('operation', 'demand', 'title', 'origin', 'authorization', 'status'):
            value = request_payload.get(key)
            if isinstance(value, (str, int, float)):
                searchable_parts.append(str(value))
        for key in ('instrument_id', 'instrument_path'):
            value = request_payload.get(key)
            if isinstance(value, str) and value.strip():
                searchable_parts.append(f"{key}:{value.strip()}")
        for key in ('transformation', 'destinations', 'navigation_invariants', 'production_chain'):
            value = request_payload.get(key)
            if isinstance(value, list):
                searchable_parts.extend(str(item) for item in value if isinstance(item, (str, int, float)))
        request = '\n'.join(searchable_parts).strip()
        if not request:
            request = json.dumps(request_payload, ensure_ascii=False, sort_keys=True)
    else:
        request = str(request_payload).strip()
    if not request: raise SystemExit('Erro: demanda vazia.')
    instruments = read_instruments(a.instruments)
    matches = resolve(request, instruments)

    # Stable defaults: coordinator, master protocol, and GitHub operational instrument.
    registry_path = a.instruments.parent / "config" / "instrument-registry.json"
    if registry_path.is_file():
        # In production, mandatory preloading follows the explicitly enabled set.
        # Temporary test fixtures without a registry retain the legacy contract.
        default_titles = [(item["title"], "mandatory_active_instrument") for item in instruments if item.get("active", True)]
    else:
        default_titles = [
            ('ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS', 'mandatory_coordinator'),
            ('PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO', 'mandatory_master_protocol'),
            ('Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas', 'mandatory_fixed_component'),
        ]
    selected_paths = {x['path'] for x in matches if x.get('path')}
    mandatory_components = []
    missing_defaults = []
    for required_title, identity in default_titles:
        required_norm = normalize(required_title)
        component = next((x for x in instruments if x['normalized_title'] == required_norm), None)
        if component is None:
            missing_defaults.append(required_title)
            continue
        if component['path'] not in selected_paths:
            matches.append({'title': component['title'], 'path': component['path'], 'identity': identity, 'content_recovered': True, 'function_status': 'content_available_for_review', 'activation_status': 'included_in_plan_not_executed', 'exception_status': 'requires_contextual_review'})
            selected_paths.add(component['path'])
        mandatory_components.append({'required_title': required_title, 'found': True, 'path': component['path']})

    # Additional default preconfiguration: preserve the repository's existing
    # architecture while making catalog/sitemap synchronization guidance available
    # for every future request. This is not counted as one of the three legacy
    # mandatory components, so the existing result contract remains compatible.
    preconfig_title = 'PRÉCONFIGURAÇÃO DE SINCRONIZAÇÃO, CORREFERÊNCIA E VALIDAÇÃO AUTOMÁTICA DA PROMPTÁRIA'
    preconfig_norm = normalize(preconfig_title)
    preconfig = next((x for x in instruments if x['normalized_title'] == preconfig_norm), None)
    if preconfig is not None and preconfig.get('active', True) and preconfig['path'] not in selected_paths:
        matches.append({
            'title': preconfig['title'],
            'path': preconfig['path'],
            'identity': 'mandatory_preconfiguration_sync',
            'content_recovered': True,
            'function_status': 'content_available_for_review',
            'activation_status': 'included_in_plan_not_executed',
            'exception_status': 'requires_contextual_review'
        })
        selected_paths.add(preconfig['path'])

    # Functional cross-reference preconfiguration: add the new architecture to every
    # future plan when present, without duplicating an already selected instrument.
    correferencia_title = 'ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS: ACIONAMENTO COORDENADO DE INSTRUMENTOS PROMPTUAIS E ARQUITETURA DE ACIONAMENTO, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS, COM CORREFERÊNCIA FUNCIONAL AUTOMÁTICA POR TÍTULOS DOS INSTRUMENTOS PROMPTUAIS, NA QUAL A MENÇÃO GENÉRICA IDENTIFICA O INSTRUMENTO, PRESERVA SUA FUNÇÃO PRÓPRIA E ACIONA SUA EXECUÇÃO, SALVO ATRIBUIÇÃO ESPECÍFICA E INEQUÍVOCA DE FUNÇÃO DIVERSA, COM RECONHECIMENTO MÚTUO, CUMULATIVO, COORDENADO E SIMULTÂNEO DE MÚLTIPLOS TÍTULOS'
    correferencia_norm = normalize(correferencia_title)
    correferencia = next((x for x in instruments if x['normalized_title'] == correferencia_norm), None)
    if correferencia is not None and correferencia.get('active', True) and correferencia['path'] not in selected_paths:
        matches.append({
            'title': correferencia['title'],
            'path': correferencia['path'],
            'identity': 'mandatory_functional_cross_reference_preconfiguration',
            'content_recovered': True,
            'function_status': 'content_available_for_review',
            'activation_status': 'included_in_plan_not_executed',
            'exception_status': 'requires_contextual_review'
        })
        selected_paths.add(correferencia['path'])

    # Always preload the update-integrity protocol for future demands. It is
    # included as a planning dependency, not executed implicitly, and does not
    # alter the three legacy mandatory components or their result contract.
    update_protocol_title = 'PROTOCOLO OPERACIONAL DE ATUALIZAÇÃO, REINTEGRAÇÃO E PRESERVAÇÃO FUNCIONAL DO ACERVO DE INSTRUMENTOS PROMPTUAIS DO PROMPTÁRIA'
    update_protocol_norm = normalize(update_protocol_title)
    update_protocol = next((x for x in instruments if x['normalized_title'] == update_protocol_norm), None)
    if update_protocol is not None and update_protocol.get('active', True) and update_protocol['path'] not in selected_paths:
        matches.append({
            'title': update_protocol['title'],
            'path': update_protocol['path'],
            'identity': 'mandatory_update_integrity_preconfiguration',
            'content_recovered': True,
            'function_status': 'content_available_for_review',
            'activation_status': 'included_in_plan_not_executed',
            'exception_status': 'requires_contextual_review'
        })
        selected_paths.add(update_protocol['path'])

    # Always include the Nocturna instrument as a future-plan dependency.
    # This is discovery/planning only: it does not claim access to the external
    # Nocturna repository and does not execute the instrument.
    nocturna_title = "Nocturna — Arquitetura da Necessidade e Reconstrução Recursiva da Identidade Sistêmica: Princípio, Origem e Fim na Unidade Fractal entre o Explícito e o Implícito, o Físico e o Metafísico, o Universal e o Particular, mediante a Integração Documental, a Correferência Multiescalar, a Indução Causal, a Verificação das Derivações e o Fechamento Arquitetônico da Totalidade — Conservar o Fundamento, Transformar a Função, Reconstruir a Necessidade, Revelar o Todo em Cada Parte e Reconhecer na Origem a Presença Integral de Todas as Consequências Legítimas."
    nocturna_norm = normalize(nocturna_title)
    nocturna = next((x for x in instruments if x['normalized_title'] == nocturna_norm), None)
    if nocturna is not None and nocturna.get('active', True) and nocturna['path'] not in selected_paths:
        matches.append({
            'title': nocturna['title'],
            'path': nocturna['path'],
            'identity': 'mandatory_nocturna_architecture_preconfiguration',
            'content_recovered': True,
            'function_status': 'content_available_for_review',
            'activation_status': 'included_in_plan_not_executed',
            'exception_status': 'requires_contextual_review'
        })
        selected_paths.add(nocturna['path'])

    destination = validate_destination(payload.get('destination', ''))
    dry_run_value = payload.get('dry_run', True)
    if not isinstance(dry_run_value, bool):
        raise SystemExit("dry_run inválido: use um valor booleano JSON (true/false).")
    dry_run = dry_run_value
    write_authorized = payload.get('write_authorized', False)
    if not isinstance(write_authorized, bool):
        raise SystemExit("write_authorized inválido: use um valor booleano JSON.")
    # There is deliberately no write executor yet. Fail closed if a caller requests
    # a non-dry run without an explicit authorization and destination.
    if not dry_run and (write_authorized is not True or not destination):
        raise SystemExit("Execução recusada: exige write_authorized=true e destination explícito; o executor de escrita ainda não está integrado.")
    result = {
        'schema_version': 2,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'request': request,
        'source_event': payload.get('source_event'),
        'source_schema_version': operation_context.get('schema_version') if operation_context else None,
        'operation_context': {
            'preserved_as_received': True,
            # Keep the complete original object, including unknown/future fields.
            # The named fields below remain as compatibility aliases for consumers.
            'original_payload': operation_context,
            'operation': operation_context.get('operation'),
            'demand': operation_context.get('demand'),
            'source': operation_context.get('source'),
            'transformation': operation_context.get('transformation', []),
            'destinations': operation_context.get('destinations', []),
            'validation': operation_context.get('validation'),
            'production_chain': operation_context.get('production_chain', []),
            'navigation_invariants': operation_context.get('navigation_invariants', []),
            'status': operation_context.get('status'),
            'review_required_before_mutation': True,
            'historical_snapshots_are_not_current_state': True
        } if operation_context else None,
        'destination': destination or None,
        'dry_run': dry_run,
        'write_authorized': write_authorized,
        'write_execution_available': False,

        'matching_policy': {
            'case_insensitive': True,
            'unicode_normalized': True,
            'punctuation_insensitive': True,
            'all_matches_retained': True,
            'no_arbitrary_cardinality_limit': True,
            'substring_only_matches': False,
            'identity_precedence': ['explicit_instrument_id', 'explicit_repository_path', 'unique_normalized_title', 'unique_normalized_alias'],
            'explicit_selectors': ['instrument_id', 'instrument_path'],
            'aliases_resolve_only_when_unique': True,
            'ambiguous_title_or_alias': 'do_not_activate',
            'disabled_instruments': 'never_auto_enabled',
        },
        'preconfiguration': {
            'enabled': True,
            'mode': 'generic_until_explicit_specialization',
            'always_include_coordinator': not registry_path.is_file() or normalize('ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS') in {item['normalized_title'] for item in instruments if item.get('active', True)},
            'always_include_master_protocol': not registry_path.is_file() or normalize('PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO') in {item['normalized_title'] for item in instruments if item.get('active', True)},
            'always_include_github_operational_instrument': not registry_path.is_file() or normalize('Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas') in {item['normalized_title'] for item in instruments if item.get('active', True)},
            'preserve_instrument_functions': True,
            'ambiguous_function_override_requires_contextual_review': True,
        },
        'instrument_count': len(instruments),
        'matched_instruments': matches,
        'unmatched_title_note': 'Nenhum título adicional correspondente foi encontrado; os componentes fixos continuam incluídos.' if not resolve(request, instruments) else None,
        'mandatory_components': mandatory_components,
        'missing_mandatory_components': missing_defaults,
        'status': 'plan_created_needs_execution_integration',
        'limitations': ['Só processa demandas transmitidas por workflow_dispatch ou comentário /promptaria.', 'Identificar ou incluir um título no plano não comprova execução da função especializada.', 'A função diversa exige interpretação contextual; o script sinaliza revisão.', 'Não escreve resultados nem acessa automaticamente conversas do ChatGPT.'] + ([f'Componente obrigatório ausente: {title}.' for title in missing_defaults])
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Instrumentos encontrados: {len(matches)}")
    print(f"Componentes obrigatórios disponíveis: {len(mandatory_components)}/{len(default_titles)}")
    if missing_defaults:
        print('Componentes obrigatórios ausentes: ' + '; '.join(missing_defaults))
    print(f'Resultado: {a.output}')

if __name__ == '__main__': main()
