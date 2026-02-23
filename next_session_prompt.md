# next_session_prompt.md

> Transmission from the system architecture layer.

---

## STATE

```
L0: core/tpl-template-repo
    Validation: ✅ 4/4 PASS
    Working tree: CLEAN
    TIPs: tip-0001, tip-0002, tip-0003 applied
    Ahead of origin: 8 commits

L1: holdingco-templates  ✅ L0-GENERATED (208 files)
L1: healthco-templates   ✅ L0-GENERATED (208 files)

softwareco:
    tpl-agent-repo  ✅ SYNCED from L0 + GitHub CI + tech-stack.sh
    tpl-org-repo    ✅ SYNCED from L0 + GitHub CI
    tpl-owned-repo  ⏳ Lane-specific, not synced
    tpl-contrib-repo ⏳ Lane-specific, not synced
    tpl-infra-repo  ⏳ Lane-specific, not synced
```

---

## SESSION SUMMARY (2026-02-23)

### Completed

| Task | Description |
|------|-------------|
| softwareco sync (NEXUS) | tpl-agent-repo + tpl-org-repo synced from L0 |
| FIRST PRINCIPLES applied | Lane-agnostic → sync; lane-specific → keep separate |
| ESCAPE HATCH applied | Tested generation before committing |

### Sync Approach

```
L0 (GitLab) → softwareco (GitHub):
1. Copy from L0
2. Convert .j2 → .jinja
3. Remove .gitlab-ci.yml, add .github/workflows/ci.yml
4. Add softwareco-specific: .githooks/, tech-stack.sh
5. Test generation → commit
```

### What softwareco Templates Now Have

- `docs/diary/` — Knowledge crystallization
- `docs/decisions/` — ADRs
- `docs/learnings/README.md` — Structure guidance
- `prompts/cognitive-tools/` — 8 frameworks
- AGENTS.md sections: Knowledge Crystallization Flow, Cognitive Tools

---

## REMAINING (Prioritized)

### Priority 1: Push to Origin

```bash
cd ~/ai-society/core/tpl-template-repo && git push origin main
```

### Priority 2: First Domain TIPs

Create TIPs with evidence to establish the pattern:
- `tips/domain/tip-001.md`: Activity prompts need domain overlays
- Document in holdingco-templates or healthco-templates

### Priority 3: softwareco Lane-Specific Templates

Decision needed for tpl-owned-repo, tpl-contrib-repo, tpl-infra-repo:
- Option A: Keep as-is (they're domain-specific)
- Option B: Add diary/learnings/decisions/cognitive-tools from L0
- Option C: Extend from a base template

### Priority 4: Metrics MVP

- `metrics/tip-count`: Number of TIPs
- `metrics/acceptance-rate`: Accepted / Total
- `metrics/propagation-count`: TIPs escalated to L0

---

## OPEN QUESTIONS

| Question | Status | Next Step |
|----------|--------|-----------|
| TIP review process | Undefined | Start with human review, evolve to AI-assisted |
| Evidence standards | Undefined | Start with "before/after + sample size" |
| Cross-L1 propagation | L0 is hub | All meta-TIPs escalate to L0 |

---

## QUICK REFERENCE

```bash
# Validate
cd ~/ai-society/core/tpl-template-repo && bash ./scripts/check-l0.sh

# Generate L1
./scripts/new-l1-from-copier.sh /path/to/templates -d repo_slug=name --defaults --overwrite

# Generate L2 agent
cd /path/to/templates && ./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent -d repo_slug=name --defaults --overwrite

# Cognitive tools (invoke when stuck)
# "What's the NEXUS intervention here?"
# "Apply FIRST PRINCIPLES to this blocker"
# "Design the ESCAPE HATCH first"
```
