---
summary: "README for generated monorepositories."
read_when:
  - "Read when changing generated tpl-monorepo overview guidance."
type: "reference"
---

# fixture-monorepo-matrix

Holding Company monorepo workspace.

## Structure

```
packages/        # Reusable libraries
apps/            # Deployable services/applications
docs/            # Documentation (_core, org_context, engineering.local)
ontology/        # ROCS ontology
governance/      # Optional task-scope snapshots, policies
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
ak task ready

# ROCS tooling
./scripts/rocs.sh --doctor
./scripts/rocs.sh version

# CI lanes
./scripts/ci/smoke.sh
./scripts/ci/full.sh

# Enable staged-file UBS pre-commit (new copies enable it automatically)
./scripts/install-hooks.sh
```

## Agent Kernel task flow

Repo-local deferred and active work is **AK-first**: it lives in the Agent Kernel DB via `ak task ...`.
No checked-in work-items projection exists in this repo; do not reintroduce one.

```bash
ak task create -r "$PWD" "<title>"
ak task ready
ak task complete <TASK-ID> --result '<json>'
```

Plain installed `ak` is the canonical operator path for repo-local task and task-scope flows.

## Optional explicit task-scope snapshots

If a monorepo AK task carries explicit scope, author/update that scope in AK and keep repo-side copies as frozen exports at the monorepo root:

```bash
ak task scope show <TASK-ID>
mkdir -p governance/task-scopes && ak task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json
```

Packages/apps consume the monorepo-root snapshot; they do not author standalone AK task-scope files. When snapshots are checked in, `./scripts/check-task-scope-snapshots.sh` and `./scripts/ci/full.sh` verify repo ownership + drift against live AK state.
If you are retiring a legacy monorepo-root `governance/task-scopes/AK-*.json` file, export the snapshot first, keep the legacy file only as temporary compatibility fallback, and remove it from the primary workflow once the snapshot checks pass. If the task stays on repo-default scope, do not invent either file.

## ROCS command flow

1. `./scripts/rocs.sh --doctor` — show core path/version, pin and workspace root
2. `./scripts/rocs.sh cleanup --repo .` — remove managed build outputs
3. `./scripts/rocs.sh validate --repo .` — validate all ontology layers (core, company, repo)
4. `./scripts/rocs.sh build --repo .` — build `ontology/dist/`

`scripts/rocs.sh` runs the workspace rocs-cli core checkout (`~/ai-society/core/rocs-cli`, override `ROCS_CORE_PROJECT`)
through `uv run --frozen`, pinned by the `rocs_cli_version` answer (`0.4.4`): the core must report the same
major.minor with a patch >= the pin, otherwise the launcher exits 2 naming both versions. There is no vendored or PATH fallback.
ROCS therefore needs the local workspace: the rocs-cli core plus the ontology repos named by `<repo:...@ref>` layers
(for example `core/ontology-kernel` and `holdingco/ontology`). The launcher defaults `ROCS_WORKSPACE_ROOT` to the
nearest ancestor that holds them (else `~/ai-society`) and sets `ROCS_RESOLVE_REFS=1`. CI runners must provide that
workspace (AK #5901) before running the ROCS step of `scripts/ci/full.sh`.
Generated outputs under `ontology/dist/` (including authority receipts) are gitignored; `./scripts/rocs.sh cleanup --repo .` removes them.

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

- Task-scope snapshots: `governance/task-scopes/AK-<TASK-ID>.snapshot.json` (when explicit task scope is in play)
- Policies: `policy/`
- Ontology: `ontology/`
- Repo-local org-context snapshot: `docs/org_context/`
- Repo-local engineering note: `docs/engineering.local.md`
- Package/app engineering contracts live inside generated members (for example `policy/engineering-lane.json` and `docs/engineering.local.md` from `tpl-package`)

## Diary

Capture sessions in `diary/YYYY-MM-DD--type-scope-summary.md`.

## Recursion Policy

- **Allowed**: L1 → L2 (this monorepo)
- **Forbidden**: L2 → L1, L1 → L0, any cycle
