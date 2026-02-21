# AGENTS.md — L2 repo

## Intent
Operate the generated L2 repository with explicit local/CI guardrails.

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
- Keep `repo_archetype` explicit (`project|agent|org|owned`) and avoid drifting across archetypes without review.
- Keep `org_docs_profile` explicit (`compact` for lean L2 repos, `rich` when full org documentation belongs in the repo).
- If `org_docs_canonical_ref` is set, keep org/project docs aligned to that canonical source.
- For `project` and `owned` archetypes, keep `docs/project/governance_overlay.md` as the project-local governance contract:
  - local rules may specialize or tighten org baseline;
  - any weakening of org controls requires explicit consent recorded in the deviation register.
- For `org` archetypes, keep governance process docs under `governance/` and org records under `docs/registers/` + `docs/decisions/`.
- For `agent` archetypes, keep persona context under `docs/person/`, `docs/system4d/`, and `docs/learnings/`.
- If `enable_community_pack=true`, maintain `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`, `CODE_OF_CONDUCT.md`, and `SUPPORT.md` as the public intake baseline.
- If `enable_release_pack=true`, maintain release workflows/metadata/docs/scripts (`release-please`, `release-check`, `publish`, release-please config/manifest, changelog/security, and scripts under `scripts/release/`).
- If `enable_vouch_gate=true`, maintain `.github/VOUCHED.td` through reviewed maintainer updates only.
