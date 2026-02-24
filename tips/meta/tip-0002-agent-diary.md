# TIP-0002: Agent Diary for Knowledge Crystallization

## Metadata

```yaml
tip: 0002
kind: meta
title: All agents should keep a diary for knowledge crystallization

provenance:
  source_agent: session-analysis
  source_l1: core/tpl-template-repo
  discovered: 2026-02-23
  validated_days: 0

evidence:
  before:
    pattern: "Learnings captured ad-hoc or not at all"
    problem: "Knowledge lost between sessions, re-learned the hard way"
  after:
    pattern: "Session → diary → learnings → TIPs"
    benefit: "Raw capture → crystallization → propagation"
  sample_size: pattern analysis
  confidence: high

changes:
  - file: copier-template/copier/tpl-agent-repo/diary/
    kind: create
    patch: |
      mkdir -p diary
      # Add README.md with entry template

  - file: copier-template/copier/tpl-agent-repo/AGENTS.md.j2
    kind: modify
    patch: |
      Add Knowledge Crystallization Flow section
      Add diary/ to read order

  - file: copier-template/copier/tpl-project-repo/diary/
    kind: create

  - file: copier-template/copier/tpl-org-repo/diary/
    kind: create

escalation:
  recommend_to_L0: true  # This IS L0
  recommend_to: []

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

**The soul:** Every session should leave the agent smarter. Every crystallized learning should leave all agents smarter.

The diary is the capture mechanism that makes crystallization possible.

## The Pattern

From `prompt-snippets.md` — KNOWLEDGE CRYSTALLIZATION:

```
What did we just learn?

Not what did we do. What did we LEARN that we didn't know before?

Extract:
- PATTERNS — What repeated structures emerged?
- ANTI-PATTERNS — What looked right but was wrong?
- SURPRISES — What violated expectations?
- HEURISTICS — What rules of thumb proved valid?
- CAVEATS — What doesn't generalize?

Knowledge that isn't crystallized is knowledge that will be re-learned the hard way.
```

## The Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Session   │────▶│    Diary    │────▶│  Learnings  │────▶│     TIPs    │
│   (raw)     │     │  (capture)  │     │(crystallize)│     │ (propagate) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │  Decisions  │
                    │   (ADRs)    │
                    └─────────────┘
```

- **Diary**: Raw capture during work
- **Learnings**: Crystallized patterns with evidence
- **Decisions**: Architectural/policy choices
- **TIPs**: Propagation to templates

## Entry Template

```markdown
# YYYY-MM-DD — [Session Focus]

## What I Did
- [Actions taken]

## What Surprised Me
- [Unexpected outcomes]

## Patterns That Emerged
- [Repeated structures]

## Crystallization Candidates

### → docs/learnings/
- [Learning to crystallize]

### → TIP Proposal
- [If this generalizes]
```

## Why This Works

1. **Capture is cheap** — Don't overthink, just write
2. **Crystallization is expensive** — Do it when patterns are clear
3. **Propagation compounds** — One TIP benefits all future agents

## Anti-Patterns

- ❌ Skipping diary → learnings die
- ❌ Over-structured diary → friction → skipped
- ❌ Never crystallizing → diary becomes graveyard
- ❌ Crystallizing too early → patterns not yet clear

## RESIDUAL LIMITATIONS

- Requires discipline to maintain
- No automated tooling yet
- Quality depends on agent self-awareness

## EVOLUTION NOTES

As this pattern matures:
1. First diaries will be crude → establish habit
2. Crystallization will formalize → better patterns
3. Cross-agent diary analysis → meta-TIPs
4. Automated pattern extraction → scale crystallization
