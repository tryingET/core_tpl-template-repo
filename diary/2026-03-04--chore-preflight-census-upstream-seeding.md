# 2026-03-04 — Seed preflight repo-census helper upstream

## What I Did
- Added `scripts/preflight-repo-census.sh` at L0 for deterministic local fallback when `~/.pi/agent/scripts/preflight-repo-census.sh` is unavailable.
- Added matching L1 baseline copy at `copier-template/scripts/preflight-repo-census.sh`.
- Updated shared tooling docs:
  - `AGENTS.md` (L0) now references `./scripts/preflight-repo-census.sh [scope]`.
  - `copier-template/AGENTS.md.jinja` (L1 template) now references the same helper.
- Updated workspace guardrail note in `~/ai-society/AGENTS.md` to prefer local deterministic helpers when present.
- Validated script syntax (`bash -n`) and runtime output against tpl-template-repo.

## What Surprised Me
- Existing preflight flow depended on an external helper path that is not consistently present across environments.

## Patterns
- Small deterministic scripts in-repo reduce environment coupling and support source-first debugging.

## Crystallization Candidates
- → docs/learnings/: fallback-first preflight helper pattern
- → tips/meta/: standard preflight helper bundle for new template baselines
