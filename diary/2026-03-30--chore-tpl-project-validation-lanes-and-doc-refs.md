# 2026-03-30 — tpl-project validation lanes + doc-reference gate hardening

## What I Did
- Read `next_session_prompt.md`, the read-first repo docs, and checked AK state for the requested `AK-538` reference.
- Confirmed `AK-538` is already closed in `softwareco/owned/agent-kernel`, so I treated this repo session as finishing the in-progress `tpl-template-repo` checkout changes and getting the repo back to a validated state.
- Kept the staged/unstaged work already present in the tree and pushed it through to a green L0 validation pass.
- Added the repo-level doc-reference gate (`scripts/check-doc-references.sh`) into `scripts/check-l0.sh` and aligned the linked docs/paths it validates.
- Finished the tpl-project CI lane split by teaching the template/docs/fixtures about `scripts/ci/fast.sh` and making `full.sh` run `fast.sh` first, then heavier AK/ROCS checks.
- Preserved the already-started ROCS GitLab cache-path sanitization changes and resynchronized all affected fixtures.
- Fixed the generated-L1 validation failure by teaching `copier-template/scripts/check-template-ci.sh` to create a temporary AK DB, register generated repos there, and then run `work-items check` against that deterministic temp state.
- Removed a stray generated `__pycache__` directory from the embedded tpl-project ROCS CLI template source.
- Ran `bash ./scripts/sync-l0-fixtures.sh` and then `bash ./scripts/check-l0.sh` to verify the full L0 surface.

## What Surprised Me
- The main blocker was not the new doc-reference gate or the fast/full lane split itself; it was that generated-template CI now exercised `ak work-items check` against temp repos that were never registered, so the validation harness needed its own isolated AK registration flow.
- A transient `__pycache__` directory inside the vendored tpl-project ROCS CLI template was enough to fail both guardrail and generation checks.

## Patterns
- When templates start enforcing stronger runtime truth, their generator-time validation harness must simulate the same runtime prerequisites instead of silently bypassing them.
- Adding a cheap `fast` lane only pays off when the heavier lane is explicit about calling it first and when docs/prompts/fixtures all teach the same lane contract.

## Crystallization Candidates
- None yet; this feels like repo-local validation plumbing rather than a new reusable learning.
