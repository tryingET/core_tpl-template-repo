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
  - Archaeology pass over ontology-lsp to crystallize reusable architecture guidance for stable cores, thin adapters, ports, and DSL/formalization placement.
- Outcome:
  - Captured ontology-lsp archaeology in repo-local diary.
  - Added a crystallized learning for the main architecture pattern: stable core + thin adapters + ports at real seams.
  - Added a linked crystallized learning for the DSL/formalization sub-pattern inside the stable core.
  - Added `TIP-0010` so the architecture rule can propagate across future AI Society repos.
  - Kept the main architecture learning DRY by linking to the DSL learning instead of duplicating it.
- Validation run:
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `docs/learnings/2026-03-13-stable-core-thin-adapters-for-multi-surface-systems.md`
  - `docs/learnings/2026-03-13-recurring-operation-languages-should-become-explicit.md`
  - `tips/meta/tip-0010-stable-core-thin-adapters-for-multi-surface-systems.md`
  - `diary/2026-03-13--research-ontology-lsp-adapter-architecture-archaeology.md`
  - `diary/2026-03-13--docs-dsl-learning-linkage.md`
- Blockers / follow-up:
  - No blocking repo-local follow-up known; use the runtime-resolved FCOS queue to choose the next slice.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
