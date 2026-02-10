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
- If `enable_vouch_gate=true`, maintain `.github/VOUCHED.td` through reviewed maintainer updates only.
