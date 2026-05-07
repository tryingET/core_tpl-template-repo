---
summary: "README for generated monorepositories."
read_when:
  - "Read when changing generated tpl-monorepo overview guidance."
type: "reference"
---

# fixture-monorepo

Holding Company monorepo workspace.

## Structure

```
packages/        # Reusable libraries
apps/            # Deployable services/applications
docs/            # Documentation (_core, org_context, tech-stack.local)
ontology/        # ROCS ontology
governance/      # AK work-items projection, optional task-scope snapshots, policies
scripts/         # CI/utility scripts
```

## Package Manager

- **uv** — workspace package management
- Languages — defined per-package (see `packages/` and `apps/`)

## Org Context Profile

- `org_docs_profile=compact`: `docs/org_context/org-summary.md`
- `org_docs_profile=rich`: adds mission / purpose / vision / strategic objectives / governance context files

## Profile Compatibility Flags

- `enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`:
  inherited compatibility flags from the parent L1 profile; currently metadata-only in `tpl-monorepo` (no extra file overlays at the monorepo root)

## Quick Commands

```bash
# Agent Kernel tooling
ak work-items check --repo . --path governance/work-items.json
ak task ready

# ROCS tooling
./scripts/rocs.sh --doctor
./scripts/rocs.sh version

# CI lanes
./scripts/ci/smoke.sh
./scripts/ci/full.sh
```

## Agent Kernel work-items flow

Repo-local deferred work is **AK-first**.
`governance/work-items.json` is a deterministic checked-in projection/mirror, not the live operational authority.

```bash
# One-time legacy JSON bootstrap into AK
ak work-items import --repo . --path governance/work-items.json

# Refresh projection from AK after work-items change
ak work-items export --repo . --path governance/work-items.json

# CI/local drift gate
ak work-items check --repo . --path governance/work-items.json
```

Plain installed `ak` is the canonical operator path for repo-local projection and task-scope flows.

## Optional explicit task-scope snapshots

If a monorepo AK task carries explicit scope, author/update that scope in AK and keep repo-side copies as frozen exports at the monorepo root:

```bash
ak task scope show <TASK-ID>
mkdir -p governance/task-scopes && ak task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json
```

Packages/apps consume the monorepo-root snapshot; they do not author standalone AK task-scope files. When snapshots are checked in, `./scripts/check-task-scope-snapshots.sh` and `./scripts/ci/full.sh` verify repo ownership + drift against live AK state.
If you are retiring a legacy monorepo-root `governance/task-scopes/AK-*.json` file, export the snapshot first, keep the legacy file only as temporary compatibility fallback, and remove it from the primary workflow once the snapshot checks pass. If the task stays on repo-default scope, do not invent either file.

## ROCS command flow

1. `./scripts/rocs.sh --doctor` — verify ROCS environment
2. `./scripts/rocs.sh validate --repo .` — validate ontology
3. `./scripts/rocs.sh lint --repo .` — lint governance files

## Adding Packages

Use `tpl-package` from your L1 templates to add packages:

```bash
# From L1 templates repo
./scripts/new-repo-from-copier.sh tpl-package /path/to/monorepo/packages/<name> \
  -d package_name=<name> \
  -d package_type=library \
  -d language=<python|node|typescript|rust|go|elixir> \
  --defaults --overwrite
```

## Adding Apps

```bash
# From L1 templates repo
./scripts/new-repo-from-copier.sh tpl-package /path/to/monorepo/apps/<name> \
  -d package_name=<name> \
  -d package_type=app \
  -d language=<python|node|typescript|rust|go|elixir> \
  --defaults --overwrite
```

## Governance

- Work-items projection: `governance/work-items.json` (AK-backed; use plain installed `ak`)
- Task-scope snapshots: `governance/task-scopes/AK-<TASK-ID>.snapshot.json` (when explicit task scope is in play)
- Projection schema: `governance/work-items.cue`
- Policies: `policy/`
- Ontology: `ontology/`
- Repo-local org-context snapshot: `docs/org_context/`
- Repo-local stack note: `docs/tech-stack.local.md`
- Package/app stack contracts live inside generated members (for example `policy/stack-lane.json` and `docs/tech-stack.local.md` from `tpl-package`)

## Diary

Capture sessions in `diary/YYYY-MM-DD--type-scope-summary.md`.

## Recursion Policy

- **Allowed**: L1 → L2 (this monorepo)
- **Forbidden**: L2 → L1, L1 → L0, any cycle
