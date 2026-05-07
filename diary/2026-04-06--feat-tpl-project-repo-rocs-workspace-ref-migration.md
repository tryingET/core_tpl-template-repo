---
summary: "Session note: 2026 04 06 Feat Tpl Project Repo Rocs Workspace Ref Migration."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 04 06 feat tpl project repo rocs workspace ref migration."
type: "reference"
---

# 2026-04-06 — tpl-project-repo ROCS workspace-ref migration

## What I Did
- Claimed repo-local AK task `#281` after the operator explicitly selected backlog work in this repo.
- Re-ran the FCOS resolver and confirmed the live runtime head now points at `FCOS-M46-01` in other repos, so this repo should remain operator-directed / backlog-only unless explicitly selected.
- Used `~/ai-society/core/rocs-cli/scripts/vendor-to.sh` to refresh the vendored `tools/rocs-cli/` copy shipped by `tpl-project-repo`.
- Migrated `tpl-project-repo` default ontology refs from legacy `<gitlab:...>` locators to workspace-only `<repo:...@main>` locators in `copier-template/copier/tpl-project-repo/copier.yml`.
- Updated `copier-template/copier/tpl-project-repo/README.md.j2` and `ontology/index.md` so generated repos point operators at `ROCS_WORKSPACE_ROOT` + `./scripts/rocs.sh` instead of legacy GitLab assumptions.
- Updated `copier-template/docs/dev/tpl-project-repo-file-contract.md` so the canonical file-contract doc records the workspace-only ROCS contract.
- Replaced old guardrail assertions that expected `gitlab.py` with new assertions that require repo-locator defaults, workspace-aware vendored sources, and absence of the legacy GitLab helper.
- Regenerated L1/L2/matrix fixtures with `bash ./scripts/sync-l0-fixtures.sh`.

## Validation
- `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- `bash ./scripts/sync-l0-fixtures.sh`
- `bash ./scripts/check-l0.sh`

## What Surprised Me
- The first validation failure was not semantic; the new shell assertions used double-quoted needles containing backticks, which `sh` treated as command substitution.
- Copier happily rendered the dynamic default `"<repo:{{ company_slug }}/ontology@main>"`, so the generated `.copier-answers.yml` and manifests now stay aligned with `company_slug` without extra post-processing.

## Patterns
- Vendored tool migrations are safest when the upstream repo owns the sync script and downstream repos only codify the contract checks.
- When shell assertions need literal backticks, quote them with single quotes or the guardrail itself becomes the regression.
- Repo-locator migrations need three layers kept in sync: template defaults, vendored tool behavior, and generated fixtures.

## Follow-up
- If backlog work in this repo is requested again, the next explicit slice is `#791`; treat `#794` as stale until the local AK storage drift is repaired if it still appears in `task ready`.
- Consider crystallizing the backtick-in-shell-assertion trap into a reusable learning if more guardrail scripts hit the same pattern.
