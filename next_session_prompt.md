# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FOLLOW THE RUNTIME-RESOLVED FCOS QUEUE, BUT DO NOT REOPEN COMPLETED LOCAL SLICES

The runtime-resolved FCOS head currently resolves to `FCOS-M43-01` and spans `holdingco/governance-kernel`, `softwareco/owned/agent-kernel`, and `core/tpl-template-repo`.
Treat repo-local AK task `#738` as the bounded `core/tpl-template-repo` slice for that concern.
Once this repo-local slice is committed and completed in AK, use this repo as a mirror/handoff surface unless the resolver points back here with a new local slice or the operator explicitly asks for a different repo-local task.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M43-01`
- Last synced runtime-resolved FCOS repo set (mirror-only, rerun the resolver instead of trusting this line):
  - `holdingco/governance-kernel`
  - `softwareco/owned/agent-kernel`
  - `core/tpl-template-repo`
- Anti-drift cadence policy:
  - loop-owned via `~/ai-society/holdingco/governance-kernel/governance/fcos/loops-registry.json` plugin `loop.fcos.drift.audit`

## READ-FIRST ALLOWLIST
1. `AGENTS.md`
2. `README.md`
3. `scripts/ak.sh`
4. `scripts/cargo-operator.sh`
5. `diary/2026-04-04--chore-ak-nightly-cargo-wrapper-propagation.md`
6. `diary/2026-04-04--ops-fcos-m43-01-tpl-template-repo-closeout.md`
7. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Claimed repo-local AK task `#738`, verified dependency `#736` was already done in `softwareco/owned/agent-kernel`, confirmed the runtime FCOS head is now `FCOS-M43-01`, and closed the tpl-template-repo launcher-bundle propagation slice by validating the already-landed wrapper propagation commit and refreshing this repo's handoff mirror.
- Outcome:
  - Repo-local AK task `#738` corresponds to the launcher-bundle propagation already landed in commit `d1ea412` (`chore(ak): propagate nightly cargo operator wrapper`).
  - The managed `scripts/ak.sh` + `scripts/cargo-operator.sh` bundle is propagated through the repo root, `copier-template/`, and checked-in fixtures.
  - Validation evidence `#433` records `validation:check-l0 = pass` for task `#738`.
  - `bash ./scripts/check-l0-generation.sh`, `bash ./scripts/check-l0-fixtures.sh`, and `bash ./scripts/check-l0.sh` all pass from this repo.
  - With governance-kernel task `#735` and agent-kernel task `#736` already done, `core/tpl-template-repo` no longer has an open local execution slice for `FCOS-M43-01` after task `#738` is completed in AK; any remaining queue/state transition belongs first in governance-kernel canonical FCOS surfaces.
  - `AK-281` is still a separate ready repo-local task, but it is unrelated to `FCOS-M43-01` and should not replace FCOS follow-through without explicit operator direction.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` (`FCOS-M43-01` includes `holdingco/governance-kernel` + `softwareco/owned/agent-kernel` + `core/tpl-template-repo`)
  - `bash ./scripts/check-l0-generation.sh` (pass)
  - `bash ./scripts/check-l0-fixtures.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `scripts/ak.sh`
  - `scripts/cargo-operator.sh`
  - `copier-template/scripts/ak.sh`
  - `copier-template/scripts/cargo-operator.sh`
  - `diary/2026-04-04--chore-ak-nightly-cargo-wrapper-propagation.md`
  - `diary/2026-04-04--ops-fcos-m43-01-tpl-template-repo-closeout.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session.
  - If `FCOS-M43-01` still resolves but this repo-local slice is already done, do not reopen task `#738`; reconcile the remaining cross-repo issue state from governance-kernel first.
  - If the runtime-resolved head moves to another repo, leave this repo and follow that head instead of starting unrelated local work here.
  - Do not substitute unrelated ready task `AK-281` for FCOS queue work unless the operator explicitly asks for that backlog item.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md diary/2026-04-04--ops-fcos-m43-01-tpl-template-repo-closeout.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
