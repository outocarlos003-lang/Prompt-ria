"""Validate Promptária title correference and produce a non-executing traceable plan."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


def _fold_with_offsets(value: str) -> tuple[str, list[int]]:
    chars, offsets = [], []
    for index, char in enumerate(value):
        folded = unicodedata.normalize("NFKD", char)
        for part in folded:
            if unicodedata.combining(part):
                continue
            if part in "\u200b\u200c\u200d\u200e\u200f\ufeff":
                continue
            chars.append(part.casefold())
            offsets.append(index)
    return "".join(chars), offsets


def _normalize(value: str) -> str:
    folded, _ = _fold_with_offsets(value)
    folded = re.sub(r"[^\w\s-]", " ", folded, flags=re.UNICODE)
    return re.sub(r"[\s-]+", " ", folded).strip()


def _read_title(path: Path) -> str | None:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    if path.suffix.lower() in {".html", ".htm"}:
        match = re.search(r"<title[^>]*>(.*?)</title>", content, re.I | re.S)
        if not match:
            match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.I | re.S)
        if match:
            return re.sub(r"<[^>]+>", "", match.group(1)).strip()
    match = re.search(r"(?m)^#\s+(.+?)\s*$", content)
    return match.group(1).strip() if match else None


def _catalog(root: Path) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    items: list[dict] = []
    repo_root = root
    instrument_dir = root / "instruments" if (root / "instruments").is_dir() else root
    registry_path = root / "config" / "instrument-registry.json"
    manifest_path = root / "tests" / "manifest.json"
    manifest_local = root / "manifest.json"
    registry_entries: list[dict] | None = None
    if registry_path.is_file():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry_entries = registry.get("instruments", [])
            if not isinstance(registry_entries, list):
                errors.append("coleção de instrumentos inválida no registro")
                registry_entries = []
        except (OSError, json.JSONDecodeError):
            errors.append("registro de instrumentos inválido")
            registry_entries = []
    manifest_entries: list[dict] | None = None
    active_manifest = manifest_local if manifest_local.is_file() else manifest_path
    if active_manifest.is_file():
        try:
            manifest = json.loads(active_manifest.read_text(encoding="utf-8"))
            manifest_entries = manifest.get("instruments", [])
            if not isinstance(manifest_entries, list):
                errors.append("coleção de instrumentos inválida no manifesto")
                manifest_entries = []
        except (OSError, json.JSONDecodeError):
            errors.append("manifesto de instrumentos inválido")
            manifest_entries = []

    if manifest_entries is not None:
        for entry in manifest_entries:
            if not isinstance(entry, dict):
                errors.append("entrada inválida no manifesto")
                continue
            relpath = entry.get("path")
            if not isinstance(relpath, str) or not relpath.strip():
                errors.append("caminho inválido no manifesto")
                continue
            candidate = (active_manifest.parent.parent / relpath) if active_manifest == manifest_path else (root / relpath)
            resolved_root = root.resolve()
            try:
                resolved_candidate = candidate.resolve()
                if resolved_root not in resolved_candidate.parents:
                    errors.append(f"caminho fora da raiz: {relpath}")
                    continue
            except OSError:
                errors.append(f"caminho inválido: {relpath}")
                continue
            title = _read_title(candidate)
            if title is None:
                errors.append(f"arquivo de instrumento ausente ou sem título: {relpath}")
                continue
            expected = entry.get("title")
            if isinstance(expected, str) and _normalize(expected) != _normalize(title):
                errors.append(f"título divergente no manifesto: {relpath}")
                continue
            registry_item = next((item for item in (registry_entries or [])
                                  if isinstance(item, dict) and item.get("path") == relpath), None)
            enabled = True if registry_entries is None else bool(
                registry_item and isinstance(registry_item.get("activation"), dict)
                and registry_item["activation"].get("enabled") is True
            )
            items.append({"id": entry.get("id"), "title": title, "path": relpath,
                          "aliases": entry.get("aliases", []) if isinstance(entry.get("aliases", []), list) else [],
                          "active": enabled})
    else:
        for path in sorted(instrument_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".html", ".htm"}:
                continue
            title = _read_title(path)
            if not title:
                continue
            relpath = path.relative_to(repo_root).as_posix()
            items.append({"id": None, "title": title, "path": relpath, "aliases": [], "active": True})

    seen: dict[str, list[dict]] = {}
    for item in items:
        seen.setdefault(_normalize(item["title"]), []).append(item)
    duplicates = [group for group in seen.values() if len(group) > 1]
    if duplicates:
        for group in duplicates:
            errors.append("título canônico ambíguo: " + group[0]["title"])
    return items, errors


def _destination(prompt: str) -> dict:
    match = re.search(r"(?im)^\s*Destino\s*:\s*(.+?)\s*$", prompt)
    value = match.group(1).strip() if match else None
    if value:
        value = re.sub(r"\s+Autorizo explicitamente a escrita\.?\s*$", "", value, flags=re.I).strip()
        value = value.rstrip().rstrip(".").strip()
    is_nocturna = bool(value and _normalize(value) == "nocturna")
    return {
        "value": value,
        "status": "resolved_candidate" if value else "missing",
        "is_nocturna": is_nocturna,
        "materialization_allowed": False,
        "authorization_status": "not_granted_by_destination_text",
    }


def validate(prompt: str, root: Path) -> dict:
    """Resolve known title mentions while keeping execution and writing disabled."""
    if not isinstance(prompt, str):
        raise TypeError("prompt must be text")
    root = Path(root)
    items, errors = _catalog(root)
    folded_prompt, offsets = _fold_with_offsets(prompt)
    candidates = []
    for item in items:
        if not item.get("active"):
            continue
        for alias in [item["title"], *item.get("aliases", [])]:
            if not isinstance(alias, str) or not alias.strip():
                continue
            folded_alias, _ = _fold_with_offsets(alias)
            # Keep punctuation as separators, but match only complete word sequences.
            folded_alias = re.sub(r"[^\w\s-]", " ", folded_alias, flags=re.UNICODE)
            folded_alias = re.sub(r"[\s-]+", " ", folded_alias).strip()
            if not folded_alias:
                continue
            pattern = re.compile(r"(?<!\w)" + r"\s+".join(re.escape(x) for x in folded_alias.split()) + r"(?!\w)")
            for match in pattern.finditer(folded_prompt):
                if not offsets or match.start() >= len(offsets) or match.end() - 1 >= len(offsets):
                    continue
                start, end = offsets[match.start()], offsets[match.end() - 1] + 1
                candidates.append((start, end, item, alias))
    # Prefer longer canonical matches at the same location; retain repeated mentions.
    candidates.sort(key=lambda value: (value[0], -(value[1] - value[0]), value[2]["path"]))
    selected = []
    for candidate in candidates:
        if any(candidate[0] < existing[1] and candidate[1] > existing[0]
               for existing in selected):
            continue
        selected.append(candidate)
    selected.sort(key=lambda value: value[0])

    matches = []
    for index, (start, end, item, alias) in enumerate(selected):
        sentence_start = max(prompt.rfind(".", 0, start), prompt.rfind("!", 0, start), prompt.rfind("?", 0, start)) + 1
        ends = [pos for pos in (prompt.find(".", end), prompt.find("!", end), prompt.find("?", end)) if pos >= 0]
        sentence_end = min(ends) + 1 if ends else len(prompt)
        sentence = prompt[sentence_start:sentence_end]
        # A diverse-function clause applies to the nearest preceding mention in its sentence.
        local_text = prompt[start:(selected[index + 1][0] if index + 1 < len(selected) else sentence_end)]
        diverse = bool(re.search(r"outra\s+fun[cç][aã]o|fun[cç][aã]o\s+diversa|desempenhar\s+outra", local_text, re.I))
        is_active = not diverse
        matches.append({
            "instrument_id": item.get("id"), "title": item["title"], "path": item["path"],
            "start": start, "end": end, "active": is_active,
            "function_status": "diversa" if diverse else "propria_preservada",
            "exception_scope": "occurrence" if diverse else None,
            "correferencia": True, "match_type": "canonical_title" if _normalize(alias) == _normalize(item["title"]) else "alias",
        })

    active_matches = [item for item in matches if item["active"]]
    active_instruments = []
    seen_active = set()
    for item in active_matches:
        key = (item["instrument_id"], item["title"], item["path"])
        if key not in seen_active:
            active_instruments.append({"instrument_id": item["instrument_id"], "title": item["title"],
                                       "path": item["path"], "activation": True,
                                       "function_status": "own"})
            seen_active.add(key)
    destination = _destination(prompt)
    policy = {
        "sections": [f"section_{index}" for index in range(1, 20)],
        "github_limits": {
            "actions_process_only_received_request": True,
            "does_not_observe_untransmitted_chat": True,
            "does_not_create_permissions": True,
            "does_not_create_access": True,
        },
    }
    coordination = {
        "coordination": {"is_cumulative": True, "is_nonexclusive": True},
        "github_limits": policy["github_limits"],
        "destination": destination,
        "unresolved_explicit_additional_titles": [],
    }
    # Do not guess missing titles explicitly requested as quoted title fields.
    for explicit in re.findall(r't[ií]tulo\s*:\s*["“](.+?)["”]', prompt, re.I):
        if not any(_normalize(explicit) == _normalize(item["title"]) for item in items):
            coordination["unresolved_explicit_additional_titles"].append(
                {"title": explicit, "status": "catalog_missing"}
            )
    status = "catalog_inconsistente" if errors else (
        "plan_created_needs_execution_integration" if matches else "no_match"
    )
    return {
        "schema_version": 2, "status": status, "request": prompt,
        "matched_occurrences": len(matches), "matches": matches,
        "active_instruments": active_instruments,
        "execution_plan": [{"title": item["title"], "path": item["path"],
                            "mode": "preserve_own_function"} for item in active_instruments],
        "exceptions": [item for item in matches if not item["active"]],
        "validation_errors": errors,
        "coordination": coordination, "architecture_policy": policy,
        "destination": destination, "dry_run": True, "write_authorized": False,
        "write_execution_available": False, "execution_performed": False,
    }
