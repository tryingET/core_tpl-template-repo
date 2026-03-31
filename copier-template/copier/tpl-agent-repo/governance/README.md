# Governance README

Agent repos stay lightweight, but if a repo-local AK task needs explicit scope, keep repo copies under `governance/task-scopes/` as frozen exports only.

## Optional explicit task-scope snapshots

- author/update the scope in AK via `./scripts/ak.sh task scope show|set|update ...`
- keep repo-side copies under `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as frozen exports
- refresh a checked-in snapshot with `mkdir -p governance/task-scopes && ./scripts/ak.sh task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json`
- verify checked-in snapshots with `./scripts/check-task-scope-snapshots.sh` before commit or in CI
- treat any hand-authored `governance/task-scopes/AK-*.json` file that is not an AK export as transitional scaffolding, not authoritative truth

## Non-negotiable

- Do not hand-author `governance/task-scopes/AK-*.snapshot.json` as if it were the live task-scope source of truth.
- Keep persona/policy docs in `docs/` and `policy/`; use `governance/task-scopes/` only for frozen AK exports when explicit scope is part of the slice.
