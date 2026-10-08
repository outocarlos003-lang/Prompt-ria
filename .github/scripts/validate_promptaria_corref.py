#!/usr/bin/env python3
"""
Valida títulos de instrumentos da Promptária em uma requisição textual.

Regra:
- título encontrado => correferência com o instrumento de mesmo título;
- ausência de desvio explícito => função própria ativa;
- função diversa só é reconhecida quando o contexto próximo contém uma
  atribuição expressa/inequívoca de finalidade, papel ou comportamento diverso;
- múltiplos títulos permanecem ativos cumulativamente.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path("Promptária")
WINDOW = 900

# Frases deliberadamente conservadoras: a exceção precisa indicar desvio
# funcional, não simples ausência de descrição.
DIVERSE_PATTERNS = [
    r"\b(?:use|utilize|empregue|empregar|trate|consider(?:e|ar)|faça|faca)\b.{0,180}\b{TITLE}\b.{0,220}\b(?:como|para|na função de|no papel de|com a finalidade de)\b",
    r"\b{TITLE}\b.{0,220}\b(?:como|para|na função de|no papel de|com a finalidade de)\b.{0,220}\b(?:em vez de|ao invés de|diferente de|outra finalidade|outra função|outro papel)\b",
    r"\b{TITLE}\b.{0,180}\b(?:não deve|nao deve|deve ser usado para|deve ser utilizada para|deve atuar como|deve desempenhar|deverá atuar como|deverá desempenhar)\b",
    r"\b{TITLE}\b.{0,180}\b(?:exclusivamente para|somente para)\b.{0,160}\b(?:outra|diversa|diferente)\b",
]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).casefold()
    s = "".join(c for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def extract_text(raw: str) -> str:
    raw = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return html.unescape(re.sub(r"\s+", " ", raw)).strip()


def instrument_catalog() -> list[dict]:
    items = []
    if not ROOT.exists():
        return items
    for p in sorted(ROOT.iterdir()):
        if not p.is_dir():
            continue
        f = p / "Index.html"
        if not f.is_file():
            continue
        raw = f.read_text(encoding="utf-8", errors="replace")
        text = extract_text(raw)
        # Prefer the HTML title, then the first heading-like line.
        m = re.search(r"<title>\s*(.*?)\s*</title>", raw, re.I | re.S)
        title = html.unescape(m.group(1)).strip() if m else p.name.replace("-", " ")
        items.append({
            "title": title,
            "path": str(f),
            "function_excerpt": text[:1200],
        })
    return items


def has_diverse_assignment(context: str, title: str) -> bool:
    t = re.escape(norm(title))
    c = norm(context)
    for pattern in DIVERSE_PATTERNS:
        if re.search(pattern.format(TITLE=t), c, re.I):
            return True
    # Also catch explicit negation immediately attached to the title.
    if re.search(rf"\b{t}\b\s+(?:não|nao)\s+(?:deve|deverá|será|é|e)", c, re.I):
        return True
    return False


def validate(prompt: str) -> dict:
    catalog = instrument_catalog()
    normalized_prompt = norm(prompt)
    matches = []

    for item in catalog:
        title = item["title"]
        nt = norm(title)
        if not nt:
            continue
        # Match the full title as a normalized literal, retaining all occurrences.
        starts = [m.start() for m in re.finditer(re.escape(nt), normalized_prompt)]
        for start in starts:
            context = normalized_prompt[max(0, start-WINDOW):min(len(normalized_prompt), start+len(nt)+WINDOW)]
            diverse = has_diverse_assignment(context, title)
            matches.append({
                "title": title,
                "instrument": item["path"],
                "function_status": "diversa_explicitamente_atribuida" if diverse else "propria_acionada",
                "correferencia": True,
                "active": not diverse,
                "context_window": context,
            })

    # Stable, cumulative identity: do not collapse different titles.
    by_title = {}
    for m in matches:
        by_title.setdefault(m["title"], []).append(m)

    active = [m for m in matches if m["active"]]
    return {
        "rule": {
            "generic_mention_preserves_function": True,
            "absence_of_function_description_is_not_diverse": True,
            "diverse_function_requires_explicit_or_unequivocal_context": True,
            "multiple_titles_are_cumulative_and_simultaneous": True,
        },
        "instrument_count": len(catalog),
        "matched_occurrences": len(matches),
        "matched_titles": list(by_title.keys()),
        "active_instruments": [
            {"title": m["title"], "instrument": m["instrument"]}
            for m in active
        ],
        "matches": matches,
        "status": "ok",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", help="Texto a validar.")
    ap.add_argument("--prompt-file", help="Arquivo com o texto a validar.")
    ap.add_argument("--output", default="correferencia-result.json")
    args = ap.parse_args()

    if bool(args.prompt) == bool(args.prompt_file):
        ap.error("Use exatamente um de --prompt ou --prompt-file.")
    prompt = args.prompt if args.prompt is not None else Path(args.prompt_file).read_text(encoding="utf-8")

    result = validate(prompt)
    Path(args.output).write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps({
        "status": result["status"],
        "matched_titles": result["matched_titles"],
        "active_instruments": result["active_instruments"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
