# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: KEEP L0 AK-FIRST AND TRUTHFUL

This repo maintains the L0 template that seeds L1/L2 repositories.
Current priority is to preserve the new AK-first authority model for repo-local work-items and prevent regressions back to silent JSON-first behavior.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Resolved at checkpoint update time:
  - `FCOS-M4-03`
- Anti-drift cadence policy:
  - loop-owned via `~/ai-society/holdingco/governance-kernel/governance/fcos/loops-registry.json` plugin `loop.fcos.drift.audit`

## READ-FIRST ALLOWLIST
1. `AGENTS.md`
2. `README.md`
3. `copier-template/docs/dev/tpl-project-repo-file-contract.md`
4. `copier-template/scripts/ak.sh`
5. `copier-template/copier/tpl-project-repo/governance/README.md`
6. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Make dormant AK work-items integration alive at L0 and distribute the AK authority model via AGENTS layering.
- Outcome:
  - Added deterministic repo-local `scripts/ak.sh` wrapper strategy for L1/L2 surfaces.
  - Switched template CI from vendored-`crates/ak-cli` gating to AK-first drift checks with explicit failure when AK is unavailable.
  - Rewrote project/monorepo work-items docs so AK is authoritative and `governance/work-items.json` is the checked-in projection.
  - Added monorepo work-items projection files to make that archetype truthful.
  - Added guardrails preventing regression to silent AK skip behavior.
  - Updated workspace and repo AGENTS policy so AK authority is ambiently distributed from parent context.
- Validation run:
  - `bash ./scripts/check-l0-guardrails.sh` (pass)
  - `bash ./scripts/check-l0-generation.sh` (pass)
  - `bash ./scripts/check-l0-fixtures.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `copier-template/scripts/ak.sh`
  - `copier-template/copier/tpl-project-repo/**`
  - `copier-template/copier/tpl-monorepo/**`
  - `copier-template/scripts/check-template-ci.sh`
  - `scripts/check-l0-guardrails.sh`
  - `/home/tryinget/ai-society/AGENTS.md`
- Blockers / follow-up:
  - Workspace root `~/ai-society` is a separate dirty repo; commit parent-level AGENTS changes separately from `core/tpl-template-repo` work.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
