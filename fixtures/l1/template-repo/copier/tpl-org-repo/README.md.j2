# tpl-org-repo

L2 template for organization/company handbook repositories.

## Purpose

Generate organization repositories with:
- Organization documentation (`docs/org/`)
- Governance (`governance/`)
- Optional AK task-scope snapshots (`governance/task-scopes/`)
- Registers (`docs/registers/`)
- Decision records (`docs/decisions/`)
- Learnings capture (`docs/learnings/`)
- CI baseline (`scripts/ci/`)

## Usage

From an L1 templates repository:

```bash
./scripts/new-repo-from-copier.sh tpl-org-repo /path/to/<org>-handbook \
  -d repo_slug=<org>-handbook \
  -d org_owner_handle=@<owner> \
  --defaults --overwrite
```

## Structure

```
<org>-handbook/
├── AGENTS.md              # Organization-specific instructions
├── docs/
│   ├── _core/             # Vendored governance (immutable)
│   ├── org/               # Organization definition
│   │   ├── vision.md
│   │   ├── mission.md
│   │   ├── purpose.md
│   │   ├── model.md
│   │   ├── core_values.md
│   │   ├── culture.md
│   │   ├── ethics.md
│   │   ├── leitbild.md
│   │   └── strategic_objectives.md
│   ├── registers/         # Organizational registers
│   │   ├── risks.md
│   │   ├── debt.md
│   │   ├── assumptions.md
│   │   └── exceptions.md
│   ├── decisions/         # ADR-style decision records
│   ├── learnings/         # Captured learnings (TIP candidates)
│   └── system4d/          # System 4D context
├── diary/                 # Repo-local session capture (KES raw input)
├── governance/            # Governance documentation + optional AK task-scope snapshots
│   ├── README.md          # AK task-scope snapshot guidance
│   ├── task-scopes/       # Optional frozen AK task-scope snapshots
│   ├── consent.md
│   └── approvals.md
└── scripts/ci/            # CI scripts
```

## Customization

- `repo_slug`: Organization identifier
- `org_owner_handle`: CODEOWNERS entry for org paths
- `core_owner_handle`: CODEOWNERS entry for core paths
- `enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`:
  inherited compatibility flags from the parent L1 profile; currently metadata-only in `tpl-org-repo` (no extra file overlays)

## Consent Model

Org repos are typically consent-gated:
- Changes require proposals (issue templates)
- MRs use consent templates
- No direct pushes to main

## Optional explicit task-scope snapshots

When a repo-local AK task carries explicit scope, author/update that scope in AK and keep repo copies as frozen exports only:

```bash
ak task scope show <TASK-ID>
mkdir -p governance/task-scopes && ak task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json
```

Treat `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as repo-consumption artifacts for operators/agents/CI, not as hand-authored authority. When snapshots are checked in, `./scripts/check-task-scope-snapshots.sh` and `./scripts/ci/full.sh` verify repo ownership + drift against live AK state.
If you are retiring a legacy `governance/task-scopes/AK-*.json` file, export the snapshot first, keep the legacy file only as temporary compatibility fallback, and remove it from the primary workflow once the snapshot checks pass. If the task stays on repo-default scope, do not invent either file.

## Validation

```bash
./scripts/check-task-scope-snapshots.sh # verify checked-in AK task-scope snapshots when present
./scripts/ci/full.sh                    # smoke + optional task-scope + ROCS checks
```

## ROCS command flow

Use deterministic wrapper commands before ad-hoc scripts:

```bash
./scripts/rocs.sh --doctor
./scripts/rocs.sh --which
```

If this repo includes ontology artifacts, run validation through the same wrapper.

## Knowledge Evolution

Organizations capture raw sessions in `diary/` and crystallize durable patterns in `docs/learnings/`. Learnings that apply across organizations should be proposed as meta-TIPs to L0.

See parent L1 `tips/` directory for TIP templates and process.
