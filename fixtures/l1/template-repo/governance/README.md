# Governance

Template governance layer for TIP review.

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
