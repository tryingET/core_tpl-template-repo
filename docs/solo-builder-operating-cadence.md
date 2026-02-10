# Solo-builder operating cadence (family-safe)

## Purpose
Sustain long-horizon delivery for AI Society without burnout or family-context drift.

## Cadence
- **Daily (30 min):** triage + commit to max 1 active technical goal.
- **Weekly (60–90 min):** review backlog by Importance/Urgency and prune scope.
- **Monthly (90 min):** architecture + risk review (recursion, supply chain, drift, recovery).

## WIP limits
- Max **1 Q1 engineering stream** in flight.
- Max **1 Q2 design stream** in parallel.
- Pause new work if validation scripts are red.

## Stop-the-line triggers
- L0 guardrail checks fail.
- Template idempotency fails.
- Consent/change-control policy mismatch across L0/L1 docs.

## Recovery loop
1. Stabilize by passing `bash ./scripts/check-l0.sh`.
2. Capture root cause in a short ADR/log note.
3. Resume roadmap only after red checks are closed.
