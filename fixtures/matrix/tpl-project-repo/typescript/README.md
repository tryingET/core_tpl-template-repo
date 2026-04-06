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
- Repo-local work-items projection (`governance/work-items.json`)
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

Explicit stack contract surface:
- `policy/stack-lane.json`
- `docs/tech-stack.local.md`
- `policy/stack-lane.json` -> `tech_stack_core.command` retrieves the upstream lane

## Usage

From an L1 templates repository:

```bash
./scripts/new-repo-from-copier.sh tpl-project-repo /path/to/<project> \
  -d repo_slug=<project> \
  -d project_owner_handle=@<owner> \
  --defaults --overwrite
```

## Agent Kernel work-items flow

Repo-local deferred work is **AK-first**.
`governance/work-items.json` is a deterministic checked-in projection/mirror for review and interoperability, not the live operational authority.

Use the repo-local wrapper so AK resolution stays explicit and reproducible:

```bash
./scripts/ak.sh --doctor
./scripts/ak.sh --which
```

By default the wrapper trusts `AK_BIN`, vendored `ak-cli`, or the workspace-core Agent Kernel. If you intentionally want to use an ambient `ak` from `PATH`, opt in with `AK_ALLOW_PATH_FALLBACK=1`.

Legacy JSON-first bootstrap (one-time migration into AK):

```bash
./scripts/ak.sh work-items import --repo . --path governance/work-items.json
```

Refresh the checked-in projection after AK state changes:

```bash
./scripts/ak.sh work-items export --repo . --path governance/work-items.json
```

Fail on projection drift locally/CI:

```bash
./scripts/ak.sh work-items check --repo . --path governance/work-items.json
```

## Optional explicit task-scope snapshots

When a repo-local AK task carries explicit scope, author/update that scope in AK and keep repo copies as frozen exports only:

```bash
./scripts/ak.sh task scope show <TASK-ID>
mkdir -p governance/task-scopes && ./scripts/ak.sh task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json
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

`./scripts/ak.sh` derives stable `--owner` / `--project-name` defaults from `.copier-answers.yml`, so projection behavior stays reproducible even if the checkout directory name differs from `repo_slug`.

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
│   │   ├── strategic_goals.md
│   │   └── tactical_goals.md
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
- `kernel_ontology_ref`: ROCS core ontology reference (default: `<repo:core/ontology-kernel@main>`)
- `company_ontology_ref`: ROCS company ontology reference (default: `<repo:holdingco/ontology@main>`)
- `enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`:
  inherited compatibility flags from the parent L1 profile; currently metadata-only in `tpl-project-repo` (no extra file overlays)

## ROCS command flow

Use the repository wrapper for deterministic execution. Default layered manifests resolve refs from local workspace clones only, so set the workspace root before running ref-aware commands:

```bash
export ROCS_WORKSPACE_ROOT="${ROCS_WORKSPACE_ROOT:-$HOME/ai-society}"
./scripts/rocs.sh --doctor
./scripts/rocs.sh build --repo . --resolve-refs --clean
./scripts/rocs.sh validate --repo . --resolve-refs
```

Default locator contract:
- core layer: `<repo:core/ontology-kernel@main>`
- company layer: `<repo:holdingco/ontology@main>`
- legacy `<gitlab:...>` locators are unsupported

If your workspace root lives somewhere else, point `ROCS_WORKSPACE_ROOT` at that clone root explicitly.
This wrapper prefers vendored `tools/rocs-cli` and falls back to workspace/global runners.

## Knowledge Evolution

Projects capture raw sessions in `diary/` and crystallize durable patterns in `docs/learnings/`. Learnings that apply beyond this project should be proposed as TIPs to the parent L1 templates.

See parent L1 `tips/` directory for TIP templates and process.
