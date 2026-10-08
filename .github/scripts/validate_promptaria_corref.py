#!/usr/bin/env python3
"""Validação técnica da correferência funcional da Promptária."""
from __future__ import annotations
import argparse, html, json, re, unicodedata
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

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = "".join(c for c in unicodedata.normalize("NFD", value)
                    if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", value).strip()

def html_title(raw: str) -> str | None:
    m = re.search(r"<title>\s*(.*?)\s*</title>", raw, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else None

def instrument_catalog(root: Path = ROOT) -> list[dict]:
    """Lê metadados dos instrumentos; não altera seu conteúdo."""
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
        aliases = []
        for candidate in (title, directory.name.replace("-", " ")):
            if candidate and norm(candidate) not in {norm(x) for x in aliases}:
                aliases.append(candidate)
        items.append({"title": title, "aliases": aliases, "instrument": str(index)})
    return items

def local_context(text: str, start: int, end: int) -> str:
    """Mantém a análise da exceção local à ocorrência."""
    left, right = max(0, start - CONTEXT_RADIUS), min(len(text), end + CONTEXT_RADIUS)
    window = text[left:right]
    rel_start, rel_end = start - left, end - left
    separators = list(re.finditer(r"(?:[.!?;]|\n\s*\n)", window))
    begin, finish = 0, len(window)
    for sep in reversed(separators):
        if sep.end() <= rel_start:
            begin = sep.end()
            break
    for sep in separators:
        if sep.start() >= rel_end:
            finish = sep.start()
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
        c, re.I
    ))

def validate(prompt: str, root: Path = ROOT) -> dict:
    catalog, normalized_prompt, matches = instrument_catalog(root), norm(prompt), []
    for item in catalog:
        seen = set()
        for alias in item["aliases"]:
            needle = norm(alias)
            if not needle:
                continue
            for match in re.finditer(re.escape(needle), normalized_prompt):
                occurrence = (match.start(), match.end())
                if occurrence in seen:
                    continue
                seen.add(occurrence)
                context = local_context(normalized_prompt, *occurrence)
                diverse = has_diverse_assignment(context, alias)
                matches.append({
                    "title": item["title"],
                    "matched_text": normalized_prompt[match.start():match.end()],
                    "instrument": item["instrument"],
                    "correferencia": True,
                    "function_status": "diversa_explicitamente_atribuida" if diverse else "propria_preservada",
                    "active": not diverse,
                    "exception_scope": "occurrence" if diverse else None,
                    "context_window": context,
                })
    index = {}
    for match in matches:
        index.setdefault(match["title"], []).append(match)
    active = [m for m in matches if m["active"]]
    return {
        "schema_version": "2.0",
        "rule": {
            "generic_mention_establishes_corref": True,
            "generic_mention_preserves_own_function": True,
            "silence_is_not_diverse_function": True,
            "ambiguity_favors_own_function": True,
            "diverse_function_requires_explicit_or_unequivocal_context": True,
            "exception_is_local_to_occurrence": True,
            "multiple_titles_are_independent_cumulative_and_nonexclusive": True,
            "instrument_content_is_not_modified": True,
        },
        "instrument_count": len(catalog),
        "matched_occurrences": len(matches),
        "matched_titles": list(index),
        "active_instruments": [{"title": m["title"], "instrument": m["instrument"]} for m in active],
        "exceptions": [m for m in matches if not m["active"]],
        "matches": matches,
        "status": "ok",
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
        "matched_occurrences": result["matched_occurrences"],
        "matched_titles": result["matched_titles"],
        "active_instruments": result["active_instruments"],
        "exceptions": result["exceptions"],
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
