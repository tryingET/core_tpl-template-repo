# Governance

Template governance layer for this company.

## Purpose

This folder contains **planning artifacts** for company-level coordination:

| Folder | Purpose | Operational? |
|--------|---------|--------------|
| `programs/` | Company-level work tracking | Planning only |
| `model-languages/` | Schema validation | Yes (CUE) |

## Three-Level Hierarchy

| Level | Scope | Location | Operational? |
|-------|-------|----------|--------------|
| **L0** | Cross-company | governance-kernel/governance/programs/ | Yes (scheduler) |
| **L1** | Company | this repo: governance/programs/ | Planning only |
| **L2** | Project | repo/governance/work-items.json | Planning only |

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
- Single-repo features → L2 (project governance)

## Validation

Validate work-items against schema:

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
