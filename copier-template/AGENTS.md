# AGENTS.md — L1 template repo

## Intent
Provide one stable, guarded template surface that generates compliant L2 repositories.

## Guardrails
- No secrets in git.
- Keep `.copier-answers.yml` committed.
- Run `./scripts/check-template-ci.sh` before merge.
- Keep `contracts/layer-contract.yml` in sync with README recursion policy.

## Recursion policy
Allowed:
- `L0 -> L1`
- `L1 -> L2`

Forbidden:
- `L1 -> L0`
- `L2 -> L1`
- any cycle
