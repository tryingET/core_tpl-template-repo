---
summary: "Company-Level Programs."
read_when:
  - "Read when changing L1 template output related to company-level programs."
type: "reference"
---

# Company-Level Programs

This folder contains programs specific to this company's template setup and compliance.

## Purpose

**These are PLANNING ARTIFACTS, not execution queues.**

| Aspect | Status |
|--------|--------|
| Structure | ✓ Complete |
| Validation | ✓ CUE schema |
| Operational | ✗ No scheduler support |

The scheduler only operates on L0 (FCOS) work-items.
L1 programs are for:
- planning and tracking company-level work
- coordinating across L2 repos
- documenting decisions and progress

Repo-local L2 work-items are now AK-first: Agent Kernel is authoritative and `repo/governance/work-items.json` is only the checked-in projection.

## Structure

```
programs/
└── template-setup/
    ├── work-items.json    # Milestones and issues
    └── README.md          # Program-specific docs
```

## Example Programs

| Program | Scope | Description |
|---------|-------|-------------|
| template-setup | This company | Individualize L2 templates, bootstrap repos |
| compliance-baseline | This company | Company-specific compliance requirements |

## Validation

```bash
# Validate all L1 work-items
cue vet governance/programs/*/work-items.json governance/model-languages/contract/work-items.cue

# Validate specific program
cue vet governance/programs/template-setup/work-items.json governance/model-languages/contract/work-items.cue
```

## State Machine

```
triage → queued → doing → review → done
```

| State | Meaning |
|-------|---------|
| triage | Not yet shaped |
| queued | Ready to start |
| doing | In progress |
| review | Awaiting approval |
| done | Complete |

## Adding a New Program

1. Create folder: `programs/<program-id>/`
2. Add `work-items.json` with milestones
3. Validate: `cue vet programs/<program-id>/work-items.json model-languages/contract/work-items.cue`
4. Document in README

## Hierarchy Context

| Level | Scope | Authority |
|-------|-------|-----------|
| L0 | Cross-company | Yes (scheduler / FCOS) |
| **L1** | **Company (this folder)** | **Planning only** |
| L2 | Project / monorepo | AK authoritative; JSON projection only |

## Related

- L0 Programs: `governance-kernel/governance/programs/`
- L2 Work Items Projection: `repo/governance/work-items.json`
- State Machine: `governance-kernel/governance/fcos/state-machine.yaml`
