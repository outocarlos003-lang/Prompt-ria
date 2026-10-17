#!/usr/bin/env python3
"""Resolve Promptária instrument titles without inventing missing content."""
from __future__ import annotations
import argparse, json, re, unicodedata
from datetime import datetime, timezone
from pathlib import Path

def normalize(value: str) -> str:
    value = unicodedata.normalize('NFKC', value).casefold()
    value = re.sub(r'[\u200b-\u200f\ufeff]', '', value)
    value = re.sub(r'[^\w\s-]', ' ', value, flags=re.UNICODE)
    return re.sub(r'\s+', ' ', value).strip()

def read_instruments(root: Path) -> list[dict]:
    items = []
    if not root.exists(): return items
    for path in sorted(root.rglob('*.md')):
        text = path.read_text(encoding='utf-8')
        match = re.search(r'(?m)^#\s+(.+?)\s*$', text)
        if match:
            title = match.group(1).strip()
            items.append({'title': title, 'path': path.as_posix(), 'content': text, 'normalized_title': normalize(title)})
    return items

def resolve(request: str, instruments: list[dict]) -> list[dict]:
    normalized_request = normalize(request)
    matches = []
    for instrument in instruments:
        title = instrument['normalized_title']
        if title and re.search(r'(?<!\w)' + re.escape(title) + r'(?!\w)', normalized_request):
            matches.append({'title': instrument['title'], 'path': instrument['path'], 'identity': 'matched_by_title', 'content_recovered': True, 'function_status': 'content_available_for_review', 'activation_status': 'recognized_not_executed', 'exception_status': 'requires_contextual_review'})
    return matches

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--request', required=True, type=Path)
    p.add_argument('--instruments', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    payload = json.loads(a.request.read_text(encoding='utf-8'))
    request = str(payload.get('request', '')).strip()
    if not request: raise SystemExit('Erro: demanda vazia.')
    instruments = read_instruments(a.instruments)
    matches = resolve(request, instruments)

    # Stable defaults: coordinator, master protocol, and GitHub operational instrument.
    default_titles = [
        ('ARQUITETURA UNIFICADA DE ACIONAMENTO, CORREFERÊNCIA, RECUPERAÇÃO E APLICAÇÃO DE INSTRUMENTOS PROMPTUAIS', 'mandatory_coordinator'),
        ('PROTOCOLO-MESTRE DE ACIONAMENTO DE INSTRUMENTOS PROMPTUAIS PRONTO PARA EXECUÇÃO', 'mandatory_master_protocol'),
        ('Acione a Promptária pelo GitHub para Inserir, Recuperar e Aplicar Demandas', 'mandatory_fixed_component'),
    ]
    selected_paths = {x['path'] for x in matches}
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

    destination = str(payload.get('destination', '')).strip()
    if destination:
        target = Path(destination)
        if target.is_absolute() or '..' in target.parts: raise SystemExit('Destino recusado: use caminho relativo sem ..')
    result = {
        'schema_version': 2,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'request': request,
        'source_event': payload.get('source_event'),
        'destination': destination or None,
        'dry_run': bool(payload.get('dry_run', True)),
        'matching_policy': {'case_insensitive': True, 'unicode_normalized': True, 'punctuation_insensitive': True, 'all_matches_retained': True, 'no_arbitrary_cardinality_limit': True, 'substring_only_matches': False},
        'preconfiguration': {'enabled': True, 'mode': 'generic_until_explicit_specialization', 'always_include_coordinator': True, 'always_include_master_protocol': True, 'always_include_github_operational_instrument': True, 'preserve_instrument_functions': True, 'ambiguous_function_override_requires_contextual_review': True},
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
    print(f"Componente fixo disponível: {'sim' if fixed else 'não'}")
    print(f'Resultado: {a.output}')

if __name__ == '__main__': main()
