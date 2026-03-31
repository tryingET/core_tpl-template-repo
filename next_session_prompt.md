# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FOLLOW THE RUNTIME-RESOLVED FCOS QUEUE FOR THE NEXT L0 SLICE

The runtime-resolved FCOS head is back on `core/tpl-template-repo` for `FCOS-M36-04`.
Continue the remaining repo-local slice chain for that issue via AK rather than trusting stale mirror notes or older blocked-state assumptions.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M36-04`
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
  - Re-ran the runtime-resolved FCOS queue lookup, claimed `AK-547`, and propagated the AK-native task-scope flow into the descendant `tpl-project-repo`, `tpl-monorepo`, and `tpl-package` template surfaces.
- Outcome:
  - `just fcos-runnable` now resolves to `FCOS-M36-04` for `core/tpl-template-repo`, so the repo-local slice was runnable again.
  - `AK-547` completed by updating descendant template docs/prompts/governance guidance to treat explicit task scope as AK-authored and repo-side snapshots as frozen exports.
  - Re-synced the L1/L2/matrix fixtures so the propagated descendant surfaces stay in lockstep with the L0 source.
  - `AK-548` is now the immediate repo-local follow-up for the remaining `FCOS-M36-04` regression-tightening slice.
- Validation run:
  - `bash ./scripts/check-l0.sh` (pass)
  - `bash ./scripts/check-session-checkpoint.sh` (pass)
- Files of interest:
  - `next_session_prompt.md`
  - `copier-template/copier/tpl-project-repo/`
  - `copier-template/copier/tpl-monorepo/`
  - `copier-template/copier/tpl-package/`
  - `diary/2026-03-30--feat-ak-task-scope-descendant-propagation.md`
- Blockers / follow-up:
  - Claim and complete `AK-548` to tighten regression checks around the new descendant task-scope adoption surface.
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting any non-`FCOS-M36-04` local slice.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
