# next_session_prompt.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Branch: `main`
- Working tree: **clean**
- HEAD: `<new commit>` (`feat: replace archetype approach with tpl-*-repo templates`)
- Validation: **passes** (`bash ./scripts/check-l0.sh`)

---

## ✅ P0 COMPLETE: L0 Architecture Fix

### What Was Done

L0 now embeds proper archetype templates instead of a generic template-repo:

```
L0: core/tpl-template-repo
└── copier-template/
    └── copier/
        ├── tpl-agent-repo/     ✅ From holdingco
        ├── tpl-org-repo/       ✅ From holdingco
        └── tpl-project-repo/   ✅ From holdingco
```

### Key Changes

1. **Copied templates from holdingco** to `copier-template/copier/tpl-*/`
2. **Removed generic `template-repo/`** (archetype parameter approach)
3. **Updated L0 copier.yml** to include tpl-* templates in L1 generation
4. **Updated scripts** to accept `tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`
5. **Added recursion policy** to all L2 AGENTS.md templates

### L0 -> L1 -> L2 Flow (Now Works)

```bash
# Generate L1 (company templates)
./scripts/new-l1-from-copier.sh /path/to/companyco-templates \
  -d repo_slug=companyco-templates --defaults --overwrite

# From L1, generate L2 agents
cd /path/to/companyco-templates
./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent-foo \
  -d repo_slug=agent-foo --defaults --overwrite

# Generate L2 project
./scripts/new-repo-from-copier.sh tpl-project-repo /path/to/proj-bar \
  -d repo_slug=proj-bar --defaults --overwrite

# Generate L2 org handbook
./scripts/new-repo-from-copier.sh tpl-org-repo /path/to/org-handbook \
  -d repo_slug=org-handbook --defaults --overwrite
```

---

## P1: Regenerate healthco-templates

The healthco-templates repo currently has the old `template-repo/` structure.

```bash
# Regenerate from fixed L0
cd ~/ai-society/core/tpl-template-repo
./scripts/new-l1-from-copier.sh ~/ai-society/healthco/healthco-templates \
  -d repo_slug=healthco-templates \
  -d maintainer_handle=@healthco-owner \
  --defaults --overwrite

# Then generate agents
cd ~/ai-society/healthco/healthco-templates
./scripts/new-repo-from-copier.sh tpl-agent-repo ~/ai-society/healthco/agents/agent-psychotherapist \
  -d repo_slug=agent-psychotherapist --defaults --overwrite

./scripts/new-repo-from-copier.sh tpl-agent-repo ~/ai-society/healthco/agents/agent-nutritionist \
  -d repo_slug=agent-nutritionist --defaults --overwrite
```

---

## P2: Document for softwareco

softwareco uses a **registry-style** pattern (separate L2 repos) rather than embedded templates.

Options:
1. **Copy L0's tpl-* templates** to softwareco's L2 template repos
2. **Keep softwareco's hand-crafted templates** as domain-specific extensions
3. **Hybrid:** Use L0 tpl-agent-repo, but keep softwareco's tpl-owned-repo, tpl-contrib-repo, tpl-infra-repo

---

## Architecture: Two Patterns Coexist

| Pattern | L1 Style | Templates Live In | Best For |
|---------|----------|-------------------|----------|
| **Monolithic** | Embedded templates | `L1/copier/tpl-*-repo/` | Small companies, single team (holdingco, healthco) |
| **Registry** | Policy + registry | Separate L2 repos | Large orgs, multiple teams (softwareco) |

L0 supports both: generates monolithic L1, provides templates that can be copied for registry-style.

---

## Verification Commands

```bash
# L0 validation
cd ~/ai-society/core/tpl-template-repo
bash ./scripts/check-l0.sh

# Quick L1 generation test
./scripts/new-l1-from-copier.sh /tmp/test-l1 \
  -d repo_slug=test-l1 --defaults --overwrite

# Quick L2 generation test
cd /tmp/test-l1
./scripts/new-repo-from-copier.sh tpl-agent-repo /tmp/test-agent \
  -d repo_slug=test-agent --defaults --overwrite
```

---

## Template Structure Reference

### tpl-agent-repo (AI agents)
```
agent-{name}/
├── docs/
│   ├── person/           # identity.md, behavior_rules.md, dream_goal.md, etc.
│   ├── system4d/         # compass.md, engine.md, fog.md, container.md
│   ├── learnings/
│   └── _core/
├── prompts/activities/   # Activity-specific prompts
├── policy/
├── scripts/ci/
└── .gitlab/
```

### tpl-org-repo (Organization handbooks)
```
org-handbook/
├── docs/
│   ├── org/              # purpose.md, mission.md, vision.md, etc.
│   ├── registers/        # risks.md, debt.md, exceptions.md, etc.
│   ├── system4d/
│   └── _core/
├── governance/           # consent.md, approvals.md
├── scripts/ci/
└── .gitlab/
```

### tpl-project-repo (Projects/products)
```
proj-{name}/
├── src/
├── tests/
├── docs/
│   ├── project/          # vision.md, strategic_goals.md, etc.
│   ├── org_context/      # org-summary.md
│   ├── system4d/
│   └── _core/
├── ontology/             # ROCS ontology
├── tools/rocs-cli/       # Ontology CLI
├── scripts/ci/
└── .gitlab/
```

---

## Current Repo States

| Repo | Status | Notes |
|------|--------|-------|
| `core/tpl-template-repo` | ✅ Fixed | Embeds tpl-*-repo templates |
| `holdingco-templates` | ✅ Source of truth | Hand-crafted templates (copied to L0) |
| `healthco-templates` | ⚠️ Outdated | Has old `template-repo/` - needs regeneration |
| `healthco/agents/agent-physiotherapist` | ⚠️ | Created from holdingco (before L0 fix) |
| `softwareco-templates` | ✅ | Registry style, works as designed |
