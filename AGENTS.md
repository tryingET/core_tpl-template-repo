# AGENTS.md — tpl-template-repo

## Intent
Build and maintain the L0 meta-template that scaffolds compliant L1 template repositories.

## Working rules
- Keep recursion bounded: `L0 -> L1 -> L2` only.
- Never encode nested `copier copy` calls inside template `_tasks`.
- Keep `.copier-answers.yml` committed in generated repositories.
- Preserve baseline folder skeleton + git baseline files unless intentionally changed by policy.
- Treat `enable_community_pack` as profile policy (default disabled, enable for public/community-facing repos).
- Treat `enable_release_pack` as profile policy (default disabled, enable where release automation is required).
- Treat `enable_vouch_gate` as profile policy (default disabled, enable for trust-gated/public repos).
- No secrets in git.

## Recursion policy (explicit)
Allowed:
- `L0 -> L1`
- `L1 -> L2`

Forbidden:
- `L1 -> L0`
- `L2 -> L1`
- any cycle

## Validation before merge
- `bash ./scripts/check-l0.sh`
- optional focused runs:
  - `bash ./scripts/check-supply-chain.sh`
  - `bash ./scripts/check-l0-generation.sh`
  - `bash ./scripts/check-l0-fixtures.sh`
