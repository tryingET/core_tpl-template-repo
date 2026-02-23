# TIPs — Template Improvement Proposals

TIPs are the genome for template evolution. They capture learnings from agents
and propagate improvements across the entire template hierarchy.

## Flow

```
Agent learns → TIP proposed → Review → Merge → Propagate → Measure
```

## Kinds

| Kind | Scope | Escalates to L0? |
|------|-------|------------------|
| `domain` | L1-specific | No |
| `meta` | Cross-cutting patterns | Yes |
| `infrastructure` | Build/CI/template tooling | Yes |

## Evidence Standards

TIPs require evidence:

```yaml
evidence:
  before: { metric: value }
  after: { metric: value }
  sample_size: N
  confidence: low | medium | high
```

## Escalation

- `recommend_to_L0: true` → propagates to core/tpl-template-repo
- `recommend_to: [other-l1-templates]` → cross-pollinates

## Review Process

1. Proposed → reviewed by maintainer
2. Accepted → merged into L1 templates
3. Meta-TIPs → escalated to L0 for system-wide propagation

## Compound Effect

Without KES: Learnings die with agents
With KES: Learnings propagate to ALL future agents

```
100 agents × 100 learnings × propagation = 10,000 inherited learnings
```
