# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: RUNTIME FCOS HEAD CURRENTLY RESOLVES ELSEWHERE; KEEP THIS REPO IN MIRROR-ONLY / OPERATOR-DIRECTED POSTURE

The live runtime-resolved FCOS queue currently points at `FCOS-M46-01`, and its repo set does **not** include this repo (`cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`).
Repo-local FCOS slices `#738`, `#820`, `#821`, `#851`, and `#281` are closed; do not reopen them for mirror-only work.
Re-run the FCOS resolver first. If the live head still excludes this repo, only fall back to the repo-local ready queue when the operator explicitly asks for backlog work here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M46-01`
- Last synced runtime-resolved FCOS repo set (mirror-only, rerun the resolver instead of trusting this line):
  - `holdingco/governance-kernel`
  - `softwareco/owned/email-copilot`
  - `softwareco/infra/workstation`
  - `softwareco/infra/ds1621-admin`
- Anti-drift cadence policy:
  - loop-owned via `~/ai-society/holdingco/governance-kernel/governance/fcos/loops-registry.json` plugin `loop.fcos.drift.audit`

## READ-FIRST ALLOWLIST
1. `AGENTS.md`
2. `README.md`
3. `scripts/ak.sh`
4. `scripts/cargo-operator.sh`
5. `diary/2026-04-04--chore-ak-nightly-cargo-wrapper-propagation.md`
6. `diary/2026-04-04--ops-fcos-m43-01-tpl-template-repo-closeout.md`
7. `diary/2026-04-05--fix-nexus-helper-parity-language-matrix-and-stack-wording.md`
8. `diary/2026-04-05--ops-task-851-generic-launcher-wrapper-template-authority.md`
9. `diary/2026-04-05--review-full-adversarial-stack.md`
10. `diary/2026-04-05--feat-negative-path-nexus-hardening.md`
11. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Completed repo-local AK task `#281`, removing template-shipped ROCS GitLab baseline/ref-resolution behavior from `tpl-project-repo` and moving the template contract to workspace-only `<repo:...>` locators.
- Outcome:
  - Refreshed `copier-template/copier/tpl-project-repo/tools/rocs-cli/` from `~/ai-society/core/rocs-cli` via `scripts/vendor-to.sh`, which removed the vendored `gitlab.py` helper and brought in workspace-aware ref resolution.
  - Updated `copier-template/copier/tpl-project-repo/copier.yml` so default ontology refs are now `<repo:core/ontology-kernel@main>` and `<repo:{{ company_slug }}/ontology@main>`.
  - Updated `copier-template/copier/tpl-project-repo/README.md.j2`, `ontology/index.md`, and `copier-template/docs/dev/tpl-project-repo-file-contract.md` so operators are pointed at `ROCS_WORKSPACE_ROOT` + `./scripts/rocs.sh` instead of legacy GitLab assumptions.
  - Strengthened `scripts/check-l0-guardrails.sh` and `copier-template/scripts/check-template-ci.sh` to require repo-locator defaults, workspace-aware vendored sources, and absence of the legacy vendored `gitlab.py` surface.
  - Regenerated L1/L2/matrix fixtures with `bash ./scripts/sync-l0-fixtures.sh`.
  - Captured the slice in `diary/2026-04-06--feat-tpl-project-repo-rocs-workspace-ref-migration.md`.
  - Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` and confirmed the live runtime FCOS head now resolves to `FCOS-M46-01` in other repos, so this repo should remain mirror-only / operator-directed unless the operator explicitly selects backlog work here.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
  - `bash ./scripts/sync-l0-fixtures.sh`
  - `bash ./scripts/check-l0.sh`
- Files of interest:
  - `copier-template/copier/tpl-project-repo/copier.yml`
  - `copier-template/copier/tpl-project-repo/README.md.j2`
  - `copier-template/copier/tpl-project-repo/ontology/index.md`
  - `copier-template/copier/tpl-project-repo/tools/rocs-cli/README.md`
  - `copier-template/copier/tpl-project-repo/tools/rocs-cli/src/rocs_cli/layers.py`
  - `scripts/check-l0-guardrails.sh`
  - `copier-template/scripts/check-template-ci.sh`
  - `diary/2026-04-06--feat-tpl-project-repo-rocs-workspace-ref-migration.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session; the live head currently targets other repos, so backlog work here should stay operator-directed.
  - In this repo, treat repo-local tasks `#738`, `#820`, `#821`, `#851`, and `#281` as closed implementation slices. If the operator wants backlog work here next, pick explicitly from `#791`; if `#794` still appears in `task ready`, treat it as stale local AK state until the DB/storage drift is repaired.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md scripts/check-l0-guardrails.sh copier-template/scripts/check-template-ci.sh copier-template/docs/dev/tpl-project-repo-file-contract.md copier-template/copier/tpl-project-repo fixtures/l1/template-repo/copier/tpl-project-repo fixtures/l1/template-repo/docs/dev/tpl-project-repo-file-contract.md fixtures/l1/template-repo/scripts/check-template-ci.sh fixtures/l2/tpl-project-repo fixtures/matrix/tpl-project-repo diary/2026-04-06--feat-tpl-project-repo-rocs-workspace-ref-migration.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
