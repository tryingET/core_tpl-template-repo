# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FOLLOW THE RUNTIME-RESOLVED FCOS QUEUE, BUT DO NOT START A NEW LOCAL SLICE UNLESS THE HEAD RETURNS HERE

The runtime-resolved FCOS head has moved off `core/tpl-template-repo` to `softwareco/infra/workstation` for `FCOS-M38-01`.
Treat the repo-local `FCOS-M36-06` slice as canonically closed and use this repo only as a mirror/handoff surface until the resolver points back here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M38-01`
- Last synced runtime-resolved FCOS repo (mirror-only, rerun the resolver instead of trusting this line):
  - `softwareco/infra/workstation`
- Anti-drift cadence policy:
  - loop-owned via `~/ai-society/holdingco/governance-kernel/governance/fcos/loops-registry.json` plugin `loop.fcos.drift.audit`

## READ-FIRST ALLOWLIST
1. `AGENTS.md`
2. `README.md`
3. `copier-template/docs/dev/task-scope-migration-playbook.md`
4. `docs/learnings/2026-03-13-stable-core-thin-adapters-for-multi-surface-systems.md`
5. `docs/learnings/2026-03-13-recurring-operation-languages-should-become-explicit.md`
6. `tips/meta/tip-0010-stable-core-thin-adapters-for-multi-surface-systems.md`
7. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Verified canonical `FCOS-M36-06` closeout in governance-kernel, re-ran the runtime-resolved FCOS queue lookup, confirmed the head advanced to `FCOS-M38-01`, and updated this repo's mirror/handoff surface.
- Outcome:
  - `FCOS-M36-06` is now `done` in `~/ai-society/holdingco/governance-kernel/governance/programs/fcos/work-items.json` with all three rollout tasks checked off and scheduler transition history recorded.
  - `just fcos-runnable` now resolves to `FCOS-M38-01` in `softwareco/infra/workstation`, so `core/tpl-template-repo` no longer owns the runtime FCOS head.
  - Repo-local template follow-through for `AK-553` remains canonically closed:
    - `copier-template/docs/dev/task-scope-migration-playbook.md` is the template-side brownfield migration playbook
    - L0/L1/L2 docs already teach the compatibility-only boundary for legacy `AK-*.json` task-scope manifests
    - no new local FCOS template slice is needed unless a later runtime head returns here
  - `AK-281` is still a separately ready repo-local AK task, but it is unrelated to the runtime-resolved FCOS queue and should not replace FCOS workflow without explicit operator direction.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` (`FCOS-M38-01` includes `holdingco/governance-kernel` + `softwareco/infra/workstation`)
  - `bash ./scripts/check-l0.sh` (pass)
  - `bash ./scripts/check-session-checkpoint.sh` (pass)
- Files of interest:
  - `~/ai-society/holdingco/governance-kernel/governance/programs/fcos/work-items.json`
  - `~/ai-society/holdingco/governance-kernel/governance/fcos/portfolio.yaml`
  - `~/ai-society/holdingco/governance-kernel/docs/project/fcos-direction-to-execution.md`
  - `diary/2026-04-01--docs-fcos-m36-06-task-scope-migration-playbook.md`
  - `diary/2026-04-01--ops-fcos-m36-06-closeout-and-queue-advance.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session.
  - If `FCOS-M38-01` still resolves to `softwareco/infra/workstation`, leave this repo and follow that head instead of starting new local work.
  - If the runtime-resolved head later returns to this repo, start from the then-current FCOS issue instead of reopening `FCOS-M36-06`.
  - Do not substitute unrelated ready task `AK-281` for FCOS queue work unless the operator explicitly asks for that backlog item.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
