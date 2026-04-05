# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: NO RUNTIME FCOS HEAD IS CURRENTLY RESOLVED; KEEP THIS REPO IN MIRROR-ONLY / OPERATOR-DIRECTED POSTURE

The runtime-resolved FCOS queue currently resolves to `none` (`cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`).
Repo-local FCOS slices `#738`, `#820`, `#821`, and `#851` are closed; do not reopen them for mirror-only work.
Re-run the FCOS resolver first. If it still returns no runnable head, only fall back to the repo-local ready queue when the operator explicitly asks for backlog work here.

## RUNTIME-RESOLVED PRIORITY / NEXT ISSUE

- CURRENT PRIORITY (query, do not hardcode):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
- Next issue resolver (same command, mirror-only):
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable | jq -r '.[0].id // "none"'`
- Last synced runtime-resolved FCOS issue id (mirror-only, rerun the resolver instead of trusting this line):
  - `none`
- Last synced runtime-resolved FCOS repo set (mirror-only, rerun the resolver instead of trusting this line):
  - `none`
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
8. `diary/2026-04-05--ops-task-851-generic-launcher-wrapper-template-authority.md`
9. `diary/2026-04-05--review-full-adversarial-stack.md`
10. `diary/2026-04-05--feat-negative-path-nexus-hardening.md`
11. latest `diary/YYYY-MM-DD--type-scope-summary.md`

## SESSION CHECKPOINT (UPDATE BEFORE /commit)
- Work package executed this session:
  - First, resumed and completed repo-local AK task `#851`, codifying `core/tpl-template-repo` as the canonical distribution authority for the generic launcher wrappers against the M45 convergence receipt.
  - Then reviewed and hardened the negative-path shell/wrapper surfaces that still failed open despite the main L0 suite passing.
- Outcome:
  - Updated `AGENTS.md`, `README.md`, and new note `docs/project/2026-04-05-generic-launcher-wrapper-template-authority.md` so the launcher-wrapper authority split is explicit: runtime/reference owner in `softwareco/owned/agent-kernel`, canonical distribution authority in `core/tpl-template-repo`, rollout/proof reporting in `holdingco/infra/template-propagator`.
  - Captured the adversarial review in `diary/2026-04-05--review-full-adversarial-stack.md`.
  - Fixed `scripts/check-doc-references.sh` to fail closed on invalid override paths instead of silently falling back.
  - Hardened `scripts/rocs.sh` so empty/invalid vendored `tools/rocs-cli/` directories no longer hijack runner selection.
  - Hardened `scripts/lib/repo-surface.sh` so repo census follows symlinked repo surfaces.
  - Added early `rsync` dependency preflight to `scripts/migrate-l1-structure.sh`.
  - Strengthened `scripts/check-l0-adversarial.sh`, `scripts/check-l0-generation.sh`, `scripts/check-l0-guardrails.sh`, and `copier-template/scripts/check-template-ci.sh`, then propagated the shared helper/wrapper changes through templates and fixtures.
  - Captured the hardening slice in `diary/2026-04-05--feat-negative-path-nexus-hardening.md`.
  - Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` and confirmed the live FCOS resolver still returns `[]` / `none`, so this repo should stay in mirror-only / operator-directed posture unless the operator picks backlog work explicitly.
- Validation run:
  - `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
  - `git diff --check --cached`
  - `bash ./scripts/check-l0.sh`
- Files of interest:
  - `scripts/check-doc-references.sh`
  - `scripts/rocs.sh`
  - `scripts/lib/repo-surface.sh`
  - `scripts/migrate-l1-structure.sh`
  - `scripts/check-l0-adversarial.sh`
  - `scripts/check-l0-generation.sh`
  - `scripts/check-l0-guardrails.sh`
  - `copier-template/scripts/check-template-ci.sh`
  - `diary/2026-04-05--review-full-adversarial-stack.md`
  - `diary/2026-04-05--feat-negative-path-nexus-hardening.md`
  - `next_session_prompt.md`
- Blockers / follow-up:
  - Re-run `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before starting another session; the current resolver returns `none`, so operator direction should choose the next slice explicitly.
  - In this repo, treat repo-local tasks `#738`, `#820`, `#821`, and `#851` as closed implementation slices. If the operator wants backlog work here, pick explicitly from `AK-281` or `#791`; if `#794` still appears in `task ready`, treat that as stale local AK state until the DB/storage drift is repaired.
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md scripts/check-doc-references.sh scripts/rocs.sh scripts/lib/repo-surface.sh scripts/migrate-l1-structure.sh scripts/check-l0-adversarial.sh scripts/check-l0-generation.sh scripts/check-l0-guardrails.sh copier-template/copier/tpl-agent-repo/scripts/lib/repo-surface.sh.j2 copier-template/copier/tpl-agent-repo/scripts/rocs.sh.j2 copier-template/copier/tpl-monorepo/scripts/lib/repo-surface.sh.j2 copier-template/copier/tpl-monorepo/scripts/rocs.sh.j2 copier-template/copier/tpl-org-repo/scripts/lib/repo-surface.sh.j2 copier-template/copier/tpl-org-repo/scripts/rocs.sh.j2 copier-template/copier/tpl-project-repo/scripts/lib/repo-surface.sh.j2 copier-template/copier/tpl-project-repo/scripts/rocs.sh.j2 copier-template/scripts/check-template-ci.sh copier-template/scripts/lib/repo-surface.sh copier-template/scripts/rocs.sh fixtures/l1/template-repo/copier/tpl-agent-repo/scripts/lib/repo-surface.sh.j2 fixtures/l1/template-repo/copier/tpl-agent-repo/scripts/rocs.sh.j2 fixtures/l1/template-repo/copier/tpl-monorepo/scripts/lib/repo-surface.sh.j2 fixtures/l1/template-repo/copier/tpl-monorepo/scripts/rocs.sh.j2 fixtures/l1/template-repo/copier/tpl-org-repo/scripts/lib/repo-surface.sh.j2 fixtures/l1/template-repo/copier/tpl-org-repo/scripts/rocs.sh.j2 fixtures/l1/template-repo/copier/tpl-project-repo/scripts/lib/repo-surface.sh.j2 fixtures/l1/template-repo/copier/tpl-project-repo/scripts/rocs.sh.j2 fixtures/l1/template-repo/scripts/check-template-ci.sh fixtures/l1/template-repo/scripts/lib/repo-surface.sh fixtures/l1/template-repo/scripts/rocs.sh fixtures/l2/tpl-agent-repo/scripts/lib/repo-surface.sh fixtures/l2/tpl-agent-repo/scripts/rocs.sh fixtures/l2/tpl-monorepo/scripts/lib/repo-surface.sh fixtures/l2/tpl-monorepo/scripts/rocs.sh fixtures/l2/tpl-org-repo/scripts/lib/repo-surface.sh fixtures/l2/tpl-org-repo/scripts/rocs.sh fixtures/l2/tpl-project-repo/scripts/lib/repo-surface.sh fixtures/l2/tpl-project-repo/scripts/rocs.sh fixtures/matrix/tpl-monorepo/root/scripts/lib/repo-surface.sh fixtures/matrix/tpl-monorepo/root/scripts/rocs.sh fixtures/matrix/tpl-project-repo/elixir/scripts/lib/repo-surface.sh fixtures/matrix/tpl-project-repo/elixir/scripts/rocs.sh fixtures/matrix/tpl-project-repo/node/scripts/lib/repo-surface.sh fixtures/matrix/tpl-project-repo/node/scripts/rocs.sh fixtures/matrix/tpl-project-repo/python/scripts/lib/repo-surface.sh fixtures/matrix/tpl-project-repo/python/scripts/rocs.sh fixtures/matrix/tpl-project-repo/rust/scripts/lib/repo-surface.sh fixtures/matrix/tpl-project-repo/rust/scripts/rocs.sh fixtures/matrix/tpl-project-repo/typescript/scripts/lib/repo-surface.sh fixtures/matrix/tpl-project-repo/typescript/scripts/rocs.sh diary/2026-04-05--feat-negative-path-nexus-hardening.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
