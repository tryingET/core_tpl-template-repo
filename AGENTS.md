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

## Shared tooling
- Docs discovery/scoping: `./scripts/docs-list.sh --task "<task>" --top 8`
- Prompt read-scope allowlist: `./scripts/docs-list.sh --from-prompt <prompt-file> --paths-only --wikilink`
- ROCS command launcher (deterministic + portable): `./scripts/rocs.sh <rocs args...>`

## Deterministic tooling policy (ROCS-first)
- Prefer deterministic wrappers (`./scripts/rocs.sh`, repo `scripts/*`) over ad-hoc inline scripts.
- For ontology/policy checks, run ROCS before custom Python one-offs.
- Use inline Python only as an explicit escape hatch when no deterministic command exists.

## Diary policy (repo-local, mandatory)
- Keep session capture in `./diary/YYYY-MM-DD--type-scope-summary.md` for this repo.
- Keep diary guidance in `./diary/README.md`.
- Apply the same diary contract per structural template (`tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`, `tpl-individual-repo` when added).

## Validation before merge
- `bash ./scripts/check-l0.sh`
- optional focused runs:
  - `bash ./scripts/check-supply-chain.sh`
  - `bash ./scripts/check-l0-generation.sh`
  - `bash ./scripts/check-l0-fixtures.sh`
