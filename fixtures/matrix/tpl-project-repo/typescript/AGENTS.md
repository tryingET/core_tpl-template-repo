# AGENTS.md — fixture-project-typescript

## Intent
Template for a delivery project repo (project context + code + tests).

## Guardrails
- No secrets in git.
- Never push to `main`; MRs only.
- Treat `docs/_core/**` as immutable.
- Track deferred work in Agent Kernel; keep `governance/work-items.json` as the exported projection via `./scripts/ak.sh` (avoid ad-hoc TODO comments and manual JSON authority confusion).
- When explicit task scope is in play, author it in AK and freeze repo-consumption snapshots via `./scripts/ak.sh task scope show|export ...`; treat `governance/task-scopes/AK-*.snapshot.json` as AK exports, not hand-authored truth.

## Deterministic tooling policy (ROCS-first)
- Prefer `./scripts/ak.sh work-items <import|export|check> ...` for repo-local work-items projection operations.
- Prefer `./scripts/rocs.sh <args...>` before ad-hoc inline scripting.
- Use `./scripts/preflight-repo-census.sh [scope]` for shallow multi-repo status checks.
- For ontology/policy checks, use ROCS commands as the default execution path.
- Use inline Python only as an explicit escape hatch when no deterministic command exists.

## Stack contract
- If this repo ships a language-specific software pack, keep the stack contract explicit:
  - `policy/stack-lane.json` declares the upstream `tech-stack-core` lane reference and the executable retrieval command
  - `docs/tech-stack.local.md` records repo-local overrides on top of that lane contract
  - consult `policy/stack-lane.json` before invoking `tech-stack-core` directly; do not assume repo-local `lanes/` overrides exist

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
- L1 -> L2

Forbidden:
- L1 -> L0
- L2 -> L1
- any cycle

## Read order
1) `docs/_core/`
2) `docs/org_context/`
3) `docs/project/`
4) `docs/decisions/`
5) `docs/learnings/`
6) `diary/`               ← recent work sessions
7) `docs/system4d/`
