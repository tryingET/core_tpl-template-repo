# TIP-0001: Universal Learnings + Decisions Structure

## Metadata

```yaml
tip: 0001
kind: meta
title: All template types need learnings/ and decisions/ structures

provenance:
  source_agent: session-analysis
  source_l1: healthco-templates
  discovered: 2026-02-21
  validated_days: 0

evidence:
  before:
    tpl-agent-repo: learnings ✅, decisions ❌
    tpl-project-repo: learnings ❌, decisions ✅
    tpl-org-repo: learnings ❌, decisions ✅
  after:
    all_templates: learnings ✅, decisions ✅
  sample_size: 3 template types
  confidence: high

changes:
  - file: copier-template/copier/tpl-project-repo/docs/learnings/
    kind: create
    patch: |
      mkdir -p docs/learnings
      # Add .gitkeep
      # Add README.md with structure guidance

  - file: copier-template/copier/tpl-project-repo/AGENTS.md.j2
    kind: modify
    patch: |
      Add `docs/learnings/` to read order

  - file: copier-template/copier/tpl-org-repo/docs/learnings/
    kind: create
    patch: |
      mkdir -p docs/learnings
      # Add .gitkeep
      # Add README.md with structure guidance

  - file: copier-template/copier/tpl-org-repo/AGENTS.md.j2
    kind: modify
    patch: |
      Add `docs/learnings/` to read order

  - file: copier-template/copier/tpl-agent-repo/docs/decisions/
    kind: create
    patch: |
      mkdir -p docs/decisions
      # Add .gitkeep
      # Add README.md with ADR-style structure

  - file: copier-template/copier/tpl-agent-repo/AGENTS.md.j2
    kind: modify
    patch: |
      Add `docs/decisions/` to read order

escalation:
  recommend_to_L0: true  # This IS L0
  recommend_to: []

review:
  status: proposed
  reviewers: []
```

## TRUE INTENT

**The soul:** Every repository, regardless of type, accumulates knowledge that should be:
1. Captured (learnings)
2. Propagated (TIPs)
3. Referenced (decisions)

The current structure artificially separates these by template type, which is wrong. A project learns. An org learns. An agent makes decisions.

## Rationale

### Why Learnings Everywhere?

- **Projects** learn about architecture, dependencies, process
- **Orgs** learn about governance, culture, operations
- **Agents** learn about prompts, behaviors, context

Without `docs/learnings/` in project/org templates, those learnings die in the repo.

### Why Decisions Everywhere?

- **Projects** make architectural decisions (ADRs)
- **Orgs** make policy decisions
- **Agents** make behavior/context decisions

Without `docs/decisions/` in agent templates, there's no structured way to document why an agent behaves a certain way.

## Proposed Structure

### docs/learnings/README.md (for all templates)

```markdown
# Learnings

Capture what works, what doesn't, and what to try next.

## Structure

- `YYYY-MM-DD-topic.md` — dated learning entries
- Link to TIPs if learning should propagate

## Template

\`\`\`markdown
# [Topic]

## Context
What situation triggered this learning?

## Discovery
What did we learn?

## Evidence
How do we know it's true?

## Application
Where else does this apply?

## TIP Candidate
Should this become a TIP? Why/why not?
\`\`\`
```

### docs/decisions/README.md (for all templates)

```markdown
# Decisions

Record significant decisions and their context.

## Format

ADR-style (Architecture Decision Records) adapted for this repo type.

## Template

\`\`\`markdown
# D-NNNN: [Title]

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue being addressed?

## Decision
What is the change being proposed/made?

## Consequences
What becomes easier? What becomes harder?
\`\`\`
```

## AGENTS.md Read Order Updates

### tpl-agent-repo

```
## Read order
1) `docs/_core/README.md`
2) `docs/person/`
3) `docs/decisions/`     # NEW
4) `docs/learnings/`
5) `docs/system4d/`
```

### tpl-project-repo

```
## Read order
1) `docs/_core/`
2) `docs/org_context/`
3) `docs/project/`
4) `docs/decisions/`
5) `docs/learnings/`     # NEW
6) `docs/system4d/`
```

### tpl-org-repo

```
## Read order
1) `docs/_core/`
2) `docs/org/`
3) `docs/decisions/`
4) `docs/learnings/`     # NEW
5) `docs/registers/`
6) `docs/system4d/`
```

## RESIDUAL LIMITATIONS

- Existing L1/L2 repos won't automatically get these structures
- Need migration script or manual addition
- Content templates are suggestions, not enforced

## NEXT ACTIONS

1. Apply to L0 templates
2. Re-validate with `check-l0.sh`
3. Re-generate holdingco-templates to verify propagation
4. Consider fixture updates
