# Contributing

This repository is the **L0 source template** for AI Society (`L0 -> L1 -> L2`).

## Workflow

1. Create a feature branch.
2. Keep changes scoped and contract-safe.
3. Run full checks:
   ```bash
   bash ./scripts/check-l0.sh
   ```
4. Update docs when behavior changes.
5. Open a PR with validation output.

## Required guardrails

- Do not introduce nested Copier runs inside template `_tasks`.
- Preserve recursion bounds (`L0 -> L1 -> L2`, no reverse/cycle).
- Keep `.copier-answers.yml` committed in generated repos.
- Keep baseline folder skeleton aligned where intended (`docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`) and document any intentional divergence.
- Keep fixtures in sync when template outputs change:
  ```bash
  bash ./scripts/sync-l0-fixtures.sh
  bash ./scripts/check-l0-fixtures.sh
  ```

## Trust-gate note

Vouch trust-gate (`.td`) baseline is not yet enabled in this L0 slice.
When introduced, policy lives in:
- `docs/vouch-td-primer.md`
- `docs/feature-matrix-l0-l1-l2-vs-pi-template.md`
