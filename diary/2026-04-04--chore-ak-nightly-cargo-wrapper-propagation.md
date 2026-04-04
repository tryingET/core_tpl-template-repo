# 2026-04-04 — Propagate nightly cargo operator wrapper before main merge

## What I Did
- Ran `bash ./scripts/check-l0.sh` as the pre-merge validation gate.
- Validation exposed non-idempotent L0 -> L1 generation for the AK wrapper chain.
- Propagated the generated `scripts/cargo-operator.sh` wrapper and the corresponding `scripts/ak.sh` updates across the repo root, `copier-template/`, and the checked-in fixtures.
- Re-ran `bash ./scripts/check-l0.sh` and confirmed the full L0 gate passed cleanly.
- Prepared the branch for a fast-forward merge into `main`.

## What Surprised Me
- The branch was clean before validation, but the generation check surfaced uncommitted wrapper propagation drift immediately.
- The missing propagation affected both template outputs and fixture mirrors, not just one layer.

## Patterns
- Template-chain changes to repo-local operator wrappers need an explicit propagation pass before merge.
- `check-l0-generation` remains the fastest signal for L0/L1 idempotency regressions.

## Crystallization Candidates
- → docs/learnings/ if the nightly cargo wrapper pattern expands beyond AK launchers.
- → scripts/ if wrapper propagation ever needs a dedicated one-shot sync helper.
