# fixture-product-repo

Holding Company project repository.

## Context

- **Location**: owned
- **Language**: python

## Purpose

Project repository with:
- Project documentation (`docs/project/`)
- Organization context (`docs/org_context/`)
- Decision records (`docs/decisions/`)
- Learnings capture (`docs/learnings/`)
- Repo-local work-items projection (`governance/work-items.json`)
- Ontology support (`ontology/`)
- ROCS tooling (`tools/rocs-cli/`)
- CI baseline (`scripts/ci/`)

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

`./scripts/ak.sh` derives stable `--owner` / `--project-name` defaults from `.copier-answers.yml`, so projection behavior stays reproducible even if the checkout directory name differs from `repo_slug`.

## Structure

```
<project>/
├── AGENTS.md              # Project-specific instructions
├── next_session_prompt.md # Active handoff for the next session
├── docs/
│   ├── _core/             # Vendored governance (immutable)
│   ├── org_context/       # Organization context summary
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
- `kernel_ontology_ref`: ROCS core ontology reference
- `company_ontology_ref`: ROCS company ontology reference
- `enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`:
  inherited compatibility flags from the parent L1 profile; currently metadata-only in `tpl-project-repo` (no extra file overlays)

## ROCS command flow

Use the repository wrapper for deterministic execution:

```bash
./scripts/rocs.sh --doctor
./scripts/rocs.sh build --repo . --resolve-refs --clean
./scripts/rocs.sh validate --repo . --resolve-refs
```

This wrapper prefers vendored `tools/rocs-cli` and falls back to workspace/global runners.

## Knowledge Evolution

Projects capture raw sessions in `diary/` and crystallize durable patterns in `docs/learnings/`. Learnings that apply beyond this project should be proposed as TIPs to the parent L1 templates.

See parent L1 `tips/` directory for TIP templates and process.
