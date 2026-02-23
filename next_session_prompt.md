# next_session_prompt.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Branch: `main`
- Working tree: **clean**
- HEAD: `e173677` (`docs: update session prompt - P0 and P1 complete`)
- Validation: **passes** (`bash ./scripts/check-l0.sh`)

---

## ✅ P0 COMPLETE: L0 Architecture Fix

L0 now embeds proper archetype templates:
```
copier-template/copier/
├── tpl-agent-repo/
├── tpl-org-repo/
└── tpl-project-repo/
```

---

## ✅ P1 COMPLETE: healthco-templates Regenerated

healthco-templates now has tpl-*-repo/ structure.

| Agent | Status |
|-------|--------|
| `agent-psychotherapist` | ✅ New |
| `agent-nutritionist` | ✅ New |
| `agent-physiotherapist` | ⚠️ Old template |

---

## P1.5: Transition agent-physiotherapist

The physiotherapist was created from holdingco before the L0 fix. Transition it:

```bash
# 1. Preserve existing customizations
cd ~/ai-society/healthco/agents/agent-physiotherapist
cp -r docs/person /tmp/physio-person-backup
cp -r prompts/activities/physiotherapy.md /tmp/physio-activities-backup 2>/dev/null || true

# 2. Regenerate from healthco-templates
cd ~/ai-society/healthco/healthco-templates
./scripts/new-repo-from-copier.sh tpl-agent-repo ~/ai-society/healthco/agents/agent-physiotherapist \
  -d repo_slug=agent-physiotherapist \
  -d core_owner_handle=@healthco-owner \
  -d agent_owner_handle=@physiotherapist-owner \
  --defaults --overwrite

# 3. Restore customizations
cp -r /tmp/physio-person-backup/* ~/ai-society/healthco/agents/agent-physiotherapist/docs/person/
cp /tmp/physio-activities-backup ~/ai-society/healthco/agents/agent-physiotherapist/prompts/activities/physiotherapy.md 2>/dev/null || true

# 4. Verify
cd ~/ai-society/healthco/agents/agent-physiotherapist
./scripts/ci/smoke.sh
```

---

## 🚀 P3: Domain-Specific Activity Prompts + Learnings Feedback Loop

### The Problem

Current `tpl-agent-repo/prompts/activities/` has generic prompts:
- `health.md` - generic health advice
- `finance.md` - generic finance
- `governance.md` - generic governance

A physiotherapist agent needs **physiotherapy-specific** prompts:
- Assessment protocols
- Exercise prescription workflows
- Progress tracking schemas
- Referral red flags

### The Innovation: Living Templates

**Templates that evolve from agent learnings:**

```
L1: healthco-templates/
└── copier/tpl-agent-repo/
    └── prompts/activities/
        ├── _base/                 # Generic (from L0)
        │   ├── health.md
        │   └── governance.md
        └── _domain/               # Domain-specific (from healthco)
            ├── physiotherapy.md   # Grown from agent-physiotherapist learnings
            ├── psychotherapy.md   # Grown from agent-psychotherapist learnings
            └── nutrition.md       # Grown from agent-nutritionist learnings
```

### How It Works

```
1. Deploy agent-physiotherapist
2. Agent accumulates learnings in docs/learnings/
3. Extract patterns → prompts/activities/physiotherapy.md
4. New physiotherapist agents start with refined prompts
5. Compound improvement over time
```

### Implementation

**Phase A: Create domain activity prompts**

```bash
cd ~/ai-society/healthco/healthco-templates/copier/tpl-agent-repo/prompts/activities

# Create physiotherapy-specific prompt
cat > physiotherapy.md << 'EOF'
# Physiotherapy Activity

## Assessment Protocol
1. **Subjective**: Chief complaint, history, aggravating/relieving factors
2. **Objective**: ROM, strength, special tests, posture analysis
3. **Assessment**: Clinical impression, differential diagnosis
4. **Plan**: Treatment goals, interventions, frequency

## Red Flags (Immediate Referral)
- Cauda equina syndrome signs
- Unexplained weight loss + night pain
- Progressive neurological deficit
- Cancer history + new back pain

## Exercise Prescription Schema
- Exercise name
- Sets/reps/duration
- Frequency
- Progression criteria
- Contraindications

## Progress Tracking
- Pain scale (0-10) at rest/activity
- Functional outcome measures (ODI, NDI, DASH)
- Goal achievement rate
EOF
```

**Phase B: Learnings extraction script**

```bash
# In healthco-templates/scripts/
cat > extract-learnings-to-prompt.sh << 'EOF'
#!/bin/bash
# Extract patterns from agent learnings to improve domain prompts
# Usage: ./extract-learnings-to-prompt.sh agent-physiotherapist physiotherapy

AGENT=$1
DOMAIN=$2
LEARNINGS_DIR=~/ai-society/healthco/agents/$AGENT/docs/learnings
PROMPT_FILE=../copier/tpl-agent-repo/prompts/activities/$DOMAIN.md

if [ -d "$LEARNINGS_DIR" ]; then
  echo "## Agent Learnings ($(date -I))" >> "$PROMPT_FILE"
  echo "" >> "$PROMPT_FILE"
  for f in "$LEARNINGS_DIR"/*.md; do
    [ -f "$f" ] || continue
    echo "### $(basename "$f" .md)" >> "$PROMPT_FILE"
    cat "$f" >> "$PROMPT_FILE"
    echo "" >> "$PROMPT_FILE"
  done
  echo "Extracted learnings to $PROMPT_FILE"
fi
EOF
chmod +x extract-learnings-to-prompt.sh
```

### Why This Is Valuable

| Feature | Before | After |
|---------|--------|-------|
| New agent startup | Generic prompts | Domain-specific prompts |
| Knowledge accumulation | Lost in agent repos | Fed back to templates |
| Cross-agent learning | Manual copy | Automatic extraction |
| Template quality | Static | Evolving |

### Compound Value

```
Generation 1: agent-physiotherapist learns → physiotherapy.md created
Generation 2: New physiotherapist starts with v1 prompt, learns more → physiotherapy.md v2
Generation 3: Even better starting point, faster onboarding
...
Generation N: Highly refined domain expertise embedded in template
```

---

## P2: Document for softwareco

softwareco uses registry-style (separate L2 repos). Options:
1. Copy L0's tpl-* templates
2. Keep softwareco's domain-specific templates (tpl-owned-repo, tpl-contrib-repo, tpl-infra-repo)
3. Hybrid: Use L0 tpl-agent-repo, keep softwareco-specific project templates

---

## Verification Commands

```bash
# L0 validation
cd ~/ai-society/core/tpl-template-repo
bash ./scripts/check-l0.sh

# Test L1 -> L2 flow
./scripts/new-l1-from-copier.sh /tmp/test-l1 -d repo_slug=test --defaults --overwrite
cd /tmp/test-l1
./scripts/new-repo-from-copier.sh tpl-agent-repo /tmp/test-agent -d repo_slug=test-agent --defaults --overwrite
```

---

## Current Repo States

| Repo | Status | Notes |
|------|--------|-------|
| `core/tpl-template-repo` | ✅ | Embeds tpl-*-repo templates |
| `holdingco-templates` | ✅ | Source of truth for L0 |
| `healthco-templates` | ✅ | tpl-*-repo/ from L0 |
| `healthco/agents/agent-physiotherapist` | ⚠️ | Needs transition to new template |
| `healthco/agents/agent-psychotherapist` | ✅ | From healthco-templates |
| `healthco/agents/agent-nutritionist` | ✅ | From healthco-templates |
| `healthco/data/health-records` | ✅ | From tpl-project-repo |
| `softwareco-templates` | ✅ | Registry style |

---

## Action Priority

1. **P1.5**: Transition agent-physiotherapist (5 min)
2. **P3**: Add domain-specific activity prompts (30 min)
3. **P3**: Add learnings extraction script (15 min)
4. **P2**: Document softwareco integration (later)
