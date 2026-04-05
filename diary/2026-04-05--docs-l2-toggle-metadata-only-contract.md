# 2026-04-05 — docs/l2-toggle-metadata-only-contract

## Context
- Operator directed work to repo-local AK task `#791`: decide whether L2 profile toggles (`enable_community_pack`, `enable_release_pack`, `enable_vouch_gate`) should gain real semantics or be documented as metadata-only.
- Existing template state was inconsistent: `tpl-project-repo` already documented the toggles as metadata-only, while `tpl-agent-repo`, `tpl-org-repo`, and `tpl-monorepo` exposed the same flags without clearly stating that they currently do not scaffold extra L2 overlays.

## Work performed
- Normalized L2 Copier help text so all four L2 archetypes describe the three toggles as inherited compatibility metadata.
- Updated L2 template READMEs so agent/org/monorepo generated repos now explicitly say those toggles are metadata-only.
- Clarified the root `README.md` and `docs/profile-governance-policy.md` so repo-level governance guidance no longer implies concrete L2 pack overlays.
- Added a regression in `scripts/check-l0-generation.sh` that renders L2 repos with toggles off vs on and asserts that non-answer-file output stays identical while the generated README still documents the metadata-only contract.
- Resynced checked-in L1/L2 fixtures after the template doc/help updates.

## Validation
- `bash ./scripts/check-l0-generation.sh`
- `bash ./scripts/check-l0-fixtures.sh`
- `bash ./scripts/check-l0.sh`

## Notes
- `./scripts/ak.sh task claim 791 --agent pi` failed repeatedly with a foreign-key error in the current Agent Kernel runtime, so task attendance proceeded by executing the scoped repo changes directly.
- `./scripts/ak.sh task scope update 791 ...` also failed with `Task not found` despite `task show` / `task scope show` succeeding.
- The task result should record the implementation + validation evidence and the AK mutation failure as runtime friction to inspect separately if it recurs.
