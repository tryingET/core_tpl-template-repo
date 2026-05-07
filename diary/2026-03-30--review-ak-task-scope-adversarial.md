---
summary: "Session note: 2026 03 30 Review Ak Task Scope Adversarial."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 30 review ak task scope adversarial."
type: "reference"
---

# 2026-03-30 — adversarial review of AK task-scope adoption commits

## Scope
- Reviewed the last three commits in `core/tpl-template-repo`:
  - `7f38bab` — checkpoint mirror sync
  - `b3ff71e` — AK task-scope propagation across descendant templates
  - `52a6721` — regression checks for the propagated task-scope wording
- Cross-checked against AK tasks `546`, `547`, `548`.

## Evidence gathered
- Inspected the new docs/prompts around `governance/task-scopes/AK-<AK-ID>.snapshot.json` in `tpl-project-repo`, `tpl-monorepo`, and `tpl-package` surfaces.
- Inspected current generated CI/runtime checks in:
  - `copier-template/copier/tpl-project-repo/scripts/ci/full.sh`
  - `copier-template/copier/tpl-monorepo/scripts/ci/full.sh`
  - `copier-template/scripts/check-template-ci.sh`
- Verified live AK behavior:
  - `./scripts/ak.sh task scope show 546`
  - `./scripts/ak.sh task scope export 47`
  - `./scripts/ak.sh task scope show AK-546` (fails: CLI expects numeric ID)
- Reproduced a silent-acceptance path in a temp generated `tpl-project-repo`:
  - exported foreign task `47` (repo=`softwareco/owned/pi-server`) into `governance/task-scopes/AK-47.snapshot.json`
  - `AK_DB=<tmp> ./scripts/ci/full.sh` still passed

## Main findings
1. The new task-scope snapshots are taught as repo-consumption artifacts, but generated CI never validates them.
2. The documented export flow is global-by-task-ID and does not force any repo-ownership sanity check, so foreign task snapshots can be committed locally.
3. The placeholder contract is copy-paste fragile: docs use `<AK-ID>` while the CLI rejects prefixed values like `AK-546`, and the new regression checks lock that wording in.

## Follow-up candidates
- Add a deterministic snapshot verification step for generated repos and for L0/L1 template CI.
- Add repo provenance / ownership validation before exporting a snapshot.
- Clarify placeholder naming (`<TASK_ID_NUMERIC>` or similar) and relax/update the wording checks accordingly.

## AK follow-up tasks created
- `#620` — `[FCOS-M36-04] Add generated-repo task-scope snapshot drift checks and CI enforcement`
  - depends on `#548`
- `#621` — `[FCOS-M36-04] Extend AK-native task-scope rollout to tpl-agent-repo/tpl-org-repo and fix task-id guidance`
  - depends on `#620`

## Interim conclusion
- No RFC yet. The current gap still looks like rollout/enforcement debt inside the already-decided M36 task-scope boundary, not a new unresolved System4D architecture split.
- If task `#620` proves that the validator surface cannot be owned cleanly in `tpl-template-repo` without duplicating governance-kernel/AK logic, then the next move should be a bounded cross-repo RFC or decision note about generic repo-side task-scope validation ownership.
