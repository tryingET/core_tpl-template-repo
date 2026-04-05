# Governance README

This directory holds consent/approval docs and optional AK task-scope snapshots when a repo-local slice needs explicit scope.

## Managed launcher-bundle adoption snapshot

Generated org repos that ship `scripts/ak.sh` + `scripts/cargo-operator.sh` also carry:

- `governance/dist/managed-launcher-bundle.adoption-snapshot.json`

Treat that file as a **consumer-side snapshot contract** for the managed launcher bundle:
- the owner repo remains `softwareco/owned/agent-kernel`
- the template propagation source remains `core/tpl-template-repo`
- downstream repos stay consumer-only unless an explicit waiver says otherwise
- copied wrappers alone do not make the org repo the durable owner of the launcher bundle

The snapshot is a deterministic checked-in contract surface, not a hand-authored claim that downstream rollout is globally complete.

## Optional explicit task-scope snapshots

- author/update the scope in AK via `./scripts/ak.sh task scope show|set|update ...`
- keep repo-side copies under `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as frozen exports
- refresh a checked-in snapshot with `mkdir -p governance/task-scopes && ./scripts/ak.sh task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json`
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
- Keep consent/approval docs reviewable in git, but keep explicit task scope authored in AK and exported back here only as frozen snapshots.
