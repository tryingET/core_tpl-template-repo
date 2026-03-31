# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FOLLOW THE RUNTIME-RESOLVED FCOS QUEUE, BUT DO NOT START A NEW LOCAL SLICE UNLESS THE HEAD RETURNS HERE

The runtime-resolved FCOS head has moved off `core/tpl-template-repo` to `softwareco/owned/dspx` for `FCOS-M36-05`.
Treat the repo-local `FCOS-M36-04` slice as canonically closed and use this repo only as a mirror/handoff surface until the resolver points back here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M36-05`
- Last synced runtime-resolved FCOS repo (mirror-only, rerun the resolver instead of trusting this line):
  - `softwareco/owned/dspx`
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
  - Re-ran the runtime-resolved FCOS queue lookup, confirmed the repo-local `AK-546 -> AK-548 -> AK-620 -> AK-621` chain had already finished the code slice, closed canonical `FCOS-M36-04` in governance-kernel, refreshed FCOS portfolio/projection/direction surfaces, and updated this repo's handoff mirror.
- Outcome:
  - `FCOS-M36-04` is now `done` in `~/ai-society/holdingco/governance-kernel/governance/programs/fcos/work-items.json` with all three rollout tasks checked off and scheduler transition history recorded.
  - `just fcos-runnable` now resolves to `FCOS-M36-05` in `softwareco/owned/dspx`, so `core/tpl-template-repo` no longer owns the runtime FCOS head.
  - Governance-kernel closeout surfaces were refreshed for the canonical queue advance:
    - `governance/fcos/portfolio.yaml` progress now reflects `queued: 4` / `done: 57`
    - `docs/dev/fcos-convergence-issue-set.md` was re-rendered from the authoritative model
    - `governance/fcos/{causal-graph,events,scopes}.yaml` were re-synced
    - `docs/project/{strategic_goals,tactical_goals,operating_plan,fcos-direction-to-execution}.md` now point at `FCOS-M36-05`
  - Repo-local FCOS follow-up work is still blocked:
    - `AK-553` depends on `AK-552`
    - `FCOS-M36-06` depends on `FCOS-M36-05`
  - `AK-281` is still the only separately ready repo-local AK task, but it is unrelated to the runtime-resolved FCOS queue and should not replace the FCOS workflow without explicit operator direction.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-check` (pass)
  - `cd ~/ai-society/holdingco/governance-kernel && python3 scripts/rocs/check-fcos-handoff-sync.py` (pass)
  - `cd ~/ai-society/holdingco/governance-kernel && python3 scripts/rocs/render-fcos-issue-set.py --check` (pass)
  - `cd ~/ai-society/holdingco/governance-kernel && bash scripts/rocs/check-fcos-doc-drift.sh` (pass)
  - `cd ~/ai-society/holdingco/governance-kernel && just cg-check` (pass)
  - `bash ./scripts/check-session-checkpoint.sh` (pass)
- Files of interest:
  - `~/ai-society/holdingco/governance-kernel/governance/programs/fcos/work-items.json`
  - `~/ai-society/holdingco/governance-kernel/governance/fcos/portfolio.yaml`
  - `~/ai-society/holdingco/governance-kernel/docs/dev/fcos-convergence-issue-set.md`
  - `~/ai-society/holdingco/governance-kernel/governance/fcos/causal-graph.yaml`
  - `~/ai-society/holdingco/governance-kernel/governance/fcos/events.yaml`
  - `~/ai-society/holdingco/governance-kernel/governance/fcos/scopes.yaml`
  - `~/ai-society/holdingco/governance-kernel/docs/project/strategic_goals.md`
  - `~/ai-society/holdingco/governance-kernel/docs/project/tactical_goals.md`
  - `~/ai-society/holdingco/governance-kernel/docs/project/operating_plan.md`
  - `~/ai-society/holdingco/governance-kernel/docs/project/fcos-direction-to-execution.md`
  - `diary/2026-03-31--ops-fcos-m36-04-closeout-and-queue-advance.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session.
  - If `FCOS-M36-05` still resolves to `softwareco/owned/dspx`, leave this repo and follow that head instead of starting new local work.
  - If the runtime-resolved head later returns to this repo, the next local FCOS slice is `FCOS-M36-06` / `AK-553`, not another `FCOS-M36-04` template change.
  - Do not substitute unrelated ready task `AK-281` for FCOS queue work unless the operator explicitly asks for that backlog item.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
