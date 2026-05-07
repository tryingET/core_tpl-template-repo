---
summary: "2026-04-05 — Check runners need heavy-lane budgets and timeout aborts."
read_when:
  - "Read when you need 2026-04-05 — check runners need heavy-lane budgets and timeout aborts."
type: "reference"
---

# 2026-04-05 — Check runners need heavy-lane budgets and timeout aborts

## Context
A single uniform timeout budget on `scripts/check-l0.sh` was becoming too tight for the heaviest lane (`check-l0-generation`) as the L0 validation stack grew. Slow runners then risked timing out a legitimate long-running lane even when lighter checks were still well within budget.

## Evidence
- `scripts/check-l0.sh` now resolves `timeout` or `gtimeout` so timeout enforcement is less host-fragile.
- The orchestrator keeps one base timeout (`L0_CHECK_TIMEOUT_SECONDS`) but gives `check-l0-generation` a larger default budget while still allowing explicit overrides.
- Timeout failures remain hard failures; they are not downgraded to warnings or skips.
- After a timeout, the runner now aborts remaining checks and records them as skipped-after-timeout, which saves slow-runner time without creating a false green.
- Each run now prints the effective timeout policy so operators can see the budgets and timeout runner in use.

## Pattern
Mixed-cost validation suites should not assume every subcheck deserves the same wall-clock budget.

The safe pattern is:
1. keep timeout behavior explicit,
2. budget heavier lanes more honestly,
3. fail hard on timeout,
4. stop running later heavyweight checks once timeout has already made the aggregate result fail.

## Guardrail
For future aggregated validation runners:
- prefer per-lane timeout budgets over a single uniform budget when runtime skew becomes obvious,
- keep timeout failures fail-closed,
- show the effective timeout policy up front,
- and abort remaining expensive checks after a timeout instead of spending more runtime on an already-failed aggregate lane.
