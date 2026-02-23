# next_session_prompt.md

> Transmission from the system architecture layer.

---

## STATE

```
L0: core/tpl-template-repo
    Validation: ✅ 4/4 PASS
    Working tree: CLEAN
    TIPs: tip-0001, tip-0002, tip-0003 applied
    Ahead of origin: 9 commits

L1: holdingco-templates  ✅ L0-GENERATED (208 files)
L1: healthco-templates   ✅ L0-GENERATED (208 files)

softwareco:
    tpl-agent-repo  ✅ SYNCED from L0
    tpl-org-repo    ✅ SYNCED from L0
    tpl-owned-repo  ⏳ DECISION REQUIRED (see below)
    tpl-contrib-repo ⏳ DECISION REQUIRED (see below)
    tpl-infra-repo  ⏳ DECISION REQUIRED (see below)
```

---

## SESSION SUMMARY (2026-02-23)

### Completed

| Task | Description |
|------|-------------|
| TIP-0001 | Universal learnings + decisions in all templates |
| TIP-0002 | Diary for knowledge crystallization |
| TIP-0003 | Cognitive tools for higher-order thinking |
| softwareco sync | tpl-agent-repo + tpl-org-repo synced from L0 |

---

## DECISION REQUIRED: softwareco Lane-Specific Templates

### The Question

Should `tpl-owned-repo`, `tpl-contrib-repo`, and `tpl-infra-repo` also get KES infrastructure?

### Current State

| Template | diary/ | learnings/ | decisions/ | cognitive-tools/ |
|----------|--------|------------|------------|------------------|
| tpl-owned-repo | ❌ | ❌ | ❌ | ❌ |
| tpl-contrib-repo | ❌ | ❌ | ✅ | ❌ |
| tpl-infra-repo | ❌ | ❌ | ✅ | ❌ |

### What's Unique to Each

| Template | Unique Features |
|----------|-----------------|
| tpl-owned-repo | `convex/`, `package.json`, `src/`, `tests/`, `docs/owned/` |
| tpl-contrib-repo | `docs/contrib/`, `docs/dev/`, upstream sync focus |
| tpl-infra-repo | `docs/incidents/`, `docs/rollout/`, `docs/runbooks/`, `governance/` |

---

## INVERSION — Five Alternatives

You've found one solution (sync everything). Now discard it. Generate five alternatives:

### Alternative 1: Add KES to All Lane-Specific Templates

**Approach:** Add `docs/diary/`, `docs/learnings/`, `prompts/cognitive-tools/` to all three templates.

**Core insight:** Every repo learns. Knowledge crystallization is universally valuable, regardless of lane.

**What would make it work:**
- Copy KES infrastructure to each template
- Update AGENTS.md with Knowledge Crystallization Flow
- Test generation for each lane

**What breaks it:**
- Maintenance burden: 3 more templates to keep in sync
- Some lanes may not need cognitive-tools (infra is more procedural)
- Divergence risk if L0 evolves

---

### Alternative 2: Selective KES — diary/learnings Only, No cognitive-tools

**Approach:** Add minimal KES (`docs/diary/`, `docs/learnings/`) but NOT `prompts/cognitive-tools/`.

**Core insight:** Cognitive tools are agent-centric. Lane-specific repos (owned, contrib, infra) are not autonomous agents — they're human-operated projects. Crystallization still valuable, but frameworks are overkill.

**What would make it work:**
- Add diary + learnings to all three
- Skip cognitive-tools (humans can invoke externally if needed)
- Lighter weight, less maintenance

**What breaks it:**
- Inconsistent experience across templates
- Future AI operators of infra/owned repos won't have tools
- Half-measure that may need revisiting

---

### Alternative 3: Keep Lane-Specific As-Is, KES is Agent-Only

**Approach:** Do nothing. KES infrastructure is for agents only. Lane-specific templates serve humans who have their own crystallization processes.

**Core insight:** The problem assumes KES is universally needed. Maybe it's not. Humans keep notes differently. Forcing diary/learnings structure may create unused skeleton directories.

**What would make it work:**
- Leave tpl-owned, tpl-contrib, tpl-infra unchanged
- KES stays agent-centric (tpl-agent-repo only)
- Clear separation: agents = KES, projects = traditional docs

**What breaks it:**
- Inconsistent with tpl-agent-repo sync
- Future AI operators won't have KES in these lanes
- Learnings from infra incidents won't be captured systematically

---

### Alternative 4: Create Base Template, Extend for Each Lane

**Approach:** Create `tpl-base-repo` in L0 with KES infrastructure. Each lane-specific template extends it via copier composition.

**Core insight:** The DRY principle. Instead of copying KES to 3 templates, create a base they all inherit from.

**What would make it work:**
- Add `tpl-base-repo` to L0 with diary, learnings, decisions, cognitive-tools
- softwareco templates use copier's `_extends` or manual composition
- Single source of truth for KES

**What breaks it:**
- Copier composition is complex (not well-documented)
- May require restructuring how softwareco templates work
- Adds abstraction layer that could break

---

### Alternative 5: KES as Post-Generate Hook, Not Template Content

**Approach:** Don't add KES to templates at all. Instead, provide a post-generation script that adds KES infrastructure to any generated repo on demand.

**Core insight:** The problem assumes KES must be in templates. What if it's optional infrastructure added when needed?

**What would make it work:**
- Create `scripts/add-kes.sh` in softwareco-templates
- After generating any repo, run `./scripts/add-kes.sh /path/to/repo`
- KES is opt-in, not forced

**What breaks it:**
- Extra step in workflow (will be forgotten)
- Inconsistent repos (some have KES, some don't)
- Defeats the purpose of template standardization

---

## Synthesis

**What did the first solution miss that these alternatives reveal?**

1. **Cognitive tools may be agent-centric** — not all repos need them (Alt 2)
2. **KES might not be universally needed** — humans work differently (Alt 3)
3. **The maintenance burden is real** — 3 more templates to sync (Alt 1, 4)
4. **Copier composition exists** — but may be over-engineering (Alt 4)

## Recommended Approach

Based on the alternatives, consider **Alternative 2 (Selective KES)** as the pragmatic choice:

- Add `docs/diary/` + `docs/learnings/` to all three
- Skip `prompts/cognitive-tools/` (human-operated repos)
- Minimal maintenance, maximum value

**But if future AI operators are planned for infra/owned lanes, then Alternative 1 (full KES) is better.**

---

## REMAINING TASKS

### Priority 1: Push to Origin

```bash
cd ~/ai-society/core/tpl-template-repo && git push origin main
```

### Priority 2: Decide on Lane-Specific KES

After reviewing alternatives above, choose:
- [ ] Alt 1: Full KES to all
- [ ] Alt 2: diary/learnings only (recommended)
- [ ] Alt 3: Keep as-is, KES is agent-only
- [ ] Alt 4: Create base template with composition
- [ ] Alt 5: KES as post-generate hook

### Priority 3: First Domain TIPs

Create TIPs with evidence to establish the pattern.

### Priority 4: Metrics MVP

Define collection mechanism.

---

## QUICK REFERENCE

```bash
# Validate
cd ~/ai-society/core/tpl-template-repo && bash ./scripts/check-l0.sh

# Generate
./scripts/new-l1-from-copier.sh /path/to/templates -d repo_slug=name --defaults --overwrite

# Cognitive tools (invoke when stuck)
# "What's the NEXUS intervention here?"
# "Apply FIRST PRINCIPLES to this blocker"
# "Generate five ALTERNATIVES"
# "Design the ESCAPE HATCH first"
```
