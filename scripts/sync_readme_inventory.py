#!/usr/bin/env python3
"""Synchronize README's versioned inventory with the repository tree."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

SECTIONS = (
    ("Instrumentos operacionais", "instruments", "*.md", False),
    ("Scripts Python", "scripts", "*.py", False),
    ("Workflows do GitHub Actions", ".github/workflows", "*.yml", False),
    ("Documentação", "docs", "*.md", False),
    ("Testes", "tests", "*", True),
    ("Configurações JSON", "config", "*.json", False),
)


def inventory(root: Path, directory: str, pattern: str, recursive: bool) -> list[str]:
    base = root / directory
    if not base.is_dir():
        raise SystemExit(f"Diretório de inventário ausente: {directory}")
    paths = base.rglob(pattern) if recursive else base.glob(pattern)
    return sorted(
        path.relative_to(root).as_posix()
        for path in paths
        if path.is_file() and "__pycache__" not in path.parts and path.name.endswith((".py", ".mjs", ".json"))
        or path.is_file() and not recursive
    )


def replace_section(document: str, heading: str, next_heading: str, paths: list[str]) -> str:
    pattern = re.compile(
        rf"(?ms)^### {re.escape(heading)} \(\d+\)\n\n.*?(?=^### {re.escape(next_heading)} \(\d+\)|\Z)"
    )
    replacement = f"### {heading} ({len(paths)})\n\n" + "".join(f"- `{path}`\n" for path in paths) + "\n"
    updated, count = pattern.subn(replacement, document, count=1)
    if count != 1:
        raise SystemExit(f"Seção de inventário ausente ou ambígua no README: {heading}")
    return updated


def synchronize(root: Path) -> bool:
    readme = root / "README.md"
    original = readme.read_text(encoding="utf-8")
    updated = original
    for index, (heading, directory, pattern, recursive) in enumerate(SECTIONS):
        paths = inventory(root, directory, pattern, recursive)
        next_heading = SECTIONS[index + 1][0] if index + 1 < len(SECTIONS) else None
        if next_heading is None:
            section_pattern = re.compile(
                rf"(?ms)^### {re.escape(heading)} \(\d+\)\n\n.*?(?=^<!-- PROMPTARIA-README-AUTO:END -->|\Z)"
            )
            replacement = f"### {heading} ({len(paths)})\n\n" + "".join(f"- `{path}`\n" for path in paths) + "\n"
            updated, count = section_pattern.subn(replacement, updated, count=1)
            if count != 1:
                raise SystemExit(f"Seção de inventário ausente ou ambígua no README: {heading}")
        else:
            updated = replace_section(updated, heading, next_heading, paths)
    if updated == original:
        return False
    readme.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true", help="Fail instead of writing when inventory is stale.")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.check:
        before = (root / "README.md").read_text(encoding="utf-8")
        synchronize(root)
        after = (root / "README.md").read_text(encoding="utf-8")
        if before != after:
            (root / "README.md").write_text(before, encoding="utf-8")
            raise SystemExit("README.md contém inventário desatualizado; execute scripts/sync_readme_inventory.py.")
        print("README inventory is synchronized.")
        return 0
    changed = synchronize(root)
    print("README inventory synchronized." if changed else "README inventory already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
