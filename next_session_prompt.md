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
  - `FCOS-M35-01`
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
  - Finished the in-progress tpl-project validation/workflow hardening already present in the checkout: added the doc-reference gate, taught tpl-project repos a `fast` + `full` CI lane split, and fixed generated-template validation to use a temporary AK DB/registration flow for work-items checks.
- Outcome:
  - Repo-level docs now carry corrected tracked relative links and `scripts/check-doc-references.sh` is part of `scripts/check-l0.sh`.
  - tpl-project template/docs/prompts/fixtures now teach `./scripts/ci/fast.sh` as the cheap guardrail lane and `./scripts/ci/full.sh` as the heavier lane that runs `fast.sh` first.
  - Generated L1 template CI now bootstraps a temp AK DB and registers generated repos before running `work-items check`, so L0 generation validation passes without depending on live workspace repo registration.
  - Removed a stray embedded `__pycache__` artifact and re-synced fixtures.
- Validation run:
  - `bash ./scripts/sync-l0-fixtures.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `scripts/check-doc-references.sh`
  - `scripts/check-l0.sh`
  - `docs/l1-adoption-playbook.md`
  - `docs/l2-transition-playbook.md`
  - `copier-template/copier/tpl-project-repo/scripts/ci/fast.sh`
  - `copier-template/copier/tpl-project-repo/scripts/ci/full.sh`
  - `copier-template/scripts/check-template-ci.sh`
  - `diary/2026-03-30--chore-tpl-project-validation-lanes-and-doc-refs.md`
- Blockers / follow-up:
  - No blocking local follow-up from this slice is known; return to the runtime-resolved FCOS queue for the next repo-local slice.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
