---
summary: "Governance guidance for generated tpl-monorepo governance directories."
read_when:
  - "Read when changing or validating generated tpl-monorepo governance guidance."
type: "reference"
---

# Governance

Deferred and active work for this monorepo lives in the **Agent Kernel DB** (`ak task ...`).
The AK DB is the sole work authority; no checked-in work-items projection exists or should be reintroduced.

## Optional explicit task-scope snapshots

When a monorepo AK task needs explicit scope:

- author/update the scope in AK via `ak task scope show|set|update ...`
- keep repo-side copies under `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as frozen exports
- refresh a checked-in snapshot with `mkdir -p governance/task-scopes && ak task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json`
- verify checked-in snapshots with `./scripts/check-task-scope-snapshots.sh` before commit or in CI
- keep package/app consumers pointed at the monorepo-root snapshot instead of inventing per-member task-scope files

## Brownfield migration boundary

If this monorepo is retiring hand-authored `governance/task-scopes/AK-*.json` files:

- author/update the scope in AK first, then export `AK-<TASK-ID>.snapshot.json`
- keep the legacy `AK-*.json` file only as temporary compatibility fallback while local/CI still depends on it
- remove legacy manifest authoring from workflow docs and handoffs as soon as `./scripts/check-task-scope-snapshots.sh` passes
- if the task still uses repo-default scope, do not invent a snapshot or a replacement legacy manifest

If this monorepo still carries a legacy `governance/work-items.json` from an older template
generation, retire it: import any unmigrated items once via the compatibility
`ak work-items import`, continue from `ak task ...`, and delete the projection file.

## Non-negotiable

- Do not leave deferred work as ad-hoc TODO comments or scattered markdown notes.
- Do not reintroduce a checked-in `governance/work-items.json` projection; the AK DB is authoritative.
- Do not hand-author `governance/task-scopes/AK-*.snapshot.json` as if it were the live task-scope source of truth.
