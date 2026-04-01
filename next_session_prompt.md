# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FOLLOW THE RUNTIME-RESOLVED FCOS QUEUE; THE LOCAL M36-06 TEMPLATE SLICE IS DONE

The runtime-resolved FCOS head now includes `FCOS-M36-06` across `holdingco/governance-kernel` and `core/tpl-template-repo`.
This repo has completed the template-side `AK-553` slice for that issue.
If the resolver still returns `FCOS-M36-06`, continue from governance-kernel closeout / issue-completion surfaces rather than inventing more local template changes here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M36-06`
- Last synced runtime-resolved FCOS repos (mirror-only, rerun the resolver instead of trusting this line):
  - `holdingco/governance-kernel`
  - `core/tpl-template-repo`
- Anti-drift cadence policy:
  - loop-owned via `~/ai-society/holdingco/governance-kernel/governance/fcos/loops-registry.json` plugin `loop.fcos.drift.audit`

## READ-FIRST ALLOWLIST
1. `AGENTS.md`
2. `README.md`
3. `copier-template/docs/dev/task-scope-migration-playbook.md`
4. `docs/learnings/2026-03-13-stable-core-thin-adapters-for-multi-surface-systems.md`
5. `docs/learnings/2026-03-13-recurring-operation-languages-should-become-explicit.md`
6. `tips/meta/tip-0010-stable-core-thin-adapters-for-multi-surface-systems.md`
7. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Re-ran the runtime-resolved FCOS queue lookup, claimed `AK-553`, published the template-side migration/deprecation playbook for AK-native task-scope adoption, clarified the brownfield boundary across L0/L1/L2 docs, and re-synced fixtures.
- Outcome:
  - Added the canonical template-side playbook at `copier-template/docs/dev/task-scope-migration-playbook.md` and propagated it into the rendered L1 fixture at `fixtures/l1/template-repo/docs/dev/task-scope-migration-playbook.md`.
  - L0 operator docs now point to one explicit migration path for this slice:
    - `README.md`
    - `docs/dev/README.md`
    - `docs/l1-adoption-playbook.md`
    - `docs/l2-transition-playbook.md`
  - L1/L2 template docs now make the deprecation boundary explicit:
    - export `AK-<TASK-ID>.snapshot.json` first
    - keep legacy `governance/task-scopes/AK-*.json` files only as temporary compatibility fallback
    - remove legacy manifest authoring from the primary workflow once snapshot checks pass
    - do not invent task-scope files when repo-default scope still applies
  - `copier-template/copier/tpl-project-repo/next_session_prompt.md` now marks snapshots as frozen exports and legacy `AK-*.json` manifests as compatibility-only, so the handoff surface no longer implies dual authority.
  - If `just fcos-runnable` still resolves to `FCOS-M36-06`, the next work should happen in governance-kernel closeout / issue-completion surfaces rather than as another new local template slice here.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` (`FCOS-M36-06` includes `holdingco/governance-kernel` + `core/tpl-template-repo`)
  - `bash ./scripts/check-doc-references.sh` (pass)
  - `bash ./scripts/sync-l0-fixtures.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `copier-template/docs/dev/task-scope-migration-playbook.md`
  - `README.md`
  - `docs/dev/README.md`
  - `docs/l1-adoption-playbook.md`
  - `docs/l2-transition-playbook.md`
  - `copier-template/README.md.jinja`
  - `copier-template/governance/README.md.jinja`
  - `copier-template/copier/tpl-project-repo/next_session_prompt.md`
  - `diary/2026-04-01--docs-fcos-m36-06-task-scope-migration-playbook.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session.
  - If `FCOS-M36-06` still resolves, continue in governance-kernel closeout/issue-completion surfaces rather than reopening this repo's docs without a new contradiction.
  - Do not substitute unrelated ready task `AK-281` for FCOS queue work unless the operator explicitly asks for that backlog item.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
