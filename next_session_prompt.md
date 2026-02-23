# next_session_prompt.md — `core/tpl-template-repo`

## State
- **Repo**: `~/ai-society/core/tpl-template-repo`
- **HEAD**: `8fdd6a3` (KES vision)
- **Validation**: ✅ passes

---

## What We Proved

**healthco was a TEST.** L0 → L1 → L2 flow works:
```
L0 (tpl-template-repo)
  → L1 (healthco-templates with embedded tpl-*-repo)
    → L2 (agents, projects)
```

Now: **Apply learnings to the real system.**

---

## The Architecture

```
┌─────────────────────────────────────────────────────┐
│                    L0: Universal                    │
│         core/tpl-template-repo                      │
│                                                     │
│  Embeds: tpl-agent-repo, tpl-org-repo,             │
│          tpl-project-repo                           │
│                                                     │
│  Receives: meta-TIPs from holdingco                 │
└───────────────────────┬─────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │holdingco│    │healthco │    │softwareco│
   │templates│    │templates│    │templates │
   │         │    │         │    │(REGISTRY)│
   │ Monolith│    │Monolith │    │ Policy  │
   └─────────┘    └─────────┘    └─────────┘
```

**Two patterns coexist:**
| Pattern | Templates | Best For |
|---------|-----------|----------|
| Monolith | Embedded in L1 | Small orgs (healthco) |
| Registry | Separate L2 repos | Large orgs (softwareco) |

---

## Next Actions

### 1. Feed healthco learnings to L0 (5 min)

What worked:
- Template structure (tpl-agent-repo has good docs/person/ structure)
- Scripts (new-repo-from-copier.sh works)
- Validation (check-l0.sh catches regressions)

What needs improvement:
- Domain prompts too generic (need TIPs)
- No learnings feedback loop (need KES)

```bash
# Sync L0 fixtures, ensure clean state
cd ~/ai-society/core/tpl-template-repo
bash ./scripts/check-l0.sh
```

### 2. Transition holdingco-templates (15 min)

**holdingco is strategic hub.** Must become L0-generated with TIPs.

```bash
# Generate from L0
cd ~/ai-society/core/tpl-template-repo
./scripts/new-l1-from-copier.sh ~/ai-society/holdingco/holdingco-templates-new \
  -d repo_slug=holdingco-templates \
  -d maintainer_handle=@holding-owner \
  --defaults --overwrite

# Add TIPs infrastructure
cd ~/ai-society/holdingco/holdingco-templates-new
mkdir -p tips/domain tips/meta tips/_templates governance metrics

# Swap
mv ~/ai-society/holdingco/holdingco-templates ~/ai-society/holdingco/holdingco-templates-old
mv ~/ai-society/holdingco/holdingco-templates-new ~/ai-society/holdingco/holdingco-templates
```

### 3. softwareco: ANALYZE FIRST ⚠️

**DO NOT refactor yet.** softwareco is different:

```
softwareco/
├── softwareco-templates/     ← POLICY only (not embedded templates)
│   └── docs/l2-registry.md   ← Maps lanes → separate template repos
│
├── tpl-agent-repo/           ← Separate L2 template
├── tpl-owned-repo/           ← NOT in L0!
├── tpl-contrib-repo/         ← NOT in L0!
├── tpl-infra-repo/           ← NOT in L0!
├── tpl-org-repo/             ← NOT in L0!
│
├── owned/                    ← Generated projects
├── contrib/
└── infra/
```

**Analysis needed before any changes:**

| Question | Why It Matters |
|----------|----------------|
| Which templates can come from L0? | tpl-agent-repo, tpl-org-repo might work |
| Which are domain-specific? | tpl-owned-repo, tpl-contrib-repo, tpl-infra-repo = software-specific |
| How does L0 → Registry pattern work? | L0 generates L1, L1 points to L2 template repos? |
| What's the TIPs flow? | Domain TIPs stay in softwareco, meta-TIPs escalate |

**Required analysis:**
```bash
# Read these BEFORE any refactor
cat ~/ai-society/softwareco/softwareco-templates/docs/lane-policy-matrix.md
cat ~/ai-society/softwareco/softwareco-templates/docs/l2-registry.md
ls -la ~/ai-society/softwareco/tpl-*-repo/
```

---

## KES: The Meta-Learning System

**TIPs = git commits to collective intelligence**

```
Agent learns → TIP with evidence → Review → Merge → All future agents benefit
```

**Escalation protocol:**
- Domain TIPs → Stay in L1 (physiotherapy protocol)
- Meta TIPs → Escalate to L0 (TIP process itself)

**holdingco role:** Strategic hub that decides what escalates.

---

## Decision Tree for Next Session

```
START
  │
  ├─ L0 clean? ─No─→ Fix validation
  │
  ├─Yes
  │
  ├─ holdingco L0-generated? ─No─→ Transition holdingco
  │                              │
  │                              └─ Add TIPs infrastructure
  │
  ├─Yes
  │
  ├─ softwareco analyzed? ─No─→ READ lane-policy-matrix.md
  │                           READ l2-registry.md
  │                           COMPARE tpl-*-repo/ vs L0
  │                           DOCUMENT findings
  │
  ├─Yes
  │
  └─ Apply learnings to L0 based on analysis
```

---

## Key Files

| File | Purpose |
|------|---------|
| `softwareco/softwareco-templates/docs/lane-policy-matrix.md` | Lane definitions |
| `softwareco/softwareco-templates/docs/l2-registry.md` | Registry pattern |
| `softwareco/tpl-*-repo/` | L2 templates (separate repos) |
| `holdingco-templates/copier/tpl-*-repo/` | Source for L0 (hand-crafted) |

---

## Commands

```bash
# Validate L0
cd ~/ai-society/core/tpl-template-repo && bash ./scripts/check-l0.sh

# Generate L1
./scripts/new-l1-from-copier.sh /path/to/company-templates --defaults --overwrite

# Generate L2 (from L1)
cd /path/to/company-templates
./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent-name -d repo_slug=agent-name --defaults --overwrite
```

---

## Summary

1. ✅ **Proved**: L0 → L1 → L2 works (healthco test)
2. 🔧 **Next**: Transition holdingco to L0-generated + TIPs
3. ⚠️ **Analyze**: softwareco BEFORE refactoring (different pattern)
4. 🌌 **Vision**: KES for self-improving AI civilization
