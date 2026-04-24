# Project Work Items

`governance/work-items.json` is the checked-in deterministic projection/mirror for this repository's Agent Kernel work-items state.

## Authority model

| Surface | Role | Authority |
|---|---|---|
| Agent Kernel work-items state | Live operational backlog for this repo | **Authoritative** |
| `governance/work-items.json` | Checked-in projection for review, diffs, and compatibility | Mirror only |
| `governance/work-items.cue` | Projection shape validation | Contract for the mirror |

Do not treat manual JSON edits as the live source of truth.
If you are migrating a legacy JSON-first repo, import once, then continue from AK and re-export the projection.

## Fresh-repo baseline

This template ships the empty projection that matches a fresh AK export for this repo identity.
That keeps `./scripts/ci/full.sh` honest: if `ak` is available, CI can validate drift immediately instead of silently skipping the check.
Use `./scripts/ci/fast.sh` for the cheap local baseline and `./scripts/ci/full.sh` for the explicit full lane.

## Workflow

Use plain installed `ak` as the canonical operator path:

```bash
ak work-items import --repo . --path governance/work-items.json
ak work-items export --repo . --path governance/work-items.json
ak work-items check --repo . --path governance/work-items.json
```

Plain installed `ak` is the canonical operator path for repo-local projection and task-scope flows.

## Optional explicit task-scope snapshots

When a repo-local AK task needs explicit scope:

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

## Projection contract

Core fields:
- `schema_version`
- `updated_at`
- `owner`
- `project_name`
- `milestones[]`

Issue state machine:
- `triage -> queued -> doing -> review -> done`

Optional schema-only validation:

```bash
cue vet governance/work-items.json governance/work-items.cue
```

## Use this vs alternatives

| Use this projection when | Use alternative when |
|---|---|
| You need a reviewable, checked-in mirror of repo-local AK state | Work spans multiple repos/programs (use FCOS/L0 program models) |
| You are migrating legacy repo-local JSON work-items into AK | You only need lightweight conversational triage (use notes/issues) |

## Non-negotiable

- Do not leave deferred work as ad-hoc TODO comments or scattered markdown notes.
- Do not repair operational drift by hand-editing `governance/work-items.json` and pretending the JSON is authoritative.
- Do not hand-author `governance/task-scopes/AK-*.snapshot.json` as if it were the live task-scope source of truth.
- For legacy/manual JSON slices, import to AK and then export the projection back out.
