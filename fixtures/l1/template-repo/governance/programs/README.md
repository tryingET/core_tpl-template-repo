# Company-Level Programs

This folder contains programs specific to this company's template setup and compliance.

## Ontology Hierarchy

```
L0 (governance-kernel)     → Cross-company programs (FCOS, Forge-Agnostic)
L1 (company-templates)     → Company-level programs (template-setup, compliance)
L2 (project repos)         → Project work (features, bugs)
```

## Structure

```
governance/
├── README.md              # This file
├── tip-process.md         # TIP review process (if separate)
└── programs/
    └── template-setup/
        └── work-items.json
```

## Example Programs

| Program | Scope | Description |
|---------|-------|-------------|
| template-setup | This company | Individualize L2 templates, bootstrap repos |
| compliance-baseline | This company | Company-specific compliance requirements |

## State Machine

Same as L0:

```
triage → queued → doing → review → done
```

## Adding a New Program

1. Create folder: `programs/<program-id>/`
2. Add `work-items.json` with milestones
3. Follow same schema as L0 programs

## Related

- L0 Programs: `governance-kernel/governance/programs/`
- L2 Work Items: `repo/governance/work-items.json`
- State Machine: `governance-kernel/governance/fcos/state-machine.yaml`
