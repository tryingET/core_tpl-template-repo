# Monorepo Work Items

`governance/work-items.json` is the checked-in deterministic projection/mirror for this monorepo's Agent Kernel work-items state.

## Authority model

| Surface | Role | Authority |
|---|---|---|
| Agent Kernel work-items state | Live operational backlog for this monorepo | **Authoritative** |
| `governance/work-items.json` | Checked-in projection for review, diffs, and compatibility | Mirror only |
| `governance/work-items.cue` | Projection shape validation | Contract for the mirror |

Do not treat manual JSON edits as the live source of truth.
If you are migrating a legacy JSON-first monorepo, import once, then continue from AK and re-export the projection.

## Workflow

Diagnose AK resolution:

```bash
./scripts/ak.sh --doctor
./scripts/ak.sh --which
```

Ambient `ak` binaries on `PATH` are blocked by default; set `AK_ALLOW_PATH_FALLBACK=1` only when you explicitly want that fallback.

Bootstrap legacy JSON into AK:

```bash
./scripts/ak.sh work-items import --repo . --path governance/work-items.json
```

Refresh the checked-in projection from AK:

```bash
./scripts/ak.sh work-items export --repo . --path governance/work-items.json
```

Check that the committed projection matches AK (used by `./scripts/ci/full.sh`):

```bash
./scripts/ak.sh work-items check --repo . --path governance/work-items.json
```

## Managed launcher-bundle adoption snapshot

Generated monorepos that ship `scripts/ak.sh` + `scripts/cargo-operator.sh` also carry:

- `governance/dist/managed-launcher-bundle.adoption-snapshot.json`

Treat that file as a **consumer-side snapshot contract** for the managed launcher bundle:
- the owner repo remains `softwareco/owned/agent-kernel`
- the template propagation source remains `core/tpl-template-repo`
- downstream repos stay consumer-only unless an explicit waiver says otherwise
- copied wrappers alone do not make the monorepo the durable owner of the launcher bundle

The snapshot is a deterministic checked-in contract surface, not a hand-authored claim that downstream rollout is globally complete.

## Optional explicit task-scope snapshots

When a monorepo AK task needs explicit scope:

- author/update it in AK via `./scripts/ak.sh task scope show|set|update ...`
- keep repo-side copies under `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as frozen exports
- refresh a checked-in snapshot with `mkdir -p governance/task-scopes && ./scripts/ak.sh task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json`
- verify checked-in snapshots with `./scripts/check-task-scope-snapshots.sh` before commit or in CI
- keep package/app consumers pointed at the monorepo-root snapshot instead of inventing per-member task-scope files

## Brownfield migration boundary

If this monorepo is retiring hand-authored `governance/task-scopes/AK-*.json` files:

- author/update the scope in AK first, then export `AK-<TASK-ID>.snapshot.json`
- keep the legacy `AK-*.json` file only as temporary compatibility fallback while local/CI still depend on it
- remove legacy manifest authoring from workflow docs and handoffs as soon as `./scripts/check-task-scope-snapshots.sh` passes
- if the task still uses repo-default scope, do not invent a snapshot or a replacement legacy manifest

Optional schema-only validation:

```bash
cue vet governance/work-items.json governance/work-items.cue
```

## State machine

```
triage → queued → doing → review → done
```

## Program vs project/monorepo

| Type | Location | Scope | Authority |
|------|----------|-------|-----------|
| **Program** | governance-kernel/governance/programs/ | Cross-company | L0 scheduler / FCOS |
| **Program** | company-templates/governance/programs/ | Company | Planning only |
| **Monorepo** | repo/governance/work-items.json (this file) | This repo | AK authoritative; JSON is the projection |

## Non-negotiable

- Do not leave deferred work as ad-hoc TODO comments or scattered markdown notes.
- Do not repair operational drift by hand-editing `governance/work-items.json` and pretending the JSON is authoritative.
- Do not hand-author `governance/task-scopes/AK-*.snapshot.json` as if it were the live task-scope source of truth.
- For legacy/manual JSON slices, import to AK and then export the projection back out.
