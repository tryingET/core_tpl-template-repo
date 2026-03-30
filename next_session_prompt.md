# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FOLLOW THE RUNTIME-RESOLVED FCOS QUEUE FOR THE NEXT L0 SLICE

This repo currently has no known blocking local follow-up after the AK-first work-items slice and the ontology-lsp architecture archaeology/crystallization pass.
Choose the next repo-local slice from the runtime-resolved FCOS queue rather than from stale hardcoded issue IDs.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M36-02`
- Anti-drift cadence policy:
  - loop-owned via `~/ai-society/holdingco/governance-kernel/governance/fcos/loops-registry.json` plugin `loop.fcos.drift.audit`

## READ-FIRST ALLOWLIST
1. `AGENTS.md`
2. `README.md`
3. `docs/learnings/2026-03-13-stable-core-thin-adapters-for-multi-surface-systems.md`
4. `docs/learnings/2026-03-13-recurring-operation-languages-should-become-explicit.md`
5. `tips/meta/tip-0010-stable-core-thin-adapters-for-multi-surface-systems.md`
6. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Re-ran the runtime-resolved FCOS queue lookup and checked the next tpl-template-repo candidates before touching code.
- Outcome:
  - `just fcos-runnable` currently resolves to `FCOS-M36-02` in `softwareco/owned/agent-kernel`, so there is no runnable repo-local L0 slice in `core/tpl-template-repo` right now.
  - The next tpl-template-repo issue in the canonical model is `FCOS-M36-04`, but it remains blocked by `FCOS-M36-02` and `FCOS-M36-03`; `FCOS-M36-06` remains downstream of `FCOS-M36-04` and `FCOS-M36-05`.
  - This session therefore stayed mirror-only: refreshed the handoff prompt and captured the queue state in a repo diary entry instead of starting a blocked implementation slice.
- Validation run:
  - `bash ./scripts/check-session-checkpoint.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `next_session_prompt.md`
  - `diary/2026-03-30--ops-runtime-fcos-queue-sync.md`
- Blockers / follow-up:
  - Wait for `FCOS-M36-02` / `FCOS-M36-03` to unblock `FCOS-M36-04` before starting the next tpl-template-repo implementation slice.
  - After `FCOS-M36-04` lands, reevaluate `FCOS-M36-06` with the runtime resolver instead of trusting this mirror.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
