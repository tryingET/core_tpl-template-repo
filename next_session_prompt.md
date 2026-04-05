# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FCOS-M44-01 REMAINS THE RUNNABLE HEAD; KEEP THIS REPO IN MIRROR-ONLY CLOSEOUT POSTURE

The runtime-resolved FCOS queue currently resolves to `FCOS-M44-01` (`cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`).
Repo-local FCOS slices `#738`, `#820`, and `#821` are closed; do not reopen them for mirror-only work.
If the operator explicitly asks for one of those closed tasks, first verify its completed commit/result before doing anything else. Otherwise re-run the FCOS resolver first, then fall back to the repo-local ready queue only if the operator wants backlog work here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M44-01`
- Last synced runtime-resolved FCOS repo set (mirror-only, rerun the resolver instead of trusting this line):
  - `holdingco/governance-kernel`, `softwareco/owned/agent-kernel`, `core/tpl-template-repo`
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
8. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Verified repo-local AK task `#821` was already completed and committed in `7a5e2a7`, then refreshed the repo handoff mirror so `tpl-template-repo` stays in mirror-only closeout posture while `FCOS-M44-01` remains the runtime-resolved cross-repo head.
- Outcome:
  - Confirmed `./scripts/ak.sh task show 821` reports `done` with commit `7a5e2a7` and the managed launcher-bundle adoption snapshot artifacts already recorded in task results.
  - Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` and confirmed the live FCOS resolver still returns `FCOS-M44-01` for `holdingco/governance-kernel`, `softwareco/owned/agent-kernel`, and `core/tpl-template-repo`.
  - Updated `next_session_prompt.md` so repo-local slices `#738`, `#820`, and `#821` stay explicitly closed and future sessions only fall back to repo-local backlog if the operator asks for backlog work here.
  - Captured the mirror-only closeout in `diary/2026-04-05--ops-fcos-m44-01-task-821-closeout-mirror.md`.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
  - `bash ./scripts/check-l0.sh`
  - `bash ./scripts/check-session-checkpoint.sh`
- Files of interest:
  - `next_session_prompt.md`
  - `diary/2026-04-05--ops-fcos-m44-01-task-821-closeout-mirror.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session; `FCOS-M44-01` is still the mirrored runnable head, and operator direction still wins over backlog inference.
  - In this repo, treat repo-local tasks `#820` and `#821` as closed implementation slices. If the operator wants backlog work here, pick explicitly from `AK-281` or `#791`; if `#794` still appears in `task ready`, treat that as stale local AK state until the DB/storage drift is repaired.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md diary/2026-04-05--ops-fcos-m44-01-task-821-closeout-mirror.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
