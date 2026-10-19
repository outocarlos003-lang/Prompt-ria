# Promptária operational audit

The operational audit is a conservative, static inventory. It compares physical Markdown instruments with the canonical registry, the test manifest, and the execution map; inspects the specialized-handler declaration without executing repository code; and records evidence gaps per instrument.

Run it from the repository root:

```bash
python scripts/promptaria_operational_audit.py --output artifacts/promptaria-operational-audit.json
```

## Catalog integrity

The report's `catalog_integrity` section detects duplicate IDs, path collisions, missing membership across the three catalogs, and conflicting titles or paths. Each finding identifies its source and affected instrument IDs. A conflicted identity is not treated as source-consistent for automation classification. If a catalog's `instruments` collection is not a list (including `null`), the audit reports `invalid_catalog_collection` and avoids iterating that malformed collection. The resulting inventory is diagnostic only: do not interpret missing inventory entries from a malformed catalog as evidence that no instruments exist.

The audit deliberately does not infer that an instrument is fully automated merely because it has documentation, a handler name, or a test reference. Full automation requires an explicit `functional_execution_verified` contract and matching source, handler, test, registry, manifest, and workflow evidence. An instrument with a handler but without all required proof remains partially automated; otherwise it is classified as having no proven executor.

## Regression tests

From the repository root, run the full regression suite:

```bash
python -m unittest discover -s tests -v
```

For the focused catalog-integrity tests, use:

```bash
python -m unittest discover -s tests -p 'test_promptaria_operational_audit_integrity.py' -v
```

The malformed-collection regression covers the registry, test manifest, and execution map independently. This ensures a bad collection is reported at its actual source rather than silently normalized into an empty list.

A successful local run is useful feedback, but the pull request must still pass the GitHub Actions checks for its current head commit. Functional changes under `scripts/`, `instruments/`, `config/`, or `.github/workflows/` must include an accompanying change to `README.md` or a Markdown file under `docs/` in the same pull request; the README-sync workflow enforces this editorial traceability rule.

## Limits and safety

- Static evidence does not prove that an instrument ran successfully or that external side effects occurred.
- Generating the report does not execute instrument text, enable an instrument, grant credentials, or authorize side effects.
- Titles and contextual similarity are not authorization. Ambiguous identity must be resolved using a stable explicit instrument ID.
- External integrations, credentials, runtime configuration, repository permissions, and branch protections require separate checks.
- Treat the report as a diagnostic snapshot, not as a substitute for CI, execution logs, or human review.

When a catalog conflict is found, fix the canonical source and its dependent manifest/map entries, then rerun the audit and regression suite. Do not resolve a conflict by silently choosing whichever duplicate happens to be indexed last.
