# 2026-03-30 — harden AK-native task-scope regression coverage

## What I Did
- Re-ran `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable` before changing code and confirmed the runtime head still resolves to `FCOS-M36-04` for `core/tpl-template-repo`.
- Claimed `AK-548` and tightened the regression surface around the AK-native task-scope adoption that had already been propagated through descendant templates in `AK-547`.
- Extended `scripts/check-l0-guardrails.sh` so it now asserts the intended task-scope contract at both template-source and fixture levels:
  - `tpl-project-repo` keeps AK-authored `governance/task-scopes/AK-<id>.snapshot.json` wording plus the transitional-scaffolding warning
  - `tpl-monorepo` keeps task-scope authority at the monorepo root
  - `tpl-package` inherits task-scope authority from the monorepo root and must not ship a standalone `scripts/ak.sh`
- Extended `scripts/check-l0-generation.sh` so rendered outputs are checked directly, not only through fixture diffs:
  - generated project repos must keep task-scope snapshot instructions in `README.md`, `governance/README.md`, and `next_session_prompt.md`
  - generated monorepos must keep the root-owned task-scope wording
  - generated package members must not create standalone `scripts/ak.sh` or `governance/task-scopes/` state
- Re-ran the full L0 validation gate to verify the stronger assertions pass end-to-end.

## Why This Slice Was Bounded
- I did not change the task-scope wording itself; `AK-547` already propagated and fixture-synced that surface.
- I kept this slice focused on executable regression coverage so future edits cannot silently drift the new AK-native contract.

## Validation
- `bash ./scripts/check-l0-guardrails.sh`
- `bash ./scripts/check-l0-generation.sh`
- `bash ./scripts/check-l0.sh`

## Files
- `scripts/check-l0-guardrails.sh`
- `scripts/check-l0-generation.sh`
- `next_session_prompt.md`
- `diary/2026-03-30--test-ak-task-scope-regression-coverage.md`

## Follow-up
- `AK-548` should complete once the session mirror is updated.
- The runtime FCOS resolver still reports `FCOS-M36-04`; before starting another local slice, re-run the resolver and confirm whether canonical FCOS state needs to move now that the repo-local AK chain (`AK-546` → `AK-548`) is complete.
