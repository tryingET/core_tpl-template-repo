# AGENTS.md — Holding Company (holdingco)

## Intent
Coordinate Holding Company work across explicit lanes:
- `owned/` (we operate)
- `contrib/` (upstream-coupled)
- `infra/` (platform/runbooks)
- `agents/` (AI agent repos)

## Guardrails
- No direct pushes to `main`; branch + MR workflow.
- Pick lane first, then follow lane policy and template contract.
- No secrets in git.
- Keep `.copier-answers.yml` committed in all repos.

## Shared tooling
- Docs discovery: `./scripts/docs-list.sh --task "<task>" --top 8`
- ROCS launcher: `./scripts/rocs.sh <rocs args...>`
- New L2 repo: `./scripts/new-repo-from-copier.sh <template> <dest> -d repo_slug=<slug> --defaults`
- Lane bootstrap: `./scripts/bootstrap-lane-root.sh <lane> [--init-lane-git]`

## Deterministic tooling policy (ROCS-first)
- Prefer `./scripts/rocs.sh <args...>` before ad-hoc inline scripting.
- For ontology/policy checks, use ROCS commands as the default execution path.
- Use inline Python only as an explicit escape hatch when no deterministic command exists.

## L2 Templates (in copier/)

| Template | Purpose | Generates |
|----------|---------|-----------|
| `copier/tpl-project-repo/` | Delivery projects | `owned/<project>/` |
| `copier/tpl-agent-repo/` | AI agent repositories | `agents/agent-<slug>/` |
| `copier/tpl-org-repo/` | Organization handbooks | `<org>-handbook/` |
| `copier/tpl-monorepo/` | Monorepo workspaces | `<monorepo>/` (packages + apps) |
| `copier/tpl-package/` | Packages inside monorepos | `packages/<name>/` (NO .git) |

## Lane root bootstrap (before nesting child repos)

Use this two-phase sequence so lane roots track baseline control-plane files while child repos remain ignored:

```bash
# 1) Materialize lane baseline in the parent repo
./scripts/bootstrap-lane-root.sh owned

# 2) Commit lane baseline in parent repo
git add .gitignore owned
git commit -m "chore: bootstrap owned lane baseline"

# 3) Initialize lane-root git repo
./scripts/bootstrap-lane-root.sh owned --init-lane-git
```

For custom lanes (example: `data`), use the same flow:

```bash
./scripts/bootstrap-lane-root.sh data
git add .gitignore data
git commit -m "chore: bootstrap data lane baseline"
./scripts/bootstrap-lane-root.sh data --init-lane-git
```

## Creating L2 repos

```bash
# Project
./scripts/new-repo-from-copier.sh tpl-project-repo ./owned/<project> \
  -d repo_slug=<project> --defaults --overwrite

# Agent
./scripts/new-repo-from-copier.sh tpl-agent-repo ./agents/agent-<slug> \
  -d repo_slug=agent-<slug> --defaults --overwrite

# Org handbook
./scripts/new-repo-from-copier.sh tpl-org-repo ./<org>-handbook \
  -d repo_slug=<org>-handbook --defaults --overwrite
```

## Placement reminders
- owned: `~/ai-society/holdingco/owned/<repo>`
- contrib: `~/ai-society/holdingco/contrib/<upstream>/<repo>`
- infra: `~/ai-society/holdingco/infra/<repo>`
- agents: `~/ai-society/holdingco/agents/agent-<slug>`

## Read order (high signal)
1. `./docs/lane-policy-matrix.md` (if exists)
2. `./docs/repo-placement-policy.md` (if exists)
3. `./docs/archetype-lane-crosswalk.md` (if exists)

## Knowledge Crystallization Flow

```
Session → diary/ (raw) → docs/learnings/ (crystallized) → TIPs (propagated)
```

1. During work: Capture in project's `diary/YYYY-MM-DD--type-scope-summary.md`
2. End of session: Extract patterns, decisions, learnings
3. Weekly: Promote to `docs/learnings/` and `docs/decisions/`
4. When pattern generalizes: Propose TIP to this L1

## Recursion policy
Allowed:
- `L0 -> L1` (this repo)
- `L1 -> L2` (projects in owned/, contrib/, infra/, agents/)

Forbidden:
- `L1 -> L0`
- `L2 -> L1`
- any cycle
