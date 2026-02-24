# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start work immediately.
Do not ask for permission to begin.

## READ-FIRST ALLOWLIST (ONLY THESE)
1. `~/ai-society/holdingco/governance-kernel/docs/dev/fcos-convergence-rollup-plan.md`
2. `~/ai-society/holdingco/governance-kernel/docs/dev/fcos-convergence-issue-set.md`

If blocked, read only the minimum additional file needed to unblock.

## AUTHORITY SPLIT (NON-NEGOTIABLE)
- Canonical issue status authority: `~/ai-society/holdingco/governance-kernel/docs/dev/fcos-convergence-issue-set.md`.
- This file's Session Checkpoint is a transient mirror for local continuity only.
- Program naming is `FCOS`; canonical issue IDs are `FCOS-*`; `RCOS-*` remains a legacy alias during transition.
- `ROCS` is reserved for the CLI/tool namespace (`core/rocs-cli`).

## EXECUTION MODE (ONE SESSION = ONE ISSUE)
Apply cognitive frameworks from `~/steve/prompts/prompt-snippets.md` (at minimum: INVERSION, TELESCOPIC, NEXUS, ESCAPE HATCH, KNOWLEDGE CRYSTALLIZATION).
1. Parse `fcos-convergence-issue-set.md`.
2. Pick the first unchecked issue with dependencies satisfied (lowest milestone first).
3. Execute that issue end-to-end (not partial planning only).
4. Run the issue’s deterministic validation/acceptance checks.
5. Update issue status/checklist in `~/ai-society/holdingco/governance-kernel/docs/dev/fcos-convergence-issue-set.md` and then add a concise mirror note here under Session Checkpoint.

## NON-NEGOTIABLES
- Control-plane authority remains in `holdingco/governance-kernel`.
- Deterministic checks are acceptance gates.
- Mainline-safe behavior: no irreversible actions without rollback path.
- `softwareco/owned/testers` is proving lane only, never policy authority.

## CURRENT PRIORITY
Execute **M1** issues in order:
- FCOS-M1-01
- FCOS-M1-02
- FCOS-M1-03
- FCOS-M1-04
- FCOS-M1-05

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Issue executed: none (out-of-band policy correction: diary authority moved to repo-local `./diary/`)
- Outcome: partial
- Files changed:
  - `~/ai-society/core/tpl-template-repo/AGENTS.md`
  - `~/ai-society/core/tpl-template-repo/CONTRIBUTING.md`
  - `~/ai-society/core/tpl-template-repo/README.md`
  - `~/ai-society/core/tpl-template-repo/diary/*`
  - `~/ai-society/core/tpl-template-repo/copier-template/**/diary/*`
  - `~/ai-society/core/tpl-template-repo/copier-template/**/AGENTS.md*`
  - `~/ai-society/core/tpl-template-repo/copier-template/**/README.md*`
  - `~/ai-society/core/tpl-template-repo/scripts/check-l0-guardrails.sh`
  - `~/ai-society/core/tpl-template-repo/copier-template/scripts/check-template-ci.sh`
  - `~/ai-society/core/tpl-template-repo/tips/meta/tip-0002-agent-diary.md`
  - `~/ai-society/core/tpl-template-repo/tips/meta/tip-0003-selective-kes-lane-templates.md`
- Validation run:
  - `bash ./scripts/sync-l0-fixtures.sh`
  - `bash ./scripts/check-l0.sh`
- Next issue: FCOS-M1-02
- Blockers/risks: FCOS M1-02 remains open; this commit only normalizes KES diary location and guardrails.

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).

`/commit` must:
- sync this file’s Session Checkpoint,
- create clear logical commit(s),
- include why + validation in commit body.
