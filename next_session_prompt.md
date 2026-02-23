# next_session_prompt.md

> Transmission from the system architecture layer.

---

## STATE

```
L0: core/tpl-template-repo
    Validation: ✅ 4/4 PASS
    Working tree: CLEAN
    TIPs: tip-0001, tip-0002, tip-0003 applied

L1: holdingco-templates  ✅ L0-GENERATED (208 files)
L1: healthco-templates   ✅ L0-GENERATED (208 files)
L1: softwareco-templates  REGISTRY (analysis complete, awaiting decision)
```

---

## APPLY COGNITIVE FRAMEWORKS

Before executing tasks, apply these frameworks to find leverage and avoid waste.

### 1. NEXUS — What's the Highest-Leverage Intervention?

Rank remaining tasks by compound value:

| Task | Solves Multiple Problems? | Compounds? | Enables Future Work? | NEXUS Score |
|------|---------------------------|------------|---------------------|-------------|
| Push to origin | No | No | Yes (others can pull) | Low |
| softwareco sync | Yes (unifies templates) | Yes (all softwareco agents inherit) | Yes (cross-pollination) | **HIGH** |
| First domain TIPs | Yes (demonstrates pattern) | Yes (compound learning) | Yes (sets precedent) | **HIGH** |
| Metrics instrumentation | No | Maybe | Yes (visibility) | Medium |

**NEXUS candidates:** softwareco sync + first domain TIPs (together they establish the full KES loop)

### 2. FIRST PRINCIPLES — softwareco Sync Decision

The question: Should tpl-agent-repo and tpl-org-repo in softwareco sync from L0?

**Decompose:**
- Why separate? → softwareco has different lanes (owned, contrib, infra)
- Why sync? → DRY, consistent agent behavior across ecosystem
- What MUST be true? → Templates must produce valid repos for their lane
- What's assumed impossible? → "Registry pattern can't use embedded templates"

**Axioms:**
1. Templates must produce valid L2 repos
2. Lane-specific extensions are needed for owned/contrib/infra
3. Agent and org templates are lane-agnostic

**Reconstruction:**
- Lane-agnostic templates (agent, org) → sync from L0
- Lane-specific templates (owned, contrib, infra) → extend L0 or stay separate
- Registry remains authoritative for lane → template mapping

**First move:** Sync tpl-agent-repo from L0, verify healthco agents still work, then softwareco agents.

### 3. TEMPORAL DEGRADATION — Metrics

**6 months out:** What has broken?
- TIPs proposed but not tracked → no visibility into improvement rate
- Metrics directory exists but empty → false sense of completeness
- No automated collection → manual effort → skipped

**12 months out:**
- Can't measure if KES is working → faith-based system
- No evidence for TIP acceptance → subjective decisions

**Prevention today:**
- Define minimum viable metrics (TIP count, acceptance rate, propagation count)
- Add to CI: count TIPs on each run
- Weekly summary script (or manual process first)

### 4. ESCAPE HATCH — Before Syncing softwareco

If sync goes wrong:
- Detection: L2 generation fails in softwareco
- Rollback: Revert to pre-sync softwareco templates
- Side effects: Existing softwareco agents may need regeneration

**Smallest irreversible step:** Sync one template (tpl-agent-repo), test with one agent, then expand.

---

## REMAINING TASKS (Prioritized by NEXUS)

### Priority 1: softwareco Sync (NEXUS intervention)

```bash
# First principles says: sync lane-agnostic templates, keep lane-specific separate

# 1. Test sync with one template
cd ~/ai-society/core/tpl-template-repo
./scripts/new-l1-from-copier.sh ~/ai-society/softwareco/tpl-agent-repo-test \
  -d repo_slug=tpl-agent-repo \
  --defaults --overwrite

# 2. Compare with existing softwareco tpl-agent-repo
diff -r ~/ai-society/softwareco/tpl-agent-repo ~/ai-society/softwareco/tpl-agent-repo-test

# 3. If compatible, update softwareco's tpl-agent-repo
# 4. Regenerate a softwareco agent to verify
```

### Priority 2: First Domain TIPs (Demonstrate KES)

Candidates from this session:
- `tips/domain/tip-domain-001.md`: Generic activity prompts need domain overlays
- `tips/domain/tip-domain-002.md`: L1 README should list domain-specific templates

Create at least one TIP with evidence to establish the pattern.

### Priority 3: Push to Origin

```bash
cd ~/ai-society/core/tpl-template-repo
git push origin main
```

### Priority 4: Metrics MVP

Define minimum viable metrics:
- `metrics/tip-count`: Number of TIPs in tips/
- `metrics/acceptance-rate`: Accepted / Total proposed
- `metrics/propagation-count`: TIPs escalated to L0

---

## OPEN QUESTIONS

Use CONSTRAINT INVENTORY to analyze:

| Question | Assumed Constraint | Is It Real? |
|----------|-------------------|-------------|
| TIP review: human-only? | "AI can't review quality" | False — AI can draft, human approve |
| Evidence standards undefined? | "Need formal process first" | False — start simple, evolve |
| Cross-L1 propagation unclear? | "Each L1 is isolated" | False — can escalate to L0 which all inherit |

---

## QUICK REFERENCE

```bash
# Validate
cd ~/ai-society/core/tpl-template-repo && bash ./scripts/check-l0.sh

# Generate
./scripts/new-l1-from-copier.sh /path/to/templates -d repo_slug=name --defaults --overwrite
./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent -d repo_slug=name --defaults --overwrite

# Cognitive tools (invoke when stuck)
# "What's the NEXUS intervention here?"
# "Apply FIRST PRINCIPLES to this blocker"
# "Inventory our CONSTRAINTS"
# "Design the ESCAPE HATCH first"
```
