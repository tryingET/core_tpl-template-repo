# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FCOS-M44-01 IS NOW THE RUNNABLE HEAD; WORK THE BOUNDED TEMPLATE FOLLOW-THROUGH

The runtime-resolved FCOS queue currently resolves to `FCOS-M44-01` (`cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`).
Repo-local FCOS slice `#738` remains closed; do not reopen it.
The next bounded follow-through here is `FCOS-M44-01` repo-local task `#820`; if the operator gives that task explicitly, work it. Otherwise re-run the FCOS resolver first, then fall back to the repo-local ready queue only if the operator wants backlog work here.

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
  - Implemented and committed the repo-side slice for AK task `#794` to tune `check-l0` timeout and orchestration behavior for slower runners without weakening failure semantics.
- Outcome:
  - `scripts/check-l0.sh` now resolves either `timeout` or `gtimeout` instead of assuming one host binary.
  - The consolidated L0 runner now prints the effective timeout policy up front so each run shows the base budget, heavier generation budget, and timeout runner in use.
  - `check-l0-generation` now gets a larger default timeout budget than the lighter subchecks, while explicit env overrides still work.
  - Timeout failures remain fail-closed, but once one timeout happens the runner aborts later heavyweight checks and records them as skipped-after-timeout instead of spending more slow-runner time on an already-failed aggregate lane.
  - Captured the session in `diary/2026-04-05--chore-check-l0-slow-runner-timeout-orchestration.md` and crystallized the pattern in `docs/learnings/2026-04-05-check-runners-need-heavy-lane-budgets-and-timeout-aborts.md`.
  - Intended next ready repo-local backlog is `FCOS-M44-01` follow-through task `#820` alongside `AK-281` and `#791`; local AK read paths may still show a stale `#794` pending entry because of storage/index drift during closeout.
- Validation run:
  - `L0_CHECK_TIMEOUT_SECONDS=1 bash ./scripts/check-l0.sh` (expected fail-closed timeout path + abort-after-timeout behavior)
  - `bash ./scripts/check-l0-generation.sh` (pass)
  - `bash ./scripts/check-l0-adversarial.sh` (pass)
  - `bash ./scripts/check-l0-fixtures.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `scripts/check-l0.sh`
  - `diary/2026-04-05--chore-check-l0-slow-runner-timeout-orchestration.md`
  - `docs/learnings/2026-04-05-check-runners-need-heavy-lane-budgets-and-timeout-aborts.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session; `FCOS-M44-01` is still the mirrored runnable head right now, and operator direction still wins over backlog inference.
  - If the operator wants backlog work here, pick explicitly from `FCOS-M44-01` task `#820`, `AK-281`, or `#791`; if `#794` still appears in `task ready`, treat that as stale local AK state until the DB/storage drift is repaired.
  - Local AK read paths around task `#794` showed inconsistent list/show/ready behavior during closeout; treat that as local `society.v2.db` storage/index drift rather than repo-code drift.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md scripts/check-l0.sh diary/2026-04-05--chore-check-l0-slow-runner-timeout-orchestration.md docs/learnings/2026-04-05-check-runners-need-heavy-lane-budgets-and-timeout-aborts.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
