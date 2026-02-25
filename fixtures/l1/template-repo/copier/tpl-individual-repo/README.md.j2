# tpl-individual-repo

L2 template for individual execution repositories.

## Purpose

Generate individual repositories with a shared baseline capability pack:
- Project/mission documentation (`docs/project/`)
- Organization context (`docs/org_context/`)
- Decision records (`docs/decisions/`)
- Learnings capture (`docs/learnings/`)
- Ontology support (`ontology/`)
- ROCS tooling (`tools/rocs-cli/`)
- CI baseline (`scripts/ci/`)

This template intentionally mirrors `tpl-project-repo` for baseline execution primitives
so company lanes can layer the same deterministic overlays.

## Usage

From an L1 templates repository:

```bash
./scripts/new-repo-from-copier.sh tpl-individual-repo /path/to/<individual-repo> \
  -d repo_slug=<individual-repo> \
  -d project_owner_handle=@<owner> \
  --defaults --overwrite
```

## Structure

```
<individual-repo>/
├── AGENTS.md              # Repository instructions
├── docs/
│   ├── _core/             # Vendored governance (immutable)
│   ├── org_context/       # Organization context summary
│   ├── project/           # Mission/model/goals
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

## Company lane overlay extension points

Use these paths for lane-specific overlays while preserving baseline behavior:
- `docs/org_context/**` — organization-specific context packs
- `policy/**` — lane guardrails and consent constraints
- `ontology/src/system4d.yaml` — lane ontology specialization
- `.gitlab/ci/rocs.yml`, `scripts/ci/**` — lane CI/gating extensions
- `CODEOWNERS` handles (`core_owner_handle`, `org_owner_handle`, `project_owner_handle`)

## Customization

- `repo_slug`: Repository identifier
- `project_owner_handle`: Primary owner handle for execution paths
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

Individual repos capture raw sessions in `diary/` and crystallize durable patterns in `docs/learnings/`. Learnings that generalize should be proposed as TIPs to the parent L1 templates.

See parent L1 `tips/` directory for TIP templates and process.
