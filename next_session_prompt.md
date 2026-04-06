# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: NO RUNTIME FCOS HEAD IS CURRENTLY RESOLVED; KEEP THIS REPO IN MIRROR-ONLY / OPERATOR-DIRECTED POSTURE

The live runtime-resolved FCOS queue currently resolves to `none` (`cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`).
Repo-local FCOS slices `#738`, `#820`, `#821`, `#851`, `#281`, and `#791` are closed; do not reopen them for mirror-only work.
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
9. `diary/2026-04-05--review-full-adversarial-stack.md`
10. `diary/2026-04-05--feat-negative-path-nexus-hardening.md`
11. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Attended repo-local AK task `#791` and determined it had already been implemented in a different way via commit `9f98e48` (`docs(l2): clarify profile toggles are metadata-only`), then reconciled AK/runtime state and closed the task.
- Outcome:
  - Verified the landed implementation already chose the `metadata-only` path for L2 `enable_community_pack`, `enable_release_pack`, and `enable_vouch_gate` toggles across `tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`, and `tpl-monorepo`.
  - Confirmed the regression in `scripts/check-l0-generation.sh` still proves toggle-on vs toggle-off L2 renders are identical apart from answers files while README text documents the metadata-only contract.
  - Closed AK task `#791` with evidence pointing at the original implementation commit plus current validation.
  - Captured the operational closeout in `diary/2026-04-06--ops-task-791-metadata-only-closeout.md`.
  - Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` and confirmed the live FCOS resolver currently returns `[]` / `none`, so this repo should remain mirror-only / operator-directed unless the operator explicitly selects backlog work here.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
  - `bash ./scripts/check-l0.sh`
- Files of interest:
  - `diary/2026-04-05--docs-l2-toggle-metadata-only-contract.md`
  - `scripts/check-l0-generation.sh`
  - `docs/profile-governance-policy.md`
  - `next_session_prompt.md`
  - `diary/2026-04-06--ops-task-791-metadata-only-closeout.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session; the live resolver currently returns `none`, so operator direction should choose the next slice explicitly.
  - In this repo, treat repo-local tasks `#738`, `#820`, `#821`, `#851`, `#281`, and `#791` as closed implementation slices. If `#794` still appears in `task ready`, treat that as stale local AK state until the DB/storage drift is repaired.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md diary/2026-04-06--ops-task-791-metadata-only-closeout.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
