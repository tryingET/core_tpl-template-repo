# next_session_prompt.md

---

## TRUE INTENT

One sentence: The system now self-improves — templates learn from agents, agents inherit from templates, and the boundary between learning and propagation is dissolved.

The deeper intent: This file is the continuity mechanism. It ensures compound learning across sessions.

---

## STATE

```
L0: core/tpl-template-repo @ 8e3bc78
    Validation: ✅ 4/4
    Ahead of origin: 10 commits
    TIPs applied: 0001, 0002, 0003

holdingco-templates  ✅ L0-GENERATED
healthco-templates   ✅ L0-GENERATED

softwareco:
    tpl-agent-repo  ✅ SYNCED
    tpl-org-repo    ✅ SYNCED
    tpl-{owned,contrib,infra}-repo  → DECISION BELOW
```

---

## THE DECISION

**Question:** Should lane-specific templates get KES infrastructure?

**Why it matters:** This determines whether ALL repos in the ecosystem crystallize knowledge, or only agents do.

**Current gap:**

| Template | diary | learnings | decisions | cognitive-tools |
|----------|-------|-----------|-----------|-----------------|
| tpl-owned-repo | ❌ | ❌ | ❌ | ❌ |
| tpl-contrib-repo | ❌ | ❌ | ✅ | ❌ |
| tpl-infra-repo | ❌ | ❌ | ✅ | ❌ |

---

## FIVE ALTERNATIVES

Applied INVERSION: Discard the obvious solution. Generate alternatives that reframe the problem.

### Alt 1: Full KES to All

Add diary, learnings, decisions, cognitive-tools to all three.

**Insight:** Every repo learns. Crystallization is universal.

**Breaks:** Maintenance burden. Some lanes don't need cognitive-tools.

---

### Alt 2: Selective KES (Recommended)

Add diary + learnings. Skip cognitive-tools.

**Insight:** Cognitive tools are agent-centric. Lane repos are human-operated. Humans have their own crystallization methods. Diary captures session state; learnings captures patterns. That's the minimum.

**Breaks:** Inconsistency if future AI operates these lanes.

---

### Alt 3: Keep As-Is

KES is agent-only. Lane-specific templates serve humans.

**Insight:** Maybe the problem assumes KES is needed everywhere. Forced structure may create unused skeleton.

**Breaks:** Future AI operators won't have KES. Incident learnings not captured systematically.

---

### Alt 4: Base Template Composition

Create `tpl-base-repo` in L0. Lane templates extend it.

**Insight:** DRY principle. Single source of truth.

**Breaks:** Copier composition is complex. Adds abstraction layer.

---

### Alt 5: Post-Generate Hook

KES added on demand, not in templates.

**Insight:** KES as opt-in infrastructure.

**Breaks:** Will be forgotten. Inconsistent repos.

---

## RECOMMENDATION

**Alt 2 (Selective KES)** is pragmatic:
- diary/learnings to all three
- cognitive-tools stays agent-only
- minimal maintenance, captures what matters

**Unless:** Future AI operators are planned for infra/owned lanes. Then Alt 1.

---

## RESIDUAL LIMITATIONS

- TIP review process undefined
- Evidence standards not codified
- Metrics not instrumented
- softwareco lane-specific decision pending

---

## NEXT ACTIONS

```bash
# 1. Push
cd ~/ai-society/core/tpl-template-repo && git push origin main

# 2. Decide
# After reviewing Alt 1-5 above, choose one.

# 3. First TIP
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
