# 2026-03-30 — Nexus control-plane hardening

## What I changed
- Added a shared `.copier-answers.yml` scalar parser helper at:
  - `scripts/lib/copier-answers.sh`
  - `copier-template/scripts/lib/copier-answers.sh`
  - `copier-template/copier/tpl-{agent,org,project,monorepo}/scripts/lib/copier-answers.sh`
- Rewired control-plane consumers to use the shared helper:
  - `scripts/preview-l1-diff.sh`
  - `scripts/ak.sh`
  - `copier-template/scripts/new-repo-from-copier.sh`
  - `copier-template/scripts/ak.sh`
  - `copier-template/scripts/check-template-ci.sh`
  - `copier-template/copier/tpl-{agent,org,project,monorepo}/scripts/ak.sh`
- Fixed suffix-policy exclusions in `copier-template/scripts/lib/suffix-policy.sh` so excluded child-repo paths are handled structurally instead of via a quoted command-fragment string.
- Fixed ROCS local-python fallback in root/L1/L2 wrappers by exporting `PYTHONPATH=<repo>/src` before `python -m rocs_cli`.
- Removed GNU-`sed -i` dependency from `copier-template/scripts/bootstrap-lane-root.sh` by replacing it with portable temp-file rewrites.
- Extended `scripts/check-l0-generation.sh` with adversarial regressions for:
  - quoted `#` values in answers + preview no-diff
  - child-repo `.j2` files under `owned/`
  - portable lane bootstrap without `sed -i`
  - generated L1 and root ROCS local-python fallback execution
- Updated guardrails and synced fixtures.

## Why
The deep adversarial review found a cluster of control-plane failures caused by duplicated shell parsing/mutation logic and happy-path-only validation. The nexus fix was to move the fragile answer parsing into a shared helper, harden the remaining shell primitives, and encode the discovered edge cases as executable regressions.

## Validation
- `bash ./scripts/check-l0-generation.sh`
- `bash ./scripts/check-l0-fixtures.sh`
- `bash ./scripts/check-l0.sh`
- Manual verification: root `scripts/rocs.sh` local-python fallback in a temp src-layout repo
- Manual verification: `scripts/preview-l1-diff.sh` stays no-diff for `company_name='Foo #1'`

## Follow-ups
- Consider propagating the shared answers helper into L2 repo-local AK wrappers as a second convergence pass if more answer parsing accumulates there.
