# 2026-02-24 — Add fail-fast timeout control to check-l0

## What I Did
- Added per-subcheck timeout support to `scripts/check-l0.sh` via `L0_CHECK_TIMEOUT_SECONDS` (default: `180`, `0` disables timeout).
- Wrapped each check invocation with `timeout --preserve-status` when available.
- Added explicit timeout failure messaging (`timed out after ...`).
- Documented usage in `CONTRIBUTING.md` with a shorter example (`L0_CHECK_TIMEOUT_SECONDS=120`).
- Added L0 guardrail assertion to keep timeout docs in contributing guidance.

## What Surprised Me
- The apparent "stuck" experience was often a long-running subcheck with no fail-fast cap, not necessarily a deadlock.

## Patterns
- Reliability of orchestration scripts depends on bounded execution time as much as correctness checks.
- User-facing control-plane commands should expose quick fail-fast controls by default.

## Crystallization Candidates
- -> `docs/learnings/2026-02-24-check-orchestrators-need-fail-fast-timeout-controls.md`
- -> `tips/meta/` candidate: standard timeout env var convention across top-level check runners.
