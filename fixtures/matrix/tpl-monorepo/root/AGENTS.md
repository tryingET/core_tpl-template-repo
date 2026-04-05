# AGENTS.md — fixture-monorepo-matrix

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
- If this repo ships `governance/work-items.json`, treat it as an AK projection via `./scripts/ak.sh`, not as the live authority.
- When explicit task scope is in play, author it in AK and freeze repo-consumption snapshots at the monorepo root; packages/apps do not create standalone AK task-scope files.

## Deterministic tooling policy (ROCS-first)
- Prefer `./scripts/ak.sh work-items <import|export|check> ...` for repo-local work-items projection operations.
- Prefer `./scripts/ak.sh task scope show|export ...` when explicit task scope is part of the slice.
- Prefer `./scripts/rocs.sh <args...>` before ad-hoc inline scripting.
- Use `./scripts/preflight-repo-census.sh [scope]` for shallow multi-repo status checks.
- For ontology/policy checks, use ROCS commands as the default execution path.
- Use inline Python only as an explicit escape hatch when no deterministic command exists.

## Package Management
- Package manager: **uv**
- Languages: Defined per-package in `packages/` and `apps/` (via tpl-package)
- Workspace config at root; packages inherit workspace settings.
- Keep the stack contract explicit:
  - root `docs/tech-stack.local.md` records monorepo control-plane overrides
  - generated packages/apps should carry `policy/stack-lane.json` + `docs/tech-stack.local.md`
  - package/app `policy/stack-lane.json` is the source of truth for the declared upstream lane command

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
3) `docs/tech-stack.local.md`
4) `governance/`
5) `ontology/`
6) `diary/`               ← recent work sessions
7) `packages/`            ← reusable libraries
8) `apps/`                ← deployable services
