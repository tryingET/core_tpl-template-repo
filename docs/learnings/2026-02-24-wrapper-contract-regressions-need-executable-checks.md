# 2026-02-24 — Wrapper contract regressions hide outside CI unless encoded

## Context
A follow-up deep review after supply-chain fixes found `scripts/preview-l1-diff.sh` passed the wrong positional args to `scripts/new-l1-from-copier.sh`.

## Evidence
- `new-l1-from-copier.sh` contract is `new-l1-from-copier.sh <dest-dir> [copier args...]`.
- `preview-l1-diff.sh` called it as:
  - `new-l1-from-copier.sh template-repo "$render_dir" ...`
- Repro: running `./scripts/preview-l1-diff.sh <target>` exited early with code `2` before rendering diff output.

## Pattern
Helper scripts can drift from wrapper contracts because contract violations are:
- not covered by the main generation checks,
- easy to miss in code review,
- only triggered when secondary utilities are executed.

## Guardrail
- Fixed invocation in `scripts/preview-l1-diff.sh` to pass render directory as first positional arg.
- Improved `preview-l1-diff.sh` default slug resolution to read `repo_slug` from target `.copier-answers.yml` before falling back to directory basename.
- Added L0 guardrail assertions in `scripts/check-l0-guardrails.sh` to lock this call + slug-inference contract.
- Added runtime coverage in `scripts/check-l0-generation.sh` (sample case) to execute `preview-l1-diff.sh` against a copied alias directory name, asserting clean no-diff output so wrapper + slug-resolution regressions fail deterministic checks.

## Propagation
- Propagated: `tips/meta/tip-0004-executable-wrapper-contract-guardrails.md`.
