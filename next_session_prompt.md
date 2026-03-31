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
  - Re-ran the runtime-resolved FCOS queue lookup, claimed `AK-548`, and encoded regression checks for the AK-native task-scope adoption across descendant generated surfaces.
- Outcome:
  - `just fcos-runnable` still resolves to `FCOS-M36-04` for `core/tpl-template-repo`, so this repo-local slice remained the runtime head during the session.
  - `AK-548` completed by tightening `scripts/check-l0-guardrails.sh` and `scripts/check-l0-generation.sh` around the propagated task-scope contract.
  - Guardrails now assert that:
    - `tpl-project-repo` keeps AK-authored `governance/task-scopes/AK-<id>.snapshot.json` guidance plus the transitional-scaffolding warning
    - `tpl-monorepo` keeps explicit task-scope authority at the monorepo root
    - `tpl-package` inherits monorepo-root task-scope authority and does not ship standalone `scripts/ak.sh` or `governance/task-scopes/`
  - No further repo-local `[FCOS-M36-04]` AK tasks remain in `core/tpl-template-repo`, but canonical FCOS state was not advanced in this repo session, so the next session must re-resolve before picking another slice.
- Validation run:
  - `bash ./scripts/check-l0-generation.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `scripts/check-l0-guardrails.sh`
  - `scripts/check-l0-generation.sh`
  - `next_session_prompt.md`
  - `diary/2026-03-30--test-ak-task-scope-regression-coverage.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another local slice.
  - If `FCOS-M36-04` still resolves, confirm whether governance-kernel FCOS state now needs sync because the repo-local AK chain (`AK-546` → `AK-548`) is complete.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
