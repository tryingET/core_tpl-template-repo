# Learnings (L0)

Capture durable lessons for `core/tpl-template-repo`.

## KES flow (mandatory)

Session output is not considered complete until it moves through this path:

```text
Session output → diary/ (raw) → docs/learnings/ (crystallized) → tips/meta/ (propagated)
```

## What goes here

- Repeated patterns that changed implementation decisions
- Anti-patterns that caused regressions or review churn
- Heuristics that should shape future guardrails/checks

## Deep-review output handling

When a `/deep-review` finds bugs/debt/smells/gaps:

1. Capture raw notes in `diary/YYYY-MM-DD--type-scope-summary.md`
2. Crystallize validated findings into a dated learning doc in `docs/learnings/`
3. Promote cross-repo/meta findings into a TIP under `tips/meta/`
4. Add/adjust deterministic checks so the same class of issue fails fast

## Entry template

```markdown
# YYYY-MM-DD — [Learning title]

## Context
[What triggered this learning]

## Evidence
[What proved this true]

## Pattern
[What repeats]

## Guardrail
[What check/doc/process now enforces it]

## Propagation
- TIP candidate: [yes/no + path]
```
