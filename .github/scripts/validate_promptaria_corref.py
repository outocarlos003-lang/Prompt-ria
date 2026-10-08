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
    return "".join(out).strip(), out_origins


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

    status = "ok" if not consistency_errors else "catalog_inconsistente"
    return {
        "schema_version": "3.0",
        "status": status,
        "validation_errors": consistency_errors,
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
