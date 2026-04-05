# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: NO RUNNABLE FCOS HEAD; FOLLOW OPERATOR DIRECTION OR REQUERY

The runtime-resolved FCOS queue currently resolves to `none` (`cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` returns `[]`).
Repo-local FCOS slice `#738` remains closed; do not reopen it.
If the operator gives an explicit repo-local AK task, follow that task. Otherwise re-run the FCOS resolver first, then fall back to the repo-local ready queue only if the operator wants backlog work here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `none`
- Last synced runtime-resolved FCOS repo set (mirror-only, rerun the resolver instead of trusting this line):
  - none
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
  - Claimed repo-local AK task `#792`, expanded the tpl-project-repo language matrix to cover Node and TypeScript, aligned stack-contract wording with the emitted `workspace-local-unpinned` provenance, hardened copied `copier-answers.sh` helpers/parity checks across L0/L1/L2 surfaces, refreshed fixtures, and updated the handoff mirror now that the FCOS runnable queue is empty.
- Outcome:
  - `tpl-project-repo` now preserves `package.json` for both Node and TypeScript software-pack renders while keeping `tsconfig.json` TypeScript-only.
  - `scripts/check-l0-generation.sh`, `scripts/check-l0-fixtures.sh`, and `scripts/sync-l0-fixtures.sh` now exercise/store matrix fixtures for Python, Node, TypeScript, Rust, and Elixir project repos plus the monorepo package-language matrix.
  - Stack-contract docs/templates now describe `policy/stack-lane.json` as the source of the declared upstream lane command instead of overstating pinning when the emitted provenance is `workspace-local-unpinned`.
  - Shared `copier-answers.sh` copies are hardened against unsupported tagged YAML fallback parsing and parity-checked across generated L0/L1/L2 surfaces.
  - Validation evidence `#416` records `validation:check-l0 = pass` for task `#792`.
  - `AK-281`, `#791`, `#793`, and `#794` remain ready repo-local backlog items; none should be substituted automatically for FCOS work unless the operator asks.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` (`[]`, next issue id `none`)
  - `bash ./scripts/check-l0-generation.sh` (pass)
  - `bash ./scripts/check-l0-fixtures.sh` (pass)
  - `bash ./scripts/check-l0.sh` (pass)
- Files of interest:
  - `scripts/check-l0-generation.sh`
  - `scripts/check-l0-fixtures.sh`
  - `scripts/sync-l0-fixtures.sh`
  - `copier-template/copier/tpl-project-repo/copier.yml`
  - `copier-template/copier/tpl-project-repo/docs/tech-stack.local.md.j2`
  - `copier-template/copier/tpl-package/docs/tech-stack.local.md.j2`
  - `copier-template/copier/tpl-monorepo/docs/tech-stack.local.md.j2`
  - `copier-template/scripts/check-template-ci.sh`
  - `scripts/lib/copier-answers.sh`
  - `fixtures/matrix/tpl-project-repo/node/`
  - `fixtures/matrix/tpl-project-repo/typescript/`
  - `diary/2026-04-05--fix-nexus-helper-parity-language-matrix-and-stack-wording.md`
  - `docs/learnings/2026-04-05-shared-helper-copies-need-parity-checks.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session; the runnable FCOS queue is currently empty.
  - Do not reopen task `#738`; that FCOS slice is already closed locally.
  - Do not reopen task `#792` unless a regression appears in Node/TypeScript matrix coverage, stack-contract wording, or helper parity.
  - If the operator wants backlog work in this repo, pick from the ready queue explicitly instead of inferring a new FCOS-local slice.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md diary/2026-04-05--fix-nexus-helper-parity-language-matrix-and-stack-wording.md docs/learnings/2026-04-05-shared-helper-copies-need-parity-checks.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
