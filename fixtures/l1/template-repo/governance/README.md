# Governance

Template governance layer for this company.

## Structure

```
governance/
├── README.md              # This file
└── programs/              # Company-level programs
    └── template-setup/
        └── work-items.json
```

## Program Tracking

Company-level programs are tracked in `programs/`:

| Program | Description |
|---------|-------------|
| template-setup | Individualize L2 templates, bootstrap company repos |

See `programs/README.md` for details.

## TIP Review Authority

- **Domain TIPs**: Reviewed by L1 maintainer
- **Meta TIPs**: Escalate to L0 maintainers
- **Infrastructure TIPs**: Escalate to L0 maintainers

## Consent Model

Changes flow through consent:
1. TIP proposed with evidence
2. Review period (default: 3 days)
3. No objection → merge
4. Objection → discuss → revise → re-propose

## Escalation Paths

```
L1 TIPs ─┬─ domain ──────► stay local
         │
         ├─ meta ────────► L0 core/tpl-template-repo
         │
         └─ infra ───────► L0 core/tpl-template-repo
```

## Hierarchy

| Level | Scope | Location |
|-------|-------|----------|
| L0 | Cross-company | governance-kernel/governance/programs/ |
| L1 | Company | this repo: governance/programs/ |
| L2 | Project | repo/governance/work-items.json |
