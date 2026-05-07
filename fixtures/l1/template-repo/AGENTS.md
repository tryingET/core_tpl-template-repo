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

## AK-native route guardrails
- In repos that declare AK-native task, direction, or route authority, read the relevant AK task and route/open-frame status before inventing new work.
- Generic operator input such as `proceed` continues the active execution task when one exists; it does not authorize lifecycle closeout, source-owner mutation, publication, or knowledge promotion.
- Treat closeout/readiness rows as gate inputs, not lifecycle authorization.
- Treat docs, work-items JSON, task-scope snapshots, and direction explorer exports as projections unless the repo declares otherwise; AK DB remains runtime authority for AK tasks, direction, evidence, and decisions.
- Handoff instead of editing by convenience when facts belong to Prompt Vault, ROCS, Pi/runtime, KES, steward/publication, template propagation, Oracle/DSPx, or another repo.
- Prefer `docs/project/vision.md` as durable product direction where present and `docs/project/product_posture.md` as a product-maturity bridge, not a queue, roadmap, changelog, or execution authority.
- Do not revive SG/TG/OP markdown planning where AK-native direction authority is declared; legacy `strategic_goals.md`, `tactical_goals.md`, `operating_plan.md`, or `operational_plan.md` files are archive/projection only unless a repo-local owner decision explicitly says otherwise.

## Shared tooling
- Docs discovery: `./scripts/docs-list.sh --task "<task>" --top 8`
- AK CLI: `ak <ak args...>` (canonical operator path for repo-local AK work-items projection and task-scope snapshot flows when in scope)
- ROCS launcher: `./scripts/rocs.sh <rocs args...>`
- New L2 repo: `./scripts/new-repo-from-copier.sh <template> <dest> -d repo_slug=<slug> --defaults`
- Lane bootstrap: `./scripts/bootstrap-lane-root.sh <lane> [--init-lane-git]`

## Deterministic tooling policy (ROCS-first)
- Prefer `ak work-items <import|export|check> ...` when repo-local work-items projection is in scope.
- When explicit task scope is in scope, author it in AK and freeze repo-consumption snapshots via `ak task scope show|export ...`; treat hand-authored `governance/task-scopes/AK-*.json` files as transitional, not authoritative.
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

Do not reuse reserved L1 control-plane paths such as `docs`, `scripts`, `copier`, `governance`, `policy`, or `ontology` as lane names.

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
