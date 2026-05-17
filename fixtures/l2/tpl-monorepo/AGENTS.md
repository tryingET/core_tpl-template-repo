---
summary: "Agent operating contract for generated monorepositories."
read_when:
  - "Read when changing the generated tpl-monorepo AGENTS.md operating contract."
type: "reference"
---

# AGENTS.md — fixture-monorepo

## Intent
Template for a monorepo workspace (packages + apps + shared tooling).

## Structure
```
packages/        # Reusable libraries
apps/            # Deployable services/applications
tools/           # Shared tooling (if any)
docs/            # Documentation
ontology/        # ROCS ontology
governance/      # AK work-items projection, optional task-scope snapshots, policies
```

## Guardrails
- No secrets in git.
- Never push to `main`; MRs only.
- Treat `docs/_core/**` as immutable.
- Packages in `packages/` have NO `.git` (managed by monorepo).
- Apps in `apps/` have NO `.git` (managed by monorepo).
- If this repo ships `governance/work-items.json`, treat it as an AK projection via plain installed `ak`, not as the live authority.
- When explicit task scope is in play, author it in AK and freeze repo-consumption snapshots at the monorepo root; packages/apps do not create standalone AK task-scope files.

## AK-native route guardrails
- If this monorepo declares AK-native task, direction, or route authority, read the relevant AK task and route/open-frame status before inventing new work.
- Generic operator input such as `proceed` continues the active execution task when one exists; it does not authorize lifecycle closeout, source-owner mutation, publication, or knowledge promotion.
- Treat closeout/readiness rows as gate inputs, not lifecycle authorization.
- Treat docs, work-items JSON, task-scope snapshots, and direction explorer exports as projections unless the repo declares otherwise; AK DB remains runtime authority for AK tasks, direction, evidence, and decisions.
- Handoff instead of editing by convenience when facts belong to Prompt Vault, ROCS, Pi/runtime, KES, steward/publication, template propagation, Oracle/DSPx, or another repo.
- Prefer `docs/project/vision.md` as durable product direction where present and `docs/project/product_posture.md` as a product-maturity bridge, not a queue, roadmap, changelog, or execution authority.
- Do not revive SG/TG/OP markdown planning where AK-native direction authority is declared; legacy `strategic_goals.md`, `tactical_goals.md`, `operating_plan.md`, or `operational_plan.md` files are archive/projection only unless a repo-local owner decision explicitly says otherwise.

## Deterministic tooling policy (ROCS-first)
- Prefer `ak work-items <import|export|check> ...` for repo-local work-items projection operations.
- Prefer `ak task scope show|export ...` when explicit task scope is part of the slice.
- Prefer `./scripts/rocs.sh <args...>` before ad-hoc inline scripting.
- Use `./scripts/preflight-repo-census.sh [scope]` for shallow multi-repo status checks.
- For ontology/policy checks, use ROCS commands as the default execution path.
- Use inline Python only as an explicit escape hatch when no deterministic command exists.

## Package Management
- Package manager: **uv**
- Languages: Defined per-package in `packages/` and `apps/` (via tpl-package)
- Workspace config at root; packages inherit workspace settings.
- Keep the engineering contract explicit:
  - root `docs/engineering.local.md` records monorepo control-plane overrides
  - generated packages/apps should carry `policy/engineering-lane.json` + `docs/engineering.local.md`
  - package/app `policy/engineering-lane.json` is the source of truth for the declared upstream lane command

## Agent/operator prompts
- Repo-local commit workflow prompt lives at `.pi/prompts/commit.md`.
- Use monorepo-aware conventional commit scopes:
  - package-local changes -> package name
  - app-local changes -> app name
  - root-level changes -> `root`, `monorepo`, `ci`, `docs`, or `release`

## Knowledge Crystallization Flow

```
Session → diary/ (raw) → docs/learnings/ (crystallized) → TIPs (propagated)
```

**Knowledge that isn't crystallized is knowledge that will be re-learned the hard way.**

1. During work: Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
2. End of session: Extract patterns, decisions, learnings
3. Weekly: Promote to `docs/learnings/` and `docs/decisions/`
4. When pattern generalizes: Propose TIP

## Recursion policy (explicit)
Allowed:
- L1 -> L2 (this monorepo)

Forbidden:
- L1 -> L0
- L2 -> L1
- any cycle

## Read order
1) `docs/_core/`
2) `docs/org_context/`
3) `docs/engineering.local.md`
4) `governance/`
5) `ontology/`
6) `diary/`               ← recent work sessions
7) `packages/`            ← reusable libraries
8) `apps/`                ← deployable services
