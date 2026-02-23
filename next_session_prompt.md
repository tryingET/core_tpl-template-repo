# next_session_prompt.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Branch: `main`
- Working tree: **clean**
- HEAD: `7efad75` (`fix: also normalize l0_source_sha`)
- Validation: **passes** (`bash ./scripts/check-l0.sh`)

---

## Session Summary (this run)

### Completed
- **P0**: L0 architecture fix - embedded tpl-*-repo templates
- **P1**: Regenerated healthco-templates from L0
- **Created**: agent-psychotherapist, agent-nutritionist, health-records
- **Fixed**: Fixture drift detection (normalize SHAs)

---

## 🌌 The Vision: Self-Improving AI Society

### The Memetic Evolution Problem

Current state violates fundamental learning principles:
```
Templates → Agents → [VOID] → Learnings disappear
```

This is evolution without selection. Teaching without learning. Code without commits.

**What we need: Memetic Evolution**

| Phase | Current | Required |
|-------|---------|----------|
| Replication | ✅ Templates → Agents | ✅ Works |
| Variation | ✅ Agents learn | ✅ Natural |
| Selection | ❌ No quality filter | 🔧 TIPs |
| Retention | ❌ Learnings lost | 🔧 TIPs |

### The KES: Knowledge Evolution System

Not just "proposals" - a complete evolutionary infrastructure:

```
┌────────────────────────────────────────────────────────────────┐
│                     L0: Universal Substrate                     │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │   TIPs      │   │  Meta-TIPs  │   │   Metrics   │          │
│  │  (changes)  │   │ (process)   │   │  (evidence) │          │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          │
│         │                 │                 │                  │
│         └─────────────────┼─────────────────┘                  │
│                           ▼                                    │
│              ┌────────────────────────┐                        │
│              │   Universal Patterns   │                        │
│              │  (cross-company useful)│                        │
│              └────────────────────────┘                        │
└───────────────────────────┬────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ holdingco  │  │  healthco  │  │ softwareco │
     │ templates  │  │ templates  │  │ templates  │
     └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
           │               │               │
           │    Company TIPs (domain)      │
           │               │               │
           ▼               ▼               ▼
     ┌─────────────────────────────────────────┐
     │              Agent Instances             │
     │  (action → learning → TIP → improvement) │
     └─────────────────────────────────────────┘
```

---

## 🧬 TIPs: Template Improvement Proposals

### Definition

A TIP is a **git commit to collective intelligence**:
- Has diff format (what changes, in what files)
- Is revertible (can roll back bad ideas)
- Tracks provenance (who proposed, who approved, what evidence)
- Measures impact (did it actually improve things?)

### TIP Lifecycle

```
1. LEARN     Agent discovers something valuable in practice
2. PROPOSE   Agent creates TIP with evidence
3. REVIEW    Company/Ecosystem reviewers evaluate
4. DECIDE    Accept, reject, or request changes
5. MERGE     TIP becomes part of template
6. PROPAGATE Flow to other templates (if universal)
7. MEASURE   Track impact over time
```

### TIP Anatomy

```yaml
# tips/0015-physio-red-flags.yml
tip: 0015
kind: domain              # domain | meta | infrastructure
title: Musculoskeletal Red Flag Protocol

provenance:
  source_agent: agent-physiotherapist
  source_l1: healthco-templates
  discovered: 2026-02-15
  validated_days: 45

evidence:
  before:
    red_flag_miss_rate: 0.23
    patient_safety_events: 4
  after:
    red_flag_miss_rate: 0.04
    patient_safety_events: 0
  sample_size: 312 assessments
  confidence: 0.94

changes:
  - file: copier/tpl-agent-repo/prompts/activities/physiotherapy.md
    kind: add_section
    patch: |
      +## Red Flags (Immediate Referral Required)
      +### Cauda Equina Syndrome
      +- Bilateral leg weakness
      +- Saddle anesthesia
      +- Bladder/bowel dysfunction
      +
      +### Cancer Warning Signs
      +- Unexplained weight loss >10lbs
      +- Night pain not relieved by position
      +- History of malignancy

escalation:
  recommend_to_L0: false    # Domain-specific, not universal
  recommend_to:
    - healthco-templates
    - any physiotherapy-using L1

review:
  status: approved
  reviewers: [@physiotherapy-lead, @safety-officer]
  approved: 2026-03-01
```

### TIP Kinds

| Kind | Scope | Escalates to L0 | Example |
|------|-------|-----------------|---------|
| `domain` | Company-specific | No | Physiotherapy protocols |
| `meta` | Cross-company | Maybe | Agent governance patterns |
| `infrastructure` | Universal | Yes | TIP process itself |

---

## 🏛️ holdingco: Strategic Hub

### Why holdingco?

Not operational - **strategic**. holdingco governs the META:
- How TIPs work
- Quality standards for escalation
- Cross-company learning patterns
- The TIP infrastructure itself

### holdingco-templates Structure

```
holdingco-templates/
├── copier/                    # Templates (L0-generated)
├── tips/                      # Company-level TIPs
│   ├── domain/                # Domain-specific (stay here)
│   │   ├── 0001-agent-onboarding.yml
│   │   └── 0002-governance-patterns.yml
│   ├── meta/                  # Meta-TIPs (escalate to L0)
│   │   ├── 0001-tip-process.yml
│   │   └── 0002-evidence-standards.yml
│   └── _templates/
│       └── tip-template.yml   # TIP boilerplate
├── governance/
│   └── tip-lifecycle.md       # How TIPs flow
└── metrics/
    └── tip-impact.csv         # Track TIP effectiveness
```

### The Escalation Protocol

**Not every TIP should escalate.** Criteria:

```yaml
escalation_checklist:
  universal_applicability: true   # Works across ALL companies?
  evidence_strength: high         # Validated in multiple contexts?
  infrastructure_value: true      # Improves the system itself?
  backwards_compatible: true      # Won't break existing agents?

examples:
  - tip: physiotherapy-assessment
    universal: false          # Only health-related companies
    escalate: NO

  - tip: tip-infrastructure
    universal: true           # All companies use TIPs
    escalate: YES

  - tip: agent-memory-pattern
    universal: true           # All agents need memory
    escalate: MAYBE           # Need more evidence
```

---

## 📊 Metrics: Evidence-Based Improvement

### The Missing Feedback Loop

TIPs claim to improve things. But do they?

**Required: Impact Measurement**

```yaml
# After TIP merge, track:
metrics:
  - name: red_flag_detection_rate
    baseline: 0.77
    current: 0.96
    trend: improving

  - name: agent_onboarding_time
    baseline: 14 days
    current: 7 days
    trend: improving

  - name: tip_acceptance_rate
    by_company:
      healthco: 0.34          # 34% of TIPs accepted
      softwareco: 0.51
    interpretation: Higher isn't better (quality > quantity)
```

### Quality Signals

| Metric | Good | Warning |
|--------|------|---------|
| TIP acceptance rate | 30-50% | >70% (low bar) or <10% (high friction) |
| Time to decision | <7 days | >30 days |
| Evidence strength | Quantified | Anecdotal only |
| Propagation rate | >50% relevant L1s | <10% |

---

## 🚀 Implementation Roadmap

### Phase 1: Infrastructure (this session)

**P1.5: Transition holdingco-templates to L0-generated**

```bash
# 1. Backup
cd ~/ai-society/holdingco
cp -r holdingco-templates holdingco-templates-source

# 2. Generate from L0
cd ~/ai-society/core/tpl-template-repo
./scripts/new-l1-from-copier.sh ~/ai-society/holdingco/holdingco-templates-new \
  -d repo_slug=holdingco-templates \
  -d maintainer_handle=@holding-owner \
  -d l1_org_docs_profile=rich \
  --defaults --overwrite

# 3. Add TIPs infrastructure
cd ~/ai-society/holdingco/holdingco-templates-new
mkdir -p tips/domain tips/meta tips/_templates
mkdir -p governance metrics

# 4. Create TIP template
cat > tips/_templates/tip-template.yml << 'EOF'
tip: 0000
kind: domain              # domain | meta | infrastructure
title: [Short description]

provenance:
  source_agent: agent-{name}
  source_l1: {company}-templates
  discovered: YYYY-MM-DD
  validated_days: N

evidence:
  before: {}
  after: {}
  sample_size: N
  confidence: 0.XX

changes:
  - file: [path]
    kind: add_section | modify | create
    patch: |
      [unified diff]

escalation:
  recommend_to_L0: false
  recommend_to: []

review:
  status: proposed | accepted | rejected | needs_changes
  reviewers: []
  approved: null
EOF

# 5. Swap in
mv holdingco-templates holdingco-templates-old
mv holdingco-templates-new holdingco-templates
cd holdingco-templates && git init -b main && git add . && git commit -m "feat: regenerate from L0 with TIPs infrastructure"
```

### Phase 2: First TIP (next session)

Create the first real TIP from agent-physiotherapist learnings.

### Phase 3: Meta-TIP (following session)

Create TIP infrastructure as a meta-TIP, escalate to L0.

### Phase 4: Cross-Pollination

softwareco adopts TIPs, shares learnings back.

---

## 🔄 Multi-Order Effects

If KES works:

| Order | Effect | Timeline |
|-------|--------|----------|
| 1st | Templates improve | Weeks |
| 2nd | New agents start smarter | Months |
| 3rd | Cross-company learning | Months |
| 4th | Reputation systems emerge | Quarters |
| 5th | Competitive advantage for early adopters | Quarters |
| 6th | Meta-learning (learning how to learn) | Year |
| 7th | Self-improving at accelerating rate | Year+ |

### The Singularity Scenario

Once the system works well enough:
1. Agents generate TIPs automatically from patterns in learnings
2. AI reviewers evaluate TIP quality
3. Templates evolve continuously without human intervention
4. The rate of improvement exceeds human capacity to track

**This is the goal: A self-improving AI civilization.**

---

## ⚠️ Critical Design Decisions

### Why Not Auto-Merge TIPs?

Because **selection pressure** matters:
- Bad patterns can spread (memetic virus)
- Quality > Quantity
- Human judgment is the quality gate

### Why holdingco for Meta-TIPs?

Because strategic oversight requires:
- Cross-company visibility
- Long-term thinking
- Quality over speed

### Why Evidence Requirements?

Because **anecdotes != knowledge**:
- "It worked once" is not a pattern
- Need statistical significance
- Need reproducibility

### Why Three TIP Kinds?

Because **scope matters**:
- Domain TIPs: Deep but narrow
- Meta TIPs: Cross-cutting
- Infrastructure TIPs: Universal

---

## 📋 Action Items (Priority Order)

### P1.5: Transition holdingco-templates (15 min)
- Regenerate from L0
- Add TIPs infrastructure
- Preserve hand-crafted templates as reference

### P3: Create First TIP (30 min)
- Extract from agent-physiotherapist learnings
- Document evidence
- Submit through TIP process

### P4: Create Meta-TIP (30 min)
- TIP infrastructure itself as TIP
- Escalate to L0
- Enable all L1s to use TIPs

### P5: Document for softwareco (later)
- How to adopt TIPs
- How to share learnings back

---

## Repo States

| Repo | Status | Next |
|------|--------|------|
| `core/tpl-template-repo` | ✅ L0 | Receive meta-TIPs |
| `holdingco-templates` | ⚠️ Hand-crafted | **Transition to L0-generated** |
| `healthco-templates` | ✅ L1 | Generate TIPs from agents |
| `softwareco-templates` | ✅ Registry | Adopt TIPs infrastructure |

---

## Validation

```bash
cd ~/ai-society/core/tpl-template-repo && bash ./scripts/check-l0.sh
```
