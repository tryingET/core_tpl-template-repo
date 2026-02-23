# Learnings from healthco Test

**Date:** 2026-02-21
**Source:** healthco-templates L0→L1→L2 validation

## What Worked

| Learning | Status | Notes |
|----------|--------|-------|
| L0→L1 generation | ✅ Proven | `new-l1-from-copier.sh` produces valid L1 |
| L1→L2 generation | ✅ Proven | 3 agents generated successfully |
| `.copier-answers.yml` provenance | ✅ Proven | Traces L2→L1→L0 chain |
| Validation scripts | ✅ Proven | `check-l0.sh` catches regressions |
| Template structure | ✅ Proven | `copier/tpl-*-repo/` pattern works |

## What Needs Improvement

| Issue | Impact | TIP Candidate |
|-------|--------|---------------|
| Domain prompts too generic | Agents lack domain context | Domain-specific prompt packs |
| No learnings loop | Agent learnings die in repo | KES infrastructure |
| No metrics | Can't measure template effectiveness | Metrics collection |
| No TIPs process | No structured improvement path | TIPs infrastructure |

## Evidence

```
healthco-templates/
├── .copier-answers.yml     ← l0_source_sha: 323af81c
└── copier/tpl-agent-repo/  ← generated 3 agents

Agents generated:
├── agent-nutritionist/
├── agent-physiotherapist/
└── agent-psychotherapist/

All have:
✅ .copier-answers.yml (L2→L1 provenance)
✅ AGENTS.md (agent instructions)
✅ scripts/ci/smoke.sh (CI baseline)
```

## TIPs to Create

### TIP-0001: Domain Prompt Packs

**Kind:** meta
**Escalate to L0:** Yes

**Problem:** Generic activity prompts (finance, health, governance) lack domain context.

**Solution:** L1 templates should ship with domain-specific prompt overlays.

**Evidence:**
- Before: Generic `prompts/activities/health.md`
- After: healthco-specific health context
- Sample size: 3 agents
- Confidence: medium

### TIP-0002: Learnings Loop

**Kind:** infrastructure
**Escalate to L0:** Yes

**Problem:** Agent learnings are not captured or propagated.

**Solution:** Add `docs/learnings/` structure with TIP escalation path.

**Evidence:**
- Before: Empty `docs/learnings/.gitkeep`
- After: Documented learnings with TIP candidates
- Sample size: 0 learnings captured (pattern not used)
- Confidence: high (this is the core KES gap)

## Compound Value

Without KES:
- 3 agents × 0 learnings = 0 propagated

With KES (after TIPs):
- 3 agents × N learnings × propagation = 3N inherited

## Next Steps

1. ✅ Document learnings (this file)
2. ⏳ Create TIP-0001 (domain prompt packs)
3. ⏳ Create TIP-0002 (learnings loop)
4. ⏳ Apply to holdingco-templates (already has KES infrastructure)
5. ⏳ Escalate meta-TIPs to L0
