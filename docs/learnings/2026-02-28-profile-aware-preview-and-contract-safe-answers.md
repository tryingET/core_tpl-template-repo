# Profile-Aware Preview and Contract-Safe Answers Parsing

**Discovered**: 2026-02-28
**Source**: Deep review + targeted reproductions in tpl-template-repo
**Confidence**: High

## Context
`preview-l1-diff.sh` was intended as a non-destructive adoption comparator, and L1->L2 generation inherited defaults from `.copier-answers.yml`.

## Evidence
- Preview diffs were noisy/false-positive for non-default profiles because re-render only supplied `repo_slug` and ignored other target answers.
- Inherited strings containing `:` (for example `company_name: Foo: Labs`) were truncated due to `awk -F':'` parsing.
- Preview comparisons included `.git/`, creating irrelevant churn in diffs for git-initialized targets.

## Pattern
Treating `.copier-answers.yml` as loosely parsed text causes contract drift and misleading tooling output.

## Guardrail
- `scripts/preview-l1-diff.sh` now rehydrates key profile/toggle inputs from target answers and compares normalized trees excluding `.git/`.
- `copier-template/scripts/new-repo-from-copier.sh` now parses inherited keys with key-prefix stripping instead of `awk -F':'`.
- `scripts/check-l0-generation.sh` now includes:
  - release-profile preview no-diff regression
  - colon-preservation inheritance regression
- `copier-template/.github/workflows/ci.yml` full lane now provisions uv explicitly; guardrails assert this.

## Heuristics
- Never parse YAML key-values with delimiter splitting when values can contain delimiters.
- Preview/adoption tooling must replay target profile state, not default assumptions.
- Structural diffs of generated repos should exclude VCS metadata unless VCS metadata is explicitly in scope.

## Propagation
- TIP candidate: yes → `tips/meta/tip-0009-profile-aware-preview-and-contract-safe-answers.md`
