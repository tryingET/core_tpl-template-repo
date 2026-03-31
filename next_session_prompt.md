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
  - Re-ran the runtime-resolved FCOS queue lookup, claimed `AK-621`, extended the AK-native task-scope rollout to `tpl-agent-repo` / `tpl-org-repo`, and standardized task-id guidance on the task-scope surfaces.
- Outcome:
  - `just fcos-runnable` still resolves to `FCOS-M36-04` for `core/tpl-template-repo`, so this repo-local slice remained the runtime head during the session.
  - Generated `tpl-agent-repo` / `tpl-org-repo` repos now ship `scripts/check-task-scope-snapshots.sh`, run it from `scripts/ci/full.sh`, and document optional AK task-scope snapshots under `governance/task-scopes/`.
  - L0/L1/L2 docs and prompts now use the clearer `TASK-ID` placeholder contract (`./scripts/ak.sh task scope show <TASK-ID>` and `governance/task-scopes/AK-<TASK-ID>.snapshot.json`) instead of the copy-paste-fragile `<AK-ID>` wording.
  - Generated L1 template CI now covers the new descendants end-to-end:
    - positive generated agent/org snapshot verification against a temp AK DB
    - rejection of foreign task snapshots in generated agent repos
    - rejection of drifted snapshot content in generated org repos
  - The repo-local `[FCOS-M36-04]` AK slice chain (`AK-546 -> AK-548 -> AK-620 -> AK-621`) is now finished in code + fixtures; if this repo remains the runtime head next session, the follow-up should be canonical FCOS sync / queue advancement rather than another local template slice.
- Validation run:
  - `bash ./scripts/sync-l0-fixtures.sh` (pass)
  - `bash ./scripts/check-l0-generation.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `copier-template/copier/tpl-agent-repo/governance/README.md`
  - `copier-template/copier/tpl-agent-repo/scripts/check-task-scope-snapshots.sh`
  - `copier-template/copier/tpl-org-repo/governance/README.md`
  - `copier-template/copier/tpl-org-repo/scripts/check-task-scope-snapshots.sh`
  - `copier-template/scripts/check-template-ci.sh`
  - `copier-template/scripts/install-hooks.sh`
  - `scripts/check-l0-generation.sh`
  - `scripts/check-l0-guardrails.sh`
  - `diary/2026-03-30--feat-ak-task-scope-agent-org-rollout.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session.
  - If `FCOS-M36-04` still resolves here, treat the repo-local code slice as complete and advance the canonical FCOS state / mirror instead of starting another local template change.
  - If the runtime-resolved head moved elsewhere, follow the new head from the resolver rather than this mirror note.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
