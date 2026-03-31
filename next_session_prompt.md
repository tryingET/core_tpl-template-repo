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
  - Re-ran the runtime-resolved FCOS queue lookup, claimed `AK-620`, and added executable task-scope snapshot drift enforcement across generated repo CI surfaces.
- Outcome:
  - `just fcos-runnable` still resolves to `FCOS-M36-04` for `core/tpl-template-repo`, so this repo-local slice remained the runtime head during the session.
  - `AK-620` completed by adding generated `scripts/check-task-scope-snapshots.sh` helpers plus CI wiring in the generated L1 template repo, `tpl-project-repo`, and `tpl-monorepo`.
  - The new enforcement now checks checked-in `governance/task-scopes/AK-<TASK-ID>.snapshot.json` files against live AK state and repo ownership when snapshots are present.
  - While wiring the full lane, the session also fixed two latent gaps that had previously been masked in generated project CI:
    - `tpl-project-repo/scripts/ci/full.sh` now preserves parallel subprocess exit codes instead of dropping failures through `! wait ...`
    - generated full lanes now use `./scripts/ak.sh work-items check --repo . ...`, matching the wrapper contract that actually keeps work-item projections reproducible
  - Generated template CI now covers:
    - positive L1 / project / monorepo snapshot verification against a temp AK DB
    - rejection of foreign task snapshots in generated project repos
    - rejection of drifted snapshot content in generated monorepos
  - The repo-local `[FCOS-M36-04]` chain is not finished yet; `AK-621` is now the next local follow-up if this repo remains the runtime head.
- Validation run:
  - `bash ./scripts/check-l0-generation.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `copier-template/scripts/check-task-scope-snapshots.sh`
  - `copier-template/scripts/check-template-ci.sh`
  - `copier-template/copier/tpl-project-repo/scripts/check-task-scope-snapshots.sh`
  - `copier-template/copier/tpl-monorepo/scripts/check-task-scope-snapshots.sh`
  - `scripts/check-l0-guardrails.sh`
  - `next_session_prompt.md`
  - `diary/2026-03-30--review-ak-task-scope-adversarial.md`
  - `diary/2026-03-30--feat-ak-task-scope-snapshot-ci.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another local slice.
  - If `FCOS-M36-04` still resolves here, continue with `AK-621` (`Extend AK-native task-scope rollout to tpl-agent-repo/tpl-org-repo and fix task-id guidance`).
  - Only advance canonical FCOS state once the remaining repo-local `[FCOS-M36-04]` slice is finished and synced.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
