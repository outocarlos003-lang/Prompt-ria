#!/usr/bin/env python3
"""Resolve Promptária instrument references by title without editing instruments."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

EXCLUDED_PARTS = {".git", ".github", "node_modules", "vendor"}
EXCLUDED_PREFIXES = ("docs/system/", "system/")


def normalize(value: str) -> str:
    """Normalize superficial title differences without inferring semantic similarity."""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.casefold().strip()
    value = re.sub(r"[*_~]", "", value)
    value = re.sub(r"[^\w\s-]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def git_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True
    ).stdout
    return [Path(p.decode("utf-8")) for p in result.split(b"\0") if p]


def eligible(path: Path) -> bool:
    parts = set(path.parts)
    return (
        path.suffix.lower() in {".md", ".markdown"}
        and not (parts & EXCLUDED_PARTS)
        and not str(path).startswith(EXCLUDED_PREFIXES)
    )


def instrument_index() -> dict[str, list[dict[str, str]]]:
    """Build the title index once per run, retaining every distinct file candidate."""
    index: dict[str, list[dict[str, str]]] = {}
    for path in git_files():
        if not eligible(path) or not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        candidates = [(path.stem, "filename")]
        for line in content.splitlines():
            match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
            if match:
                candidates.append((match.group(1).strip(), "heading"))
        for title, source in candidates:
            key = normalize(title)
            if key:
                entry = {"title": title, "path": path.as_posix(), "matched_by": source}
                entries = index.setdefault(key, [])
                # Avoid duplicate records for the same path/title/source combination.
                if entry not in entries:
                    entries.append(entry)
    add_manifest_entries(index)
    return index


def add_manifest_entries(
    index: dict[str, list[dict[str, str]]],
    manifest_path: Path = Path("Promptária/manifest.json"),
) -> None:
    """Add canonical manifest titles without treating aliases as activation titles."""
    if not manifest_path.is_file():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return
    for instrument in manifest.get("instruments", []):
        title = str(instrument.get("title", "")).strip()
        path = str(instrument.get("path", "")).strip()
        if not title or not path:
            continue
        key = normalize(title)
        entry = {
            "id": str(instrument.get("id", "")).strip(),
            "title": title,
            "path": path,
            "matched_by": "manifest",
        }
        entries = index.setdefault(key, [])
        if entry not in entries:
            entries.append(entry)
        instrument_id = entry["id"]
        if instrument_id:
            id_entries = index.setdefault("__id__:" + instrument_id, [])
            if entry not in id_entries:
                id_entries.append(entry)


def safe_manifest_path(raw_path: str, repo_root: Path | None = None) -> Path | None:
    """Return a manifest path only when it stays inside the repository."""
    candidate = Path(raw_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    root = (repo_root if repo_root is not None else Path.cwd()).resolve()
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root):
        return None
    return resolved


def resolve(title: str, index: dict[str, list[dict[str, str]]]) -> dict:
    # Stable IDs take precedence over titles, matching the JavaScript resolver contract.
    id_matches = index.get("__id__:" + title.strip(), [])
    candidates = id_matches if id_matches else index.get(normalize(title), [])
    # Multiple headings in one file are not ambiguous; distinct files are.
    by_path: dict[str, dict[str, str]] = {}
    for item in candidates:
        by_path.setdefault(item["path"], item)
    matches = list(by_path.values())
    if not matches:
        return {"input_title": title, "status": "not_found", "matches": []}
    if len(matches) > 1:
        return {"input_title": title, "status": "ambiguous", "matches": matches}
    item = matches[0]
    content_path = Path(item["path"])
    if item.get("matched_by") == "manifest":
        safe_path = safe_manifest_path(item["path"])
        if safe_path is None:
            return {
                "input_title": title,
                "status": "invalid_manifest_path",
                "matches": [item],
                "error": "manifest path must stay inside the repository and be relative",
            }
        content_path = safe_path
    try:
        content = content_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {
            "input_title": title,
            "status": "identified_content_unavailable",
            "matches": [item],
            "error": str(exc),
        }
    return {
        "input_title": title,
        "status": "identified_and_recovered",
        "matches": [item],
        "content": content,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", action="append", default=[])
    parser.add_argument("--titles-file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    titles = list(args.title)
    if args.titles_file:
        titles.extend(
            line.strip()
            for line in Path(args.titles_file).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    if not titles:
        parser.error("provide at least one --title or --titles-file")

    # The repository scan is independent of the number of requested titles.
    index = instrument_index()
    results = [resolve(title, index) for title in titles]
    payload = {
        "schema_version": 1,
        "principles": {
            "preserve_instrument_files": True,
            "all_titles_processed": True,
            "no_arbitrary_selection": True,
            "ambiguous_matches_are_not_guessed": True,
            "identification_is_not_execution": True,
        },
        "results": results,
    }
    print(
        json.dumps(payload, ensure_ascii=False, indent=2)
        if args.json
        else "\n".join(f'{x["status"]}: {x["input_title"]}' for x in results)
    )
    return 0 if all(r["status"] == "identified_and_recovered" for r in results) else 2


if __name__ == "__main__":
    sys.exit(main())
