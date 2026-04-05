# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: FCOS-M44-01 IS NOW THE RUNNABLE HEAD; WORK THE BOUNDED TEMPLATE FOLLOW-THROUGH

The runtime-resolved FCOS queue currently resolves to `FCOS-M44-01` (`cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`).
Repo-local FCOS slice `#738` remains closed; do not reopen it.
The next bounded follow-through here is `FCOS-M44-01` repo-local task `#820`; if the operator gives that task explicitly, work it. Otherwise re-run the FCOS resolver first, then fall back to the repo-local ready queue only if the operator wants backlog work here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `FCOS-M44-01`
- Last synced runtime-resolved FCOS repo set (mirror-only, rerun the resolver instead of trusting this line):
  - `holdingco/governance-kernel`, `softwareco/owned/agent-kernel`, `core/tpl-template-repo`
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
8. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - Claimed and completed repo-local AK task `#793` to enforce `L0 -> L1 -> L2` recursion boundaries in code instead of relying on docs alone.
- Outcome:
  - Added machine-readable `contracts/layer-contract.yml` files across all L2 template archetypes and regenerated the rendered L1/L2/matrix fixtures so descendants now carry an explicit layer contract.
  - Hardened `scripts/new-l1-from-copier.sh` to verify it is running from an L0 root and to fail closed when the destination already declares a conflicting layer.
  - Hardened generated L1 `scripts/new-repo-from-copier.sh` with the same fail-closed destination-layer guard for `L1 -> L2` renders.
  - Updated generated `scripts/bootstrap-lane-root.sh` so lane-root baselines keep `contracts/` tracked instead of dropping the new layer contract from lane control-plane surfaces.
  - `scripts/check-l0-generation.sh`, `scripts/check-l0-guardrails.sh`, and generated `scripts/check-template-ci.sh` now assert the new contract presence + wrapper refusal behavior.
  - Validation evidence `#417` records `validation:check-l0 = pass` for task `#793`, and AK task `#793` is now `done`.
  - Current ready repo-local backlog includes `FCOS-M44-01` follow-through task `#820` alongside `AK-281`, `#791`, and `#794`; do not substitute one automatically unless the operator asks.
- Validation run:
  - `bash ./scripts/check-l0-generation.sh` (pass)
  - `bash ./scripts/check-l0-fixtures.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `scripts/new-l1-from-copier.sh`
  - `scripts/check-l0-generation.sh`
  - `scripts/check-l0-guardrails.sh`
  - `copier-template/scripts/new-repo-from-copier.sh`
  - `copier-template/scripts/bootstrap-lane-root.sh`
  - `copier-template/scripts/check-template-ci.sh`
  - `copier-template/copier/tpl-agent-repo/contracts/layer-contract.yml`
  - `copier-template/copier/tpl-org-repo/contracts/layer-contract.yml`
  - `copier-template/copier/tpl-project-repo/contracts/layer-contract.yml`
  - `copier-template/copier/tpl-monorepo/contracts/layer-contract.yml`
  - `copier-template/copier/tpl-package/contracts/layer-contract.yml`
  - `fixtures/l1/template-repo/`
  - `fixtures/l2/`
  - `fixtures/matrix/`
  - `diary/2026-04-05--feat-layer-contract-recursion-guardrails.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session; `FCOS-M44-01` is the mirrored runnable head right now, and operator direction still wins over backlog inference.
  - Existing older repos without `contracts/layer-contract.yml` remain compatibility-allowed if they predate this contract; tightening brownfield migration rules would be a separate follow-up.
  - If the operator wants backlog work here, pick explicitly from `FCOS-M44-01` task `#820`, `AK-281`, `#791`, or `#794`.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md diary/2026-04-05--feat-layer-contract-recursion-guardrails.md scripts/new-l1-from-copier.sh scripts/check-l0-generation.sh scripts/check-l0-guardrails.sh copier-template/scripts/new-repo-from-copier.sh copier-template/scripts/bootstrap-lane-root.sh copier-template/scripts/check-template-ci.sh copier-template/copier/tpl-agent-repo/contracts/layer-contract.yml copier-template/copier/tpl-org-repo/contracts/layer-contract.yml copier-template/copier/tpl-project-repo/contracts/layer-contract.yml copier-template/copier/tpl-monorepo/contracts/layer-contract.yml copier-template/copier/tpl-package/contracts/layer-contract.yml`
  - `bash ./scripts/sync-l0-fixtures.sh`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
