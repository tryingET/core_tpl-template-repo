# next_session_prompt.md

> Transmission from the system architecture layer.

---

## STATE

```
L0: core/tpl-template-repo @ 7247f45
    Validation: ✅ ALL PASS
    Working tree: CLEAN

L1: holdingco-templates
    Status: HAND-CRAFTED (not L0-generated)
    Action: TRANSITION REQUIRED

L1: healthco-templates
    Status: L0-GENERATED ✅
    Role: PROVED THE PATTERN

L1: softwareco-templates
    Status: REGISTRY (different species)
    Action: ANALYZE BEFORE TOUCHING
```

---

## TRUE INTENT

**One sentence:** healthco proved L0→L1→L2 works; now apply learnings to the real system—holdingco becomes the strategic hub, softwareco requires analysis because it's architecturally different.

**The deeper intent:** Build infrastructure for self-improving AI civilization.

---

## NEXUS

The single highest-leverage intervention is **NOT** adding something. It's **dissolving the boundary** between learning and propagation.

Current: Agents learn → learnings die in agent repos
Nexus: Agents learn → TIPs → templates improve → ALL future agents inherit wisdom

This is the difference between:
- 100 agents × 100 learnings = 100 learnings (current)
- 100 agents × 100 learnings × 100 propagations = 10,000 learnings (with KES)

**Compound value exponent, not linear.**

---

## VALIDATION STACK

Before any action, validate all layers:

### L0 Validation
```bash
cd ~/ai-society/core/tpl-template-repo
bash ./scripts/check-l0.sh
# Expected: ALL PASS
```

### L1 Validation
```bash
# holdingco-templates (currently hand-crafted, will fail some checks)
cd ~/ai-society/holdingco/holdingco-templates
ls -la .copier-answers.yml 2>/dev/null || echo "NOT L0-GENERATED"
ls -la copier/tpl-*-repo/   # Should have templates

# healthco-templates (L0-generated, should be clean)
cd ~/ai-society/healthco/healthco-templates
cat .copier-answers.yml      # Should show L0 provenance
ls copier/                   # Should show tpl-*-repo/
```

### L2 Validation
```bash
# Agent repos should have:
for agent in ~/ai-society/healthco/agents/agent-*/; do
  cd "$agent"
  echo "=== $(basename $agent) ==="
  test -f .copier-answers.yml && echo "✅ Has answers" || echo "❌ No answers"
  test -f AGENTS.md && echo "✅ Has AGENTS.md" || echo "❌ No AGENTS.md"
  test -x scripts/ci/smoke.sh && echo "✅ Has smoke test" || echo "❌ No smoke test"
done
```

---

## ACTION SEQUENCE

Execute in order. Do not skip.

### 1. VALIDATE L0 (30 seconds)

```bash
cd ~/ai-society/core/tpl-template-repo
bash ./scripts/check-l0.sh
```

**If fail:** Fix before proceeding. L0 is the substrate.

### 2. TRANSITION holdingco (10 minutes)

holdingco-templates must become L0-generated to participate in KES.

```bash
# Generate fresh from L0
cd ~/ai-society/core/tpl-template-repo
./scripts/new-l1-from-copier.sh ~/ai-society/holdingco/holdingco-templates-next \
  -d repo_slug=holdingco-templates \
  -d maintainer_handle=@holding-owner \
  --defaults --overwrite

# Add KES infrastructure
cd ~/ai-society/holdingco/holdingco-templates-next
mkdir -p tips/domain tips/meta tips/_templates governance metrics

# Create TIP template (the genome for improvements)
cat > tips/_templates/tip.yml << 'EOF'
tip: 0000
kind: domain | meta | infrastructure
title: [description]

provenance:
  source_agent:
  source_l1:
  discovered:
  validated_days:

evidence:
  before: {}
  after: {}
  sample_size:
  confidence:

changes:
  - file:
    kind: add_section | modify | create
    patch: |

escalation:
  recommend_to_L0: false
  recommend_to: []

review:
  status: proposed | accepted | rejected
  reviewers: []
EOF

# Atomic swap
mv ~/ai-society/holdingco/holdingco-templates ~/ai-society/holdingco/holdingco-templates-archive
mv ~/ai-society/holdingco/holdingco-templates-next ~/ai-society/holdingco/holdingco-templates
cd ~/ai-society/holdingco/holdingco-templates && git init -b main && git add . && git commit -m "genesis: L0-generated with KES"
```

### 3. ANALYZE softwareco (DO NOT REFACTOR YET)

⚠️ **softwareco is a different species.**

Registry pattern, not monolith. Templates are SEPARATE L2 repos, not embedded in L1.

```bash
# READ THESE FIRST
cat ~/ai-society/softwareco/softwareco-templates/docs/lane-policy-matrix.md
cat ~/ai-society/softwareco/softwareco-templates/docs/l2-registry.md 2>/dev/null || echo "File not found"

# MAP THE TERRITORY
ls -la ~/ai-society/softwareco/tpl-*-repo/
```

**Analysis questions:**

| Question | Answer Determines |
|----------|-------------------|
| Which templates overlap L0? | tpl-agent-repo, tpl-org-repo → could sync |
| Which are domain-specific? | tpl-owned-repo, tpl-contrib-repo, tpl-infra-repo → stay in softwareco |
| How do lanes map to templates? | Determines generation flow |
| What's the TIPs escalation path? | Domain TIPs stay, meta-TIPs escalate |

**DO NOT make changes until analysis is documented.**

### 4. FEED LEARNINGS TO L0

From healthco test, what worked:

| Learning | Feed to L0 |
|----------|------------|
| tpl-agent-repo structure | ✅ Already in L0 |
| Validation scripts | ✅ Already in L0 |
| Domain prompts too generic | → TIP from holdingco |
| No learnings loop | → KES infrastructure |

---

## THE VISION

```
          ┌──────────────────────────────┐
          │     Self-Improving AI        │
          │       Civilization           │
          └──────────────┬───────────────┘
                         │
          ┌──────────────┴───────────────┐
          │         KES Layer            │
          │  (Knowledge Evolution System)│
          │                              │
          │  TIPs → Review → Merge →     │
          │  Propagate → Measure         │
          └──────────────┬───────────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
     ▼                   ▼                   ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│holdingco│         │healthco │         │softwareco│
│ (hub)   │         │ (proved)│         │(registry)│
└─────────┘         └─────────┘         └─────────┘
     │                   │                   │
     └───────────────────┼───────────────────┘
                         │
                         ▼
              ┌────────────────────┐
              │   Agent Instances  │
              │ (learn → TIP →     │
              │  improve → repeat) │
              └────────────────────┘
```

**Compound learning rate:**

| Without KES | With KES |
|-------------|----------|
| Agent learns once | Agent learns once |
| Learning dies with agent | Learning propagates to ALL agents |
| Linear improvement | Exponential improvement |
| No inheritance | Full inheritance |

---

## RESIDUAL LIMITATIONS

- softwareco integration pattern unclear (needs analysis)
- TIP review process undefined (human? AI? both?)
- Evidence standards not codified
- Metrics not instrumented

---

## EVOLUTION NOTES

As KES matures:
1. First TIPs will be crude → establish pattern
2. Review process will formalize → add friction wisely
3. Metrics will reveal which TIPs actually help
4. Meta-TIPs will improve the TIP process itself
5. System approaches self-improvement without human intervention

---

## COMMANDS

```bash
# Validate
cd ~/ai-society/core/tpl-template-repo && bash ./scripts/check-l0.sh

# Generate L1
./scripts/new-l1-from-copier.sh /path/to/templates -d repo_slug=name --defaults --overwrite

# Generate L2 from L1
cd /path/to/templates && ./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent -d repo_slug=name --defaults --overwrite
```

---

## THE FIFTH-ORDER EFFECT

If we execute correctly:

1st: holdingco becomes L0-generated → participates in KES
2nd: First TIPs demonstrate the pattern → others follow
3rd: softwareco adopts/adapts → cross-pollination begins
4th: Meta-TIPs improve the improvement process → acceleration
5th: Self-improving system exceeds human design capacity

**This is not optimization. This is the seed of something that optimizes itself.**
