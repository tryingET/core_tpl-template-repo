# TIP-0003: Repo-Local Diary by Structural Template

## Metadata

```yaml
tip: 0003
kind: meta
title: Diary is repo-local (`./diary/`) for every archetype

provenance:
  source_agent: session-continuation
  source_l1: core/tpl-template-repo
  discovered: 2026-02-24
  validated_days: 0
  implemented: 2026-02-24

evidence:
  before:
    pattern: "Mixed diary authority (workspace/global vs repo-local)"
    problem: "Context drift and unclear ownership of raw session capture"
  after:
    pattern: "Repo-local diary in every structural template"
    benefit: "Clear local continuity + consistent KES entry point per repo"
  sample_size: pattern correction
  confidence: high

changes:
  - file: core/tpl-template-repo/AGENTS.md
    kind: modify
    patch: |
      Enforce repo-local diary policy (`./diary/`).

  - file: copier-template/copier/tpl-agent-repo/diary/README.md
    kind: create
  - file: copier-template/copier/tpl-org-repo/diary/README.md
    kind: create
  - file: copier-template/copier/tpl-project-repo/diary/README.md
    kind: create

  - file: copier-template/copier/tpl-agent-repo/docs/diary/
    kind: remove
  - file: copier-template/copier/tpl-org-repo/docs/diary/
    kind: remove
  - file: copier-template/copier/tpl-project-repo/docs/diary/
    kind: remove

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

**The continuity unit is the repository context in front of the agent.**

Each repo keeps its own raw capture under `./diary/`; crystallized outputs still live in `docs/learnings/`, `docs/decisions/`, and TIPs.

## Structural Contract

Apply the same diary contract per structural template:

- `tpl-agent-repo`
- `tpl-org-repo`
- `tpl-project-repo`
- `tpl-individual-repo` (when introduced)

## Crystallization Flow

```
Session → ./diary/ (raw) → docs/learnings/ (crystallized) → TIPs (propagated)
                               ↓
                         docs/decisions/
```

## Rules

1. `./diary/` exists in every generated repo type.
2. Diary entry template is consistent across archetypes.
3. No workspace/global diary is canonical for repo execution history.
4. Learnings remain per-repo and TIPs remain the propagation mechanism.
