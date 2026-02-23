# TIP-0003: Global Diary + Per-Repo Learnings

## Metadata

```yaml
tip: 0003
kind: domain
title: Diary is global (agent-level), learnings are per-repo

provenance:
  source_agent: session-continuation
  source_l1: core/tpl-template-repo
  discovered: 2026-02-21
  validated_days: 2
  implemented: 2026-02-23

evidence:
  before:
    pattern: "KES duplicated in every template"
    problem: "Diary per-repo creates fragmentation, cognitive-tools scattered"
  after:
    pattern: "Global diary + cognitive-tools in ~/.pi/agent/AGENTS.md; per-repo learnings only"
    benefit: "Agent continuity across all repos; crystallization captured where it matters"
  sample_size: pattern analysis
  confidence: high

changes:
  - file: ~/.pi/agent/AGENTS.md
    kind: modify
    patch: |
      Add Cognitive Tools section (reference to prompt-snippets.md)
      Add Diary section with entry format
      Add Diary Entries section for session capture
  
  - file: softwareco/tpl-owned-repo/docs/learnings/
    kind: create
  - file: softwareco/tpl-infra-repo/docs/learnings/
    kind: create
  - file: softwareco/tpl-contrib-repo/AGENTS.md.jinja
    kind: modify
    patch: |
      Add "Upstream-Facing Note" explaining global diary does NOT apply

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

**The soul:** The agent is the continuity unit, not the repo.

Diary captures the agent's session state across ALL repos. Learnings capture crystallized patterns specific to a repo.

## The Pattern

| Component | Location | Scope | Purpose |
|-----------|----------|-------|---------|
| **Diary** | `~/.pi/agent/AGENTS.md` | Global | Session continuity across all work |
| **Cognitive Tools** | `~/.pi/agent/AGENTS.md` | Global | Reasoning frameworks (INVERSION, etc.) |
| **Learnings** | `docs/learnings/` per-repo | Repo-specific | Crystallized patterns for that context |
| **Decisions** | `docs/decisions/` per-repo | Repo-specific | ADRs for that codebase |

## Crystallization Flow

```
Session → Diary (global) → Learnings (per-repo) → TIPs (L0)
                                    ↓
                              Decisions (per-repo)
```

1. **Raw capture** → Global diary (always available)
2. **Crystallization** → Per-repo learnings (when pattern emerges)
3. **Propagation** → TIPs (when pattern generalizes)

## Per-Lane Application

| Lane | Learnings | Notes |
|------|-----------|-------|
| Owned | ✅ `docs/learnings/` | Internal, commit patterns |
| Infra | ✅ `docs/learnings/` | Internal, commit incident learnings |
| Contrib | ❌ None | Upstream-facing, global diary does NOT apply |
| Agent | ✅ `docs/learnings/` | Core to agent memory |

## Why Contrib is Different

Contrib repos interact with upstream. The agent working on contrib:
- Should NOT capture diary entries about upstream work (leaks context)
- Should NOT have local learnings about upstream (creates divergence)
- Follows upstream's contribution patterns instead

The global diary explicitly notes this exception.

## RESIDUAL LIMITATIONS

- LOOPS (automated crystallization) not yet implemented at company/holdingco level
- TIP review process undefined (needs governance-kernel integration)
- No automated reminders to crystallize diary → learnings
