# next_session_prompt.md

---

## TRUE INTENT

One sentence: The system now self-improves — templates learn from agents, agents inherit from templates, and the boundary between learning and propagation is dissolved.

The deeper intent: This file is the continuity mechanism. It ensures compound learning across sessions.

---

## STATE

```
L0: core/tpl-template-repo @ dbe5d20
    Validation: ✅ 4/4
    Ahead of origin: 32 commits
    TIPs applied: 0001, 0002, 0003

holdingco-templates  ✅ L0-GENERATED
healthco-templates   ✅ L0-GENERATED

softwareco:
    tpl-agent-repo  ✅ SYNCED
    tpl-org-repo    ✅ SYNCED
    tpl-owned-repo  ✅ KES ADDED (4412b90)
    tpl-contrib-repo ✅ KES ADDED (5cdc91b)
    tpl-infra-repo  ✅ KES ADDED (9e717b8)
```

---

## DECISION: Alt 2 (Selective KES) — IMPLEMENTED

**Chosen:** Add `docs/diary/` + `docs/learnings/` to all lane-specific templates. Skip `cognitive-tools/` (agent-centric).

**Rationale:** Cognitive tools are agent-specific. Lane repos are human-operated. Humans have their own crystallization methods. Diary captures session state; learnings captures patterns.

**Outcome:**

| Template | diary | learnings | decisions | cognitive-tools |
|----------|-------|-----------|-----------|-----------------|
| tpl-owned-repo | ✅ | ✅ | ✅ | ❌ |
| tpl-contrib-repo | ✅ | ✅ | ✅ | ❌ |
| tpl-infra-repo | ✅ | ✅ | ✅ | ❌ |

All three templates now have the KES infrastructure committed.

---

## RESIDUAL LIMITATIONS

- ~~softwareco lane-specific decision pending~~ ✅ RESOLVED
- TIP review process undefined
- Evidence standards not codified
- Metrics not instrumented
- ~~L0 changes not pushed~~ ✅ PUSHED
- Lane templates: local-only (no remotes configured)

---

## NEXT ACTIONS

```bash
# 1. Push L0 (DONE)
# cd ~/ai-society/core/tpl-template-repo && git push origin main

# 2. Lane templates (local-only, no remotes)
# KES additions committed locally

# 3. First domain TIP
# Create a domain TIP with evidence to establish pattern.

# 4. Metrics
# Define tip-count, acceptance-rate, propagation-count.
```

---

## COMPOUND VALUE

This file improves with use:
- Session summary → next session context
- Decision matrix → cognitive framework application
- Alternatives → prevents premature convergence
- Residual limitations → honest debt tracking

The document should feel inevitable: it's exactly what's needed for continuity, no more, no less.
