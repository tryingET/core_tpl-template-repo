# 2026-02-24 — Check orchestrators need fail-fast timeout controls

## Context
Long-running aggregated checks can feel stuck and delay feedback loops.

## Evidence
- `scripts/check-l0.sh` previously had no per-subcheck timeout control.
- A user report flagged 1200s command budgets as too long for practical iteration.

## Pattern
Top-level check orchestrators should bound execution time per subcheck to avoid silent hangs and improve feedback cadence.

## Guardrail
- Added `L0_CHECK_TIMEOUT_SECONDS` to `scripts/check-l0.sh`:
  - default: `180`
  - `0` disables timeout behavior
- Uses `timeout --preserve-status` when available.
- Timeout failures are explicit in summary output.
- Documented usage in `CONTRIBUTING.md` and guarded via `scripts/check-l0-guardrails.sh`.

## Propagation
- Propagated: `tips/meta/tip-0006-fail-fast-timeout-conventions-for-check-runners.md`.
