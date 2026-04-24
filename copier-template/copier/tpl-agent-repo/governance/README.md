# Governance README

Agent repos stay lightweight, but if a repo-local AK task needs explicit scope, keep repo copies under `governance/task-scopes/` as frozen exports only.

## Optional explicit task-scope snapshots

- author/update the scope in AK via `ak task scope show|set|update ...`
- keep repo-side copies under `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as frozen exports
- refresh a checked-in snapshot with `mkdir -p governance/task-scopes && ak task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json`
- verify checked-in snapshots with `./scripts/check-task-scope-snapshots.sh` before commit or in CI
- treat any hand-authored `governance/task-scopes/AK-*.json` file that is not an AK export as transitional scaffolding, not authoritative truth

## Brownfield migration boundary

If this repo is retiring hand-authored `governance/task-scopes/AK-*.json` files:

- author/update the scope in AK first, then export `AK-<TASK-ID>.snapshot.json`
- keep the legacy `AK-*.json` file only as temporary compatibility fallback while local/CI still depend on it
- remove legacy manifest authoring from workflow docs and handoffs as soon as `./scripts/check-task-scope-snapshots.sh` passes
- if the task still uses repo-default scope, do not invent a snapshot or a replacement legacy manifest

## Non-negotiable

- Do not hand-author `governance/task-scopes/AK-*.snapshot.json` as if it were the live task-scope source of truth.
- Keep persona/policy docs in `docs/` and `policy/`; use `governance/task-scopes/` only for frozen AK exports when explicit scope is part of the slice.
