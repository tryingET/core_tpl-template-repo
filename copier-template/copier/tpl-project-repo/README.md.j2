# tpl-project-repo

L2 template for delivery project repositories.

## Purpose

Generate project repositories with:
- Project documentation (`docs/project/`)
- Organization context (`docs/org_context/`)
- Decision records (`docs/decisions/`)
- Learnings capture (`docs/learnings/`)
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

## Structure

```
<project>/
├── AGENTS.md              # Project-specific instructions
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
│   ├── dev/               # Development notes
│   └── system4d/          # System 4D context
├── diary/                 # Repo-local session capture (KES raw input)
├── ontology/              # ROCS ontology
│   └── src/system4d.yaml
├── tools/rocs-cli/        # ROCS validation tooling
├── src/                   # Source code
├── tests/                 # Test suite
└── scripts/ci/            # CI scripts
```

## Customization

- `repo_slug`: Project identifier
- `project_owner_handle`: CODEOWNERS entry for project paths
- `org_owner_handle`: CODEOWNERS entry for org paths
- `kernel_ontology_ref`: ROCS core ontology reference
- `company_ontology_ref`: ROCS company ontology reference
- `enable_vouch_gate`: Enable trust gating
- `enable_community_pack`: Enable community collaboration
- `enable_release_pack`: Enable release automation

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
