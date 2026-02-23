# next_session_prompt.md

---

## TRUE INTENT

One sentence: The system now self-improves — templates learn from agents, agents inherit from templates, and the boundary between learning and propagation is dissolved.

The deeper intent: This file is the continuity mechanism. It ensures compound learning across sessions.

---

## STATE

```
L0: core/tpl-template-repo @ 25bbb4c
    Validation: ✅ 4/4
    TIPs: 3 (2 accepted, 1 proposed)

holdingco-templates  ✅ L0-GENERATED
healthco-templates   ✅ L0-GENERATED

softwareco:
    tpl-agent-repo  ✅ SYNCED
    tpl-org-repo    ✅ SYNCED
    tpl-owned-repo  ✅ learnings/ (local)
    tpl-contrib-repo ✅ no KES (upstream-facing)
    tpl-infra-repo  ✅ learnings/ (local)

governance-kernel:
    guiding-circle.md ✅ LOOPS + TIP acceptance TODO added
```

---

## KES PATTERN (Final)

| Component | Location | Scope |
|-----------|----------|-------|
| **Diary** | `~/ai-society/AGENTS.md` | Workspace |
| **Cognitive Tools** | `~/ai-society/AGENTS.md` | Workspace |
| **Learnings** | `docs/learnings/` per-repo | Repo-specific |
| **Decisions** | `docs/decisions/` per-repo | Repo-specific |

| Lane | Learnings | Notes |
|------|-----------|-------|
| Owned | ✅ | Commit patterns |
| Infra | ✅ | Commit incident learnings |
| Contrib | ❌ | Diary does NOT apply |
| Agent | ✅ | Core to memory |

---

## RESIDUAL LIMITATIONS

- LOOPS not implemented (awaiting company/holdingco implementation)
- TIP review process undefined (awaiting Guiding Circle)
- Lane templates are local-only (no remotes)
- Evidence standards not codified
- governance-kernel has uncommitted changes (unrelated)

---

## NEXT ACTIONS

```bash
# 1. Run validation
cd ~/ai-society/core/tpl-template-repo && ./scripts/check-l0.sh && ./scripts/tip-metrics.sh

# 2. Big picture:
# - LOOPS need implementation at company + holdingco layer
# - TIP acceptance needs Guiding Circle operational
# - Consider: set up remotes for lane templates?
```
