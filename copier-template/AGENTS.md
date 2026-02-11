# AGENTS.md — L1 template repo

## Intent
Provide one stable, guarded template surface that generates compliant L2 repositories.

## Guardrails
- No secrets in git.
- Keep `.copier-answers.yml` committed.
- Run `./scripts/check-template-ci.sh` before merge.
- Keep `contracts/layer-contract.yml` in sync with README recursion policy.
- Preserve baseline structure folders and git baseline files unless intentionally changed by policy.
- Treat `l1_org_docs_profile` as a profile decision (default rich; compact allowed for lightweight internal template lines).
- Treat `l2_org_docs_default` as a profile decision (default compact; rich when L2 repos should carry full org docs).
- Treat `enable_community_pack` as a profile decision (default disabled, enable for public/community-facing contribution surfaces).
- Treat `enable_release_pack` as a profile decision (default disabled, enable where release automation is required).
- Treat `enable_vouch_gate` as a profile decision (default disabled, enable for trust-gated/public contribution surfaces).

## Recursion policy
Allowed:
- `L0 -> L1`
- `L1 -> L2`

Forbidden:
- `L1 -> L0`
- `L2 -> L1`
- any cycle
