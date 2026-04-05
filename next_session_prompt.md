# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: NO RUNTIME FCOS HEAD IS CURRENTLY RESOLVED; KEEP THIS REPO IN MIRROR-ONLY / OPERATOR-DIRECTED POSTURE

The runtime-resolved FCOS queue currently resolves to `none` (`cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`).
Repo-local FCOS slices `#738`, `#820`, `#821`, and `#851` are closed; do not reopen them for mirror-only work.
Re-run the FCOS resolver first. If it still returns no runnable head, only fall back to the repo-local ready queue when the operator explicitly asks for backlog work here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `none`
- Last synced runtime-resolved FCOS repo set (mirror-only, rerun the resolver instead of trusting this line):
  - `none`
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
9. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Resumed and completed repo-local AK task `#851` on explicit operator request, codifying `core/tpl-template-repo` as the canonical distribution authority for the generic launcher wrappers against the M45 convergence receipt.
- Outcome:
  - Updated `AGENTS.md`, `README.md`, and new note `docs/project/2026-04-05-generic-launcher-wrapper-template-authority.md` so the launcher-wrapper authority split is explicit: runtime/reference owner in `softwareco/owned/agent-kernel`, canonical distribution authority in `core/tpl-template-repo`, rollout/proof reporting in `holdingco/infra/template-propagator`.
  - Updated all four L2 governance README templates plus synced fixtures so generated repos keep the same owner/distribution/reporting split for `scripts/ak.sh` and `scripts/cargo-operator.sh`.
  - Added deterministic assertions to `copier-template/scripts/check-template-ci.sh` and propagated the generated fixture copy.
  - Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` and confirmed the live FCOS resolver currently returns `[]` / `none`, so this repo should return to mirror-only / operator-directed posture after task `#851` closeout.
  - Captured the session in `diary/2026-04-05--ops-task-851-generic-launcher-wrapper-template-authority.md`.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
  - `bash ./scripts/check-l0-generation.sh`
  - `bash ./scripts/check-l0-fixtures.sh`
  - `bash ./scripts/check-doc-references.sh`
  - `bash ./scripts/check-l0.sh`
- Files of interest:
  - `AGENTS.md`
  - `README.md`
  - `docs/project/2026-04-05-generic-launcher-wrapper-template-authority.md`
  - `copier-template/scripts/check-template-ci.sh`
  - `diary/2026-04-05--ops-task-851-generic-launcher-wrapper-template-authority.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session; the current resolver returns `none`, so operator direction should choose the next slice explicitly.
  - In this repo, treat repo-local tasks `#738`, `#820`, `#821`, and `#851` as closed implementation slices. If the operator wants backlog work here, pick explicitly from `AK-281` or `#791`; if `#794` still appears in `task ready`, treat that as stale local AK state until the DB/storage drift is repaired.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md AGENTS.md README.md docs/project/2026-04-05-generic-launcher-wrapper-template-authority.md copier-template/copier/tpl-agent-repo/governance/README.md copier-template/copier/tpl-monorepo/governance/README.md copier-template/copier/tpl-org-repo/governance/README.md copier-template/copier/tpl-project-repo/governance/README.md copier-template/scripts/check-template-ci.sh fixtures/l1/template-repo/copier/tpl-agent-repo/governance/README.md fixtures/l1/template-repo/copier/tpl-monorepo/governance/README.md fixtures/l1/template-repo/copier/tpl-org-repo/governance/README.md fixtures/l1/template-repo/copier/tpl-project-repo/governance/README.md fixtures/l1/template-repo/scripts/check-template-ci.sh fixtures/l2/tpl-agent-repo/governance/README.md fixtures/l2/tpl-monorepo/governance/README.md fixtures/l2/tpl-org-repo/governance/README.md fixtures/l2/tpl-project-repo/governance/README.md fixtures/matrix/tpl-monorepo/root/governance/README.md fixtures/matrix/tpl-project-repo/elixir/governance/README.md fixtures/matrix/tpl-project-repo/node/governance/README.md fixtures/matrix/tpl-project-repo/python/governance/README.md fixtures/matrix/tpl-project-repo/rust/governance/README.md fixtures/matrix/tpl-project-repo/typescript/governance/README.md diary/2026-04-05--ops-task-851-generic-launcher-wrapper-template-authority.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
