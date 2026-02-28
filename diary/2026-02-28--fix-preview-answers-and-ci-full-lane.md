# 2026-02-28 — Fix preview fidelity, inheritance parsing, and full-lane CI prerequisites

## What I Did
- Fixed `scripts/preview-l1-diff.sh` to rehydrate render inputs from target `.copier-answers.yml` (company/profile/toggles), so non-default bundles diff correctly.
- Made preview comparisons ignore `.git/` by diffing normalized compare copies.
- Fixed colon-safe inherited value parsing in `copier-template/scripts/new-repo-from-copier.sh` (`company_name: Foo: Labs` now preserved).
- Added `Setup uv (full lane)` to `copier-template/.github/workflows/ci.yml` for the full job.
- Added guardrail assertions for the new CI requirement and expanded generation tests:
  - release-profile preview no-diff regression check
  - colon-preservation inheritance regression check
- Synced fixtures and re-ran full L0 validation.

## What Surprised Me
- `preview-l1-diff.sh` previously produced large false diffs against git repos because `.git/` was included in `git diff --no-index`.
- Copier rejects absolute `-a /abs/path/.copier-answers.yml` as non-relative.

## Patterns
- Ad-hoc YAML parsing via `awk -F':'` is fragile for valid scalar values containing colons.
- Adoption tooling must mirror target profile toggles to avoid false drift signals.

## Crystallization Candidates
- → docs/learnings/: “profile-aware preview render contracts”
- → tips/meta/: “never diff generated repos including `.git/` when comparing structure/content”
