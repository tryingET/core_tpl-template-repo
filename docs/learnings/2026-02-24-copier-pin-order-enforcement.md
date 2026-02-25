# 2026-02-24 — Pinned toolchain checks must verify execution order, not only string presence

## Context
A deep review of L0/L1 Copier wrappers found that both scripts advertised pinned Copier usage but selected bare `copier` before pinned `uv tool run` when both binaries were installed.

## Evidence
- `scripts/new-l1-from-copier.sh` and `copier-template/scripts/new-repo-from-copier.sh` had branch order: `uvx` -> `copier` -> `uv`.
- `scripts/check-supply-chain.sh` asserted pinned command literals but did not assert runtime precedence.
- Result: policy looked satisfied in CI while runtime could execute unpinned Copier in common environments.

## Pattern
Supply-chain drift can hide in control flow, not just command text.

If checks only validate “string exists,” wrappers can pass policy while choosing weaker branches at runtime.

## Guardrail
- Enforced deterministic branch order in wrappers:
  - `uvx --from copier==...`
  - `uv tool run --from copier==...`
  - bare `copier` fallback only when `uvx/uv` unavailable
- Added explicit warning on unpinned fallback path.
- Added line-order + fallback-warning assertions to `scripts/check-supply-chain.sh` so precedence regressions fail CI.
- Extended `copier-template/scripts/check-template-ci.sh` so generated L1 repositories enforce the same wrapper guarantees.
- Added L0 assertions in `scripts/check-l0-guardrails.sh` to ensure the L1 supply-chain checks remain encoded.
- Updated `docs/supply-chain-policy.md` to codify the exact order.

## Propagation
- Propagated: `tips/meta/tip-0004-executable-wrapper-contract-guardrails.md`.
