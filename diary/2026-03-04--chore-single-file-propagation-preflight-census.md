# 2026-03-04 — Single-file propagation for preflight census helper

## What I Did
- Followed `docs/dev/single-file-propagation-playbook.md` as the knowledge source for safe targeted propagation.
- Removed accidental L1 baseline placement at `copier-template/scripts/preflight-repo-census.sh`.
- Kept L0 helper at `scripts/preflight-repo-census.sh`.
- Added L2 template file(s) through L1 template layer only:
  - `copier-template/copier/tpl-agent-repo/scripts/preflight-repo-census.sh.j2`
  - `copier-template/copier/tpl-org-repo/scripts/preflight-repo-census.sh.j2`
  - `copier-template/copier/tpl-project-repo/scripts/preflight-repo-census.sh.j2`
  - `copier-template/copier/tpl-monorepo/scripts/preflight-repo-census.sh.j2`
- Updated L2 AGENTS template docs to reference the helper in deterministic tooling policy.
- Reverted L1 AGENTS baseline claim so L1 does not claim a non-existent local helper.
- Synced fixtures and validated guardrails:
  - `bash ./scripts/sync-l0-fixtures.sh`
  - `bash ./scripts/check-l0-fixtures.sh`
  - `bash ./scripts/check-l0-guardrails.sh`

## What Surprised Me
- Shell array length `${#REPOS[@]}` conflicts with Jinja comment syntax in `.j2` templates; replaced with a Jinja-safe count expression.

## Patterns
- For template repos, adding one file often requires fixture synchronization to preserve deterministic contracts.
- "Propagate through L1" works best by editing `copier-template/copier/*` and then syncing fixture renders.

## Crystallization Candidates
- → docs/learnings/: Jinja-safe shell snippets for `.j2` scripts (`${#...}` hazard)
- → tips/meta/: one-file propagation checklist for template repos with fixture checks
