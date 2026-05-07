---
summary: "Session note: 2026 03 30 Feat Ak Task Scope Snapshot Ci."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 30 feat ak task scope snapshot ci."
type: "reference"
---

# 2026-03-30 — enforce AK task-scope snapshot drift checks in generated repo CI

## What I Did
- Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` and confirmed the runtime head still resolves to `FCOS-M36-04` for `core/tpl-template-repo`.
- Claimed `AK-620` and translated the adversarial review findings into executable generated-repo guardrails.
- Added `scripts/check-task-scope-snapshots.sh` to the generated L1 template repo plus generated `tpl-project-repo` and `tpl-monorepo` surfaces.
- Wired generated CI so task-scope snapshots are checked against live AK state when present:
  - generated L1 `scripts/ci/full.sh`
  - generated `tpl-project-repo/scripts/ci/full.sh`
  - generated `tpl-monorepo/scripts/ci/full.sh`
- Fixed two latent full-lane problems that the new enforcement exposed while making the lane real rather than nominal:
  - `tpl-project-repo/scripts/ci/full.sh` now captures parallel subprocess exit codes correctly instead of losing failures through `! wait ...`
  - generated project/monorepo/L1 full lanes now call `./scripts/ak.sh work-items check --repo . ...`, matching the wrapper contract that actually keeps work-item projections in sync
- Updated generated governance/README surfaces so operators know checked-in `governance/task-scopes/AK-<TASK-ID>.snapshot.json` files can be validated via `./scripts/check-task-scope-snapshots.sh` and are enforced by `./scripts/ci/full.sh`.
- Extended generated template CI to cover the new behavior end-to-end:
  - positive L1 / project / monorepo snapshot checks against a temp AK DB
  - rejection of foreign task snapshots in generated project repos
  - rejection of drifted snapshot content in generated monorepos
- Re-synced L0 fixtures after the new helper/CI/doc surface landed.

## Why This Slice Was Bounded
- I kept the slice focused on project/monorepo/L1 generated-repo enforcement, which is the debt called out by `AK-620`.
- I did not yet change placeholder wording like `<AK-ID>` vs numeric task IDs or extend the rollout to `tpl-agent-repo` / `tpl-org-repo`; that remains the next follow-up in `AK-621`.

## Validation
- `bash ./scripts/check-l0-generation.sh`
- `bash ./scripts/check-l0.sh`

## Files
- `copier-template/scripts/check-task-scope-snapshots.sh`
- `copier-template/scripts/ci/full.sh`
- `copier-template/scripts/check-template-ci.sh`
- `copier-template/scripts/install-hooks.sh`
- `copier-template/governance/README.md.jinja`
- `copier-template/README.md.jinja`
- `copier-template/copier/tpl-project-repo/scripts/check-task-scope-snapshots.sh`
- `copier-template/copier/tpl-project-repo/scripts/ci/full.sh`
- `copier-template/copier/tpl-project-repo/README.md.j2`
- `copier-template/copier/tpl-project-repo/governance/README.md`
- `copier-template/copier/tpl-monorepo/scripts/check-task-scope-snapshots.sh`
- `copier-template/copier/tpl-monorepo/scripts/ci/full.sh`
- `copier-template/copier/tpl-monorepo/README.md.j2`
- `copier-template/copier/tpl-monorepo/governance/README.md`
- `scripts/check-l0-guardrails.sh`
- `fixtures/`
- `next_session_prompt.md`
- `diary/2026-03-30--feat-ak-task-scope-snapshot-ci.md`

## Follow-up
- Complete `AK-620` after the session mirror is updated and the repo commit lands.
- Re-run the runtime FCOS resolver next session; if `FCOS-M36-04` still points here, the next repo-local slice should be `AK-621` (`Extend AK-native task-scope rollout to tpl-agent-repo/tpl-org-repo and fix task-id guidance`).
