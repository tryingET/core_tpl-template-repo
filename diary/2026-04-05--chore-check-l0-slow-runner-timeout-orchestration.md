# 2026-04-05 — Tune check-l0 timeout orchestration for slower runners

## What I Did
- Updated `scripts/check-l0.sh` so timeout enforcement resolves `timeout` or `gtimeout` instead of assuming one host binary.
- Split the effective timeout budget so `check-l0-generation` gets a larger default wall-clock cap than the lighter subchecks.
- Kept timeout failures fail-closed and changed orchestration so later checks are skipped after a timeout instead of burning more slow-runner time.
- Added timeout-policy summary output so each run shows the effective per-check budgets and timeout runner.
- Verified the new timeout path with `L0_CHECK_TIMEOUT_SECONDS=1 bash ./scripts/check-l0.sh` and re-ran focused validation for generation/adversarial/fixtures.

## What Surprised Me
- The biggest runtime risk is not the aggregate command but one heavy lane (`check-l0-generation`) sitting close to the old generic timeout budget.
- The full `check-l0.sh` gate is currently blocked by unrelated docs-reference drift for managed launcher-bundle receipt paths, so task-local validation had to stay focused on the orchestrator slice.

## Patterns
- Aggregated check runners need heavier budgets for the few lanes that render or simulate whole repos; uniform per-check caps age poorly as coverage grows.
- Once a timeout happens on a slow runner, continuing into later heavyweight checks usually adds latency rather than signal.
- Timeout handling must stay fail-closed; the safe optimization is "abort remaining work after timeout," not "downgrade timeout to warning."

## Crystallization Candidates
- → docs/learnings/2026-04-05-check-runners-need-heavy-lane-budgets-and-timeout-aborts.md
- → future tip if more repos adopt aggregated check orchestrators with mixed-cost subchecks
