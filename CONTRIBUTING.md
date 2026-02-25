# Contributing

This repository is the **L0 source template** for AI Society (`L0 -> L1 -> L2`).

## Workflow

1. Create a feature branch.
2. Keep changes scoped and contract-safe.
3. Run full checks:
   ```bash
   bash ./scripts/check-l0.sh
   ```
4. Prefer deterministic wrappers over ad-hoc scripting:
   ```bash
   ./scripts/rocs.sh --doctor
   ./scripts/rocs.sh --which
   ```
5. Capture session notes in `./diary/` (repo-local KES rule), then crystallize durable patterns into `docs/learnings/` and `tips/meta/`.
6. Update docs when behavior changes.
7. Open a PR with validation output.

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

## Profile toggles note

This L0 now exposes optional profile toggles:
- `enable_community_pack` (issue templates / PR template / CoC / support docs)
- `enable_release_pack` (release-please / release-check / publish + release docs/scripts)
- `enable_vouch_gate` (vouch trust-gate workflows + `.github/VOUCHED.td`)

Defaults stay `false`; enable per repository governance/risk profile.
Policy references:
- `docs/profile-governance-policy.md`
- `docs/vouch-td-primer.md`
- `docs/feature-matrix-l0-l1-l2-vs-pi-template.md`
