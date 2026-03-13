# Governance

Template governance layer for this company.

## Purpose

This folder contains company-level planning artifacts plus validation contracts.
Repo-local work-items in generated L2 project/monorepo repos are **AK-first** and only projected back into git.

| Folder | Purpose | Operational? |
|--------|---------|--------------|
| `programs/` | Company-level work tracking | Planning only |
| `model-languages/` | Schema validation | Yes (CUE) |

## Three-Level Hierarchy

| Level | Scope | Location | Authority |
|-------|-------|----------|-----------|
| **L0** | Cross-company | governance-kernel/governance/programs/ | Yes (scheduler / FCOS) |
| **L1** | Company | this repo: governance/programs/ | Planning only |
| **L2** | Project / monorepo | repo/governance/work-items.json | Agent Kernel authoritative; JSON is the checked-in projection |

## Company-Level Programs

Programs are tracked in `programs/`:

```
programs/
└── template-setup/
    ├── work-items.json    # Milestones and issues
    └── README.md
```

### What Goes Here

- Template individualization for this company
- Repo bootstrapping (tpl-owned, tpl-contrib, tpl-infra)
- Company-specific compliance baseline

### What Does NOT Go Here

- Cross-company work → L0 (governance-kernel)
- Single-repo features → L2 repo-local AK work-items

## L2 repo-local work-items (AK-first)

Generated `tpl-project-repo` and `tpl-monorepo` repos treat repo-local work-items this way:

- live operational authority stays in Agent Kernel
- `governance/work-items.json` is a deterministic checked-in projection/mirror
- `./scripts/ak.sh work-items import` is the legacy JSON bootstrap path
- `./scripts/ak.sh work-items export` refreshes the checked-in projection
- `./scripts/ak.sh work-items check` is the drift gate used by repo CI

## Validation

Validate company-level program work-items against schema:

```bash
cue vet governance/programs/*/work-items.json governance/model-languages/contract/work-items.cue
```

## TIP Review Process

See `governance/README.md` for TIP escalation paths.

## State Machine

All levels use the same 5-state machine:

```
triage → queued → doing → review → done
```

Defined in: `governance-kernel/governance/fcos/state-machine.yaml`

## Related

- L0 Programs: `governance-kernel/governance/programs/`
- State Machine: `governance-kernel/governance/fcos/state-machine.yaml`
- Org Handbook: `holdingco/org-handbook/docs/org/governance/structure.md`
