# AGENTS.md — L2 repo

## Intent
Operate the generated product repository with explicit local/CI guardrails.

## Recursion policy
Allowed:
- `L1 -> L2`

Forbidden:
- `L2 -> L1`
- `L2 -> L0`
- any cycle

## Local quality gate
- Install hooks: `./scripts/install-hooks.sh`
- Smoke lane: `./scripts/ci/smoke.sh`
- Full lane: `./scripts/ci/full.sh`

## Guardrails
- Keep `.copier-answers.yml` committed for reproducibility.
- Preserve baseline folder skeleton + git baseline files unless policy explicitly changes them.
- If `enable_community_pack=true`, maintain `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`, `CODE_OF_CONDUCT.md`, and `SUPPORT.md` as the public intake baseline.
- If `enable_release_pack=true`, maintain release workflows/metadata/docs/scripts (`release-please`, `release-check`, `publish`, release-please config/manifest, changelog/security, and scripts under `scripts/release/`).
- If `enable_vouch_gate=true`, maintain `.github/VOUCHED.td` through reviewed maintainer updates only.
