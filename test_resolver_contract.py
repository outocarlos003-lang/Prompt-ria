"""Cross-language contract tests for canonical title identity.

Python currently resolves identities; JavaScript additionally classifies local
functional exceptions. These tests compare identity sets without pretending
that the two modules have identical execution semantics.
"""
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "promptaria_resolver",
    ROOT / "scripts" / "promptaria_resolver.py",
)
PY_RESOLVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PY_RESOLVER)
JS_MODULE = ROOT / ".github" / "scripts" / "resolver-correferencia.mjs"

INSTRUMENTS = [
    {"id": "alpha", "title": "INSTRUMENTO ÁLFA", "path": "instruments/alfa.md", "aliases": ["alfa"]},
    {"id": "beta", "title": "Instrumento Beta", "path": "instruments/beta.md", "aliases": ["beta"]},
    {"id": "gamma", "title": "Instrumento Gama", "path": "instruments/gama.md", "aliases": ["gama"]},
]


def resolve_javascript(request):
    script = """
      import { readFileSync } from 'node:fs';
      const { resolveMentions } = await import(process.env.PROMPTARIA_JS_MODULE);
      const input = JSON.parse(readFileSync(0, 'utf8'));
      const matches = resolveMentions(input.request, input.instruments);
      process.stdout.write(JSON.stringify(matches));
    """
    import os
    env = dict(os.environ, PROMPTARIA_JS_MODULE=JS_MODULE.as_uri())
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        input=json.dumps({"request": request, "instruments": INSTRUMENTS}, ensure_ascii=False),
        capture_output=True, text=True, encoding="utf-8", env=env, check=False,
    )
    if completed.returncode:
        raise AssertionError(completed.stderr)
    return json.loads(completed.stdout)


class CrossResolverContractTests(unittest.TestCase):
    def compare_identity_sets(self, request):
        python_catalog = [
            {**item, "normalized_title": PY_RESOLVER.normalize(item["title"])}
            for item in INSTRUMENTS
        ]
        python_ids = {
            next(item["id"] for item in INSTRUMENTS if item["title"] == match["title"])
            for match in PY_RESOLVER.resolve(request, python_catalog)
        }
        javascript_ids = {match["instrument_id"] for match in resolve_javascript(request)}
        self.assertEqual(python_ids, javascript_ids)

    def test_unicode_punctuation_and_multiple_titles_have_same_identity_set(self):
        self.compare_identity_sets(
            "Aplicar: instrumento álfa, INSTRUMENTO BETA e Instrumento Gama!"
        )

    def test_repeated_mentions_do_not_change_the_identity_set(self):
        self.compare_identity_sets(
            "Instrumento Beta; novamente Instrumento Beta; e Instrumento Gama."
        )

    def test_unique_aliases_resolve_consistently_in_both_resolvers(self):
        self.compare_identity_sets("Aplicar alfa e beta.")
        self.assertEqual(
            {match["instrument_id"] for match in resolve_javascript("Aplicar alfa e beta.")},
            {"alpha", "beta"},
        )


if __name__ == "__main__":
    unittest.main()
