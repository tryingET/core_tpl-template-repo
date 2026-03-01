# 2026-03-01 — Replace stale status/next-steps with next-session prompt in tpl-project baseline

## What I Did
- Audited `next_session_prompt.md` patterns across:
  - `holdingco/governance-kernel`
  - `softwareco/owned/*`
  - this repository (`core/tpl-template-repo`)
- Replaced `tpl-project-repo` baseline docs split:
  - removed `docs/dev/status.md`
  - removed `docs/dev/next_steps.md`
  - added root `next_session_prompt.md` template with anti-stale contract
- Updated template structure docs in:
  - `copier-template/copier/tpl-project-repo/README.md.j2`
  - `copier-template/docs/dev/tpl-project-repo-file-contract.md`
- Regenerated fixtures via `bash ./scripts/sync-l0-fixtures.sh`.
- Validated full L0 checks with `bash ./scripts/check-l0.sh` (all green).

## What Surprised Me
- The old `status.md` + `next_steps.md` files were only present in `tpl-project-repo`, not all archetypes.
- Existing `next_session_prompt.md` examples vary a lot (19 to 281 lines), which strongly affects staleness risk.

## Patterns
- Best reusable shape is a hybrid:
  - strict sections (`read-first`, `execution mode`, `checkpoint`) from governance-kernel
  - concise format from dep-viz
- Staleness increases quickly when prompt files become historical logs instead of current-session handoff contracts.

## Crystallization Candidates
- → docs/learnings/: “single handoff prompt beats status+next_steps split for session continuity”
- → tips/meta/: “anti-stale session-prompt skeleton with source-of-truth map + bounded checkpoint”
