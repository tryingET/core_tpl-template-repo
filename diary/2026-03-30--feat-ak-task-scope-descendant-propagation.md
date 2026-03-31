# 2026-03-30 — propagate AK-native task-scope flow across descendant templates

## What I Did
- Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before touching code and confirmed the queue head had moved back to `FCOS-M36-04` for `core/tpl-template-repo`.
- Claimed `AK-547` and propagated the AK-native task-scope pattern into the descendant template chain that is actually exercised by this repo's fixture/generation checks:
  - `copier-template/copier/tpl-project-repo/**`
  - `copier-template/copier/tpl-monorepo/**`
  - `copier-template/copier/tpl-package/**`
- Updated those surfaces so they now say the same bounded thing:
  - explicit task scope is authored in AK
  - repo-side `governance/task-scopes/AK-<id>.snapshot.json` files are frozen exports for consumption
  - package/app members inherit task-scope authority from the monorepo root instead of inventing local AK state
- Re-synced the generated L1/L2/matrix fixtures so descendant docs stay aligned with the L0 source.
- Refreshed `next_session_prompt.md` so the handoff now reflects the current runtime queue head and points at `AK-548` as the immediate follow-up.

## Why This Slice Was Bounded
- I did not add new regression assertions beyond what existing generation/fixture checks already prove; that stays in `AK-548`.
- I kept the change at the documentation/prompt/governance surface level for descendants rather than introducing new baseline files or directories that would make task-scope support look mandatory everywhere.

## Validation
- `bash ./scripts/sync-l0-fixtures.sh`
- `bash ./scripts/check-l0.sh`

## Files
- `copier-template/copier/tpl-project-repo/README.md.j2`
- `copier-template/copier/tpl-project-repo/AGENTS.md.j2`
- `copier-template/copier/tpl-project-repo/governance/README.md`
- `copier-template/copier/tpl-project-repo/next_session_prompt.md`
- `copier-template/copier/tpl-monorepo/README.md.j2`
- `copier-template/copier/tpl-monorepo/AGENTS.md.j2`
- `copier-template/copier/tpl-monorepo/governance/README.md`
- `copier-template/copier/tpl-package/README.md.j2`
- `copier-template/copier/tpl-package/AGENTS.md.j2`
- `fixtures/l1/**`
- `fixtures/l2/**`
- `fixtures/matrix/**`
- `next_session_prompt.md`

## Follow-up
- `AK-548` — tighten regression checks around descendant task-scope adoption now that the surface is propagated.
- After `AK-548`, re-run the runtime FCOS resolver before assuming the next local slice.
