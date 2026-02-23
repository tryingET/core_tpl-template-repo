# TIP-0003: Selective KES for Lane Templates

## Metadata

```yaml
tip: 0003
kind: domain
title: Lane-specific templates get selective KES (diary + learnings), not cognitive-tools

provenance:
  source_agent: session-continuation
  source_l1: core/tpl-template-repo
  discovered: 2026-02-21
  validated_days: 0
  implemented: 2026-02-21

evidence:
  before:
    pattern: "KES only in agent templates"
    problem: "Lane templates (owned, contrib, infra) had no crystallization infrastructure"
  after:
    pattern: "All templates have diary + learnings; cognitive-tools remain agent-only"
    benefit: "Humans can crystallize knowledge; AI-specific tools stay where AI operates"
  sample_size: 3 lane templates
  confidence: high

changes:
  - file: softwareco/tpl-owned-repo/docs/learnings/
    kind: create
  - file: softwareco/tpl-owned-repo/docs/diary/
    kind: create
  - file: softwareco/tpl-contrib-repo/docs/learnings/
    kind: create
  - file: softwareco/tpl-contrib-repo/docs/diary/
    kind: create
  - file: softwareco/tpl-infra-repo/docs/learnings/
    kind: create
  - file: softwareco/tpl-infra-repo/docs/diary/
    kind: create

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

**The soul:** Every repository type can accumulate knowledge. But not every repository needs AI-specific cognitive tools.

The distinction matters because:
1. **Diary** captures raw session state — useful for humans too
2. **Learnings** crystallizes patterns — useful for teams
3. **Cognitive-tools** are prompts for AI reasoning — agent-specific

## The Decision Matrix

Applied INVERSION to generate alternatives:

| Alt | Diary | Learnings | Cognitive-tools | Verdict |
|-----|-------|-----------|-----------------|---------|
| 1 | ✅ | ✅ | ✅ | Too heavy for human repos |
| 2 | ✅ | ✅ | ❌ | **SELECTED** — pragmatic |
| 3 | ❌ | ❌ | ❌ | Too light — knowledge dies |
| 4 | N/A (abstraction) | — | — | Adds complexity |
| 5 | N/A (opt-in) | — | — | Will be forgotten |

## Why Cognitive-tools Stay Agent-Only

1. **Human operators** have their own methods (notes, docs, retros)
2. **Cognitive tools** (like INVERSION, FIRST PRINCIPLES) are prompt patterns for AI reasoning
3. **Forced structure** that isn't used becomes skeleton clutter
4. **Future-proofing** — if AI operates these lanes later, add cognitive-tools then

## Application

When creating or reviewing lane-specific templates:

1. **Owned repos** → Add diary + learnings
2. **Contrib repos** → Add diary + learnings
3. **Infra repos** → Add diary + learnings
4. **Agent repos** → Add diary + learnings + cognitive-tools

## RESIDUAL LIMITATIONS

- If future AI operates infra/owned lanes, cognitive-tools will be needed
- Requires discipline to maintain diary → learnings → TIPs flow
- No automated reminders or tooling yet
