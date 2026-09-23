---
summary: "README for generated project repositories."
read_when:
  - "Read when changing generated tpl-project-repo overview guidance."
type: "reference"
---

# fixture-project-typescript

Holding Company project repository.

## Context

- **Location**: owned
- **Language**: typescript
- **Software Pack**: Enabled (see language-specific files below)

## Purpose

Project repository with:
- Project documentation (`docs/project/`)
- Organization context (`docs/org_context/`)
  - `org_docs_profile=compact`: `README.md` + `org-summary.md`
  - `org_docs_profile=rich`: adds mission/purpose/vision/strategic objectives/governance context files
- Decision records (`docs/decisions/`)
- Learnings capture (`docs/learnings/`)
- Ontology support (`ontology/`)
- ROCS tooling (`tools/rocs-cli/`)
- CI baseline (`scripts/ci/`)

## Software Pack

TypeScript project scaffolded with:
- `package.json` — project configuration
- `tsconfig.json` — TypeScript configuration

```bash
npm install          # Install dependencies
npm test             # Run tests
```

Explicit engineering contract surface:
- `policy/engineering-lane.json`
- `docs/engineering.local.md`
- `policy/engineering-lane.json` -> `engineering_core.command` retrieves the upstream lane

## Usage

From an L1 templates repository:

```bash
./scripts/new-repo-from-copier.sh tpl-project-repo /path/to/<project> \
  -d repo_slug=<project> \
  -d project_owner_handle=@<owner> \
  --defaults --overwrite
```

## Agent Kernel work flow

Repo-local deferred work is **AK-native**: the Agent Kernel DB is the sole work authority.

Use plain installed `ak` as the canonical operator path:

```bash
ak task create -r "$PWD" "<title>"
ak task ready
ak task complete <TASK-ID> --result '<json>'
```

No checked-in work-items projection exists in this repo; do not reintroduce one.

## Optional explicit task-scope snapshots

When a repo-local AK task carries explicit scope, author/update that scope in AK and keep repo copies as frozen exports only:

```bash
ak task scope show <TASK-ID>
mkdir -p governance/task-scopes && ak task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json
```

Treat `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as repo-consumption artifacts for operators/agents/CI, not as hand-authored authority. When snapshots are checked in, `./scripts/check-task-scope-snapshots.sh` and `./scripts/ci/full.sh` verify repo ownership + drift against live AK state.
If you are retiring a legacy `governance/task-scopes/AK-*.json` file, export the snapshot first, keep the legacy file only as temporary compatibility fallback, and remove it from the primary workflow once the snapshot checks pass. If the task stays on repo-default scope, do not invent either file.

## Validation

Use the staged CI lanes:

```bash
./scripts/ci/fast.sh                    # cheap local guardrail lane
./scripts/check-task-scope-snapshots.sh # verify checked-in AK task-scope snapshots when present
./scripts/ci/full.sh                    # explicit full lane; runs fast first, then work-items + task-scope + ROCS checks in parallel when they apply
```

Plain installed `ak` is the canonical operator path for repo-local projection and task-scope flows.

## Structure

```
<project>/
├── AGENTS.md              # Project-specific instructions
├── next_session_prompt.md # Active handoff for the next session
├── docs/
│   ├── _core/             # Vendored governance (immutable)
│   ├── org_context/       # Organization context summary (+ optional rich org-context pack)
│   ├── project/           # Project definition
│   │   ├── vision.md
│   │   ├── mission.md
│   │   ├── purpose.md
│   │   ├── model.md
│   │   └── product_posture.md
│   ├── decisions/         # ADR-style decision records
│   ├── learnings/         # Captured learnings (TIP candidates)
│   └── system4d/          # System 4D context
├── governance/
│   ├── README.md          # AK-first workflow and projection rules
│   ├── task-scopes/       # Optional frozen AK task-scope snapshots
│   ├── work-items.cue     # Projection schema contract
│   └── work-items.json    # Checked-in AK projection/mirror
├── diary/                 # Repo-local session capture (KES raw input)
├── ontology/              # ROCS ontology
│   └── src/system4d.yaml
├── tools/rocs-cli/        # ROCS validation tooling
├── src/                   # Source code
├── tests/                 # Test suite
└── scripts/
    ├── ak.sh             # Deterministic AK launcher
    └── ci/               # CI scripts
```

## Customization

- `repo_slug`: Project identifier
- `project_owner_handle`: CODEOWNERS entry for project paths
  - if not passed explicitly, generation tries `PROJECT_OWNER_HANDLE`, `PI_PROJECT_OWNER_HANDLE`, `GITHUB_ACTOR`, then local git config
- `org_owner_handle`: CODEOWNERS entry for org paths
- `org_docs_profile`: `compact` keeps a short org-context snapshot; `rich` adds mission/purpose/vision/strategic-objectives/governance context files
- `kernel_ontology_ref`: ROCS core ontology reference (default: `<repo:core/ontology-kernel@v0.2.1>`)
- `company_ontology_ref`: ROCS company ontology reference (default: `<repo:holdingco/ontology@main>`)
- `enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`:
  inherited compatibility flags from the parent L1 profile; currently metadata-only in `tpl-project-repo` (no extra file overlays)

## ROCS command flow

Use the repository wrapper for deterministic execution. Layered manifests resolve refs from local workspace clones only; the launcher discovers the enclosing workspace automatically, so plain commands check every layer:

```bash
./scripts/rocs.sh --doctor
./scripts/rocs.sh cleanup --repo .
./scripts/rocs.sh validate --repo .
./scripts/rocs.sh build --repo .
```

Default locator contract:
- core layer: `<repo:core/ontology-kernel@v0.2.1>`
- company layer: `<repo:holdingco/ontology@main>`
- legacy `<gitlab:...>` locators are unsupported

If the repo is not checked out inside the workspace that holds those layers, point `ROCS_WORKSPACE_ROOT` at that clone root explicitly.
`scripts/rocs.sh` runs the workspace rocs-cli core checkout (`~/ai-society/core/rocs-cli`, override `ROCS_CORE_PROJECT`)
through `uv run --frozen`, pinned by the `rocs_cli_version` answer (`0.4.3`): the core must report the same
major.minor with a patch >= the pin, otherwise the launcher exits 2 naming both versions. There is no vendored or PATH fallback.
ROCS therefore needs the local workspace: the rocs-cli core plus the ontology repos named by `<repo:...@ref>` layers
(for example `core/ontology-kernel` and `holdingco/ontology`). The launcher defaults `ROCS_WORKSPACE_ROOT` to the
nearest ancestor that holds them (else `~/ai-society`) and sets `ROCS_RESOLVE_REFS=1`. CI runners must provide that
workspace (AK #5901) before running the ROCS step of `scripts/ci/full.sh`.
Generated outputs under `ontology/dist/` (including authority receipts) are gitignored; `./scripts/rocs.sh cleanup --repo .` removes them.

## Knowledge Evolution

Projects capture raw sessions in `diary/` and crystallize durable patterns in `docs/learnings/`. Learnings that apply beyond this project should be proposed as TIPs to the parent L1 templates.

See parent L1 `tips/` directory for TIP templates and process.
