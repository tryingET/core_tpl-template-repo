# next_session_prompt.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Branch: `main`
- Working tree: **clean**
- HEAD: `0c3b682` (`feat(l0): add L1 provenance seal with l0_source_sha tracking`)
- Validation: **passes** (`bash ./scripts/check-l0.sh`)
- Remote: `origin/main` (6 commits behind local)

---

## What was completed this session

### 1) Merged L2 archetype/provenance work to main
- Merged `feat/l2-archetype-cutover-clean` (provenance seal + legacy guardrails)
- Cleaned up all backup/feature branches
- Removed stale `NEXT_SESSION_PROMPT.md`

### 2) Added `docs-list.sh` wrapper script
- Added at L0, L1, L2 template layers
- Delegates to shared `~/ai-society/core/agent-scripts/scripts/docs-list.mjs`
- Updated AGENTS.md files with "Shared tooling" section

### 3) Added L1 provenance seal (`l0_source_sha`)
- Added `l0_source_sha` parameter to L0 copier config
- Added `copier-template/contracts/provenance-seal.yml.jinja` for L1
- Updated L1 answers template to persist `l0_source_sha`
- Updated `new-l1-from-copier.sh` to inject L0 git SHA
- Updated L1 smoke.sh and check-template-ci.sh to validate provenance seal
- Synced fixtures

---

## Key discovery: holdingco-templates WS branch exists but unmerged

### The WS work (WS0-WS7) was already done but **NOT merged to main**

```
holdingco-templates-ws (worktree)
└── branch: feat/holdingco-ws1-policy-docs
    └── 8 commits AHEAD of main (NOT merged)
        ├── WS0: baseline stabilization
        ├── WS1: governance docs
        ├── WS2: guardrails in CI
        ├── WS3: script convergence
        ├── WS4: profile toggles
        ├── WS5: copier/template mirror consistency
        ├── WS6: drift reporting script
        └── WS7: pilot rollout plan
```

### Current repo states

| Repo | Branch | Status |
|------|--------|--------|
| `core/tpl-template-repo` | `main` | ✅ L0 origin, 6 commits ahead of origin |
| `holdingco-templates` | `main` | ⚠️ Behind WS branch by 8 commits |
| `holdingco-templates` | `issue-6-template-ci-smoke` | 🔄 Dirty working tree |
| `holdingco-templates-ws` | `feat/holdingco-ws1-policy-docs` | ✅ Has WS0-WS7, needs merge |

---

## Immediate next objectives (in order)

### Step 1: Review what's in WS branch (3)

Before merging, review the 8 commits on `feat/holdingco-ws1-policy-docs`:

```bash
cd ~/ai-society/holdingco/holdingco-templates-ws

# See commit summary
git log --oneline feat/holdingco-ws1-policy-docs --not main

# Review each workstream
git show 6babef6  # WS0: baseline
git show 6569576  # WS1: governance docs
git show 5970f70  # WS2: guardrails in CI
git show feb5bae  # WS3: script convergence
git show 9c3cd0d  # WS4: profile toggles
git show 20ad65a  # WS5: mirror consistency
git show cd25d65  # WS6: drift reporting
git show 151bf35  # WS7: pilot rollout
```

Key files to review:
- `docs/profile-governance-policy.md`
- `docs/l0-adoption-plan.md`
- `docs/l1-adoption-playbook.md`
- `docs/ws0-baseline-report.md`
- `docs/ws7-pilot-rollout-plan.md`
- `scripts/check-template-ci.sh` (changes)
- `scripts/new-repo-from-copier.sh` (changes)

### Step 2: Rebase WS branch on current main (2)

If `main` has moved since WS branch was created:

```bash
cd ~/ai-society/holdingco/holdingco-templates-ws
git fetch origin
git rebase origin/main

# Or if conflicts are complex, consider merge instead:
git merge origin/main
```

Resolve any conflicts, then validate:

```bash
bash ./scripts/check-template-ci.sh
```

### Step 3: Merge WS branch to main (1)

After review and rebase:

```bash
cd ~/ai-society/holdingco/holdingco-templates
git switch main
git pull --ff-only origin main
git merge feat/holdingco-ws1-policy-docs --no-ff
git push origin main

# Cleanup worktree if desired
git worktree remove ../holdingco-templates-ws
git branch -d feat/holdingco-ws1-policy-docs
```

---

## Background: Layer architecture (from docs)

```
L0 (core/tpl-template-repo)
  → defines baseline contracts and generation profiles
  → does NOT embed company-specific lane routing

L1 (<company>/<company>-templates)
  → hosts company-specific control plane (registry + resolver + policy overlay)
  → chooses company-specific lane sets
  → e.g., holdingco-templates, softwareco-templates

L2 (<company>/tpl-*-repo)
  → implements template products for selected lanes/archetypes
  → e.g., tpl-agent-repo, tpl-org-repo, tpl-project-repo

L3 (generated repos)
  → product repos generated from L2 templates
```

---

## Companies overview (current + future)

| Company | L1 repo | Status |
|---------|---------|--------|
| holdingco | `holdingco-templates` | WS branch ready to merge |
| softwareco | `softwareco-templates` | Different structure, no copier/ profiles yet |
| (future) | financeco, houseco, healthco, teachingco, etc. | Will need L1 from L0 |

---

## Verification commands

```bash
# L0 validation
cd ~/ai-society/core/tpl-template-repo
bash ./scripts/check-l0.sh

# holdingco-templates WS branch review
cd ~/ai-society/holdingco/holdingco-templates-ws
git log --oneline -10
cat docs/profile-governance-policy.md
bash ./scripts/check-template-ci.sh

# Preview L1 diff (after WS merge)
cd ~/ai-society/core/tpl-template-repo
./scripts/preview-l1-diff.sh ~/ai-society/holdingco/holdingco-templates
```

---

## Related docs

- `~/ai-society/holdingco/governance-kernel/docs/core/definitions/dream-model-stack.md` — L0→L1→L2→L3 placement
- `~/ai-society/holdingco/holdingco-templates-ws/docs/l0-adoption-plan.md` — Full WS0-WS7 plan
- `~/ai-society/core/tpl-template-repo/docs/profile-governance-policy.md` — Toggle bundles
- `~/ai-society/core/tpl-template-repo/docs/feature-matrix-l0-l1-l2-vs-pi-template.md` — Gap analysis

---

## Constraint reminders

- Keep recursion bounded: `L0 -> L1 -> L2 -> L3` only.
- No nested `copier copy` in `_tasks`.
- No direct commits to `main`; use topic branches + MRs (or merge commits).
- No secrets in git.
- Keep `.copier-answers.yml` committed in generated repos.
