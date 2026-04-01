# 2026-04-01 — publish template-side task-scope migration playbook

## What I Did
- Re-ran `just fcos-runnable` in `holdingco/governance-kernel` and confirmed the runtime-resolved FCOS head now includes `FCOS-M36-06` for `holdingco/governance-kernel` + `core/tpl-template-repo`.
- Claimed `AK-553` and published the template-side migration/deprecation playbook for AK-native task-scope adoption.
- Added the new canonical template-side playbook at `copier-template/docs/dev/task-scope-migration-playbook.md` and propagated it into the rendered L1 fixture.
- Updated the L0 operator docs (`README.md`, `docs/dev/README.md`, `docs/l1-adoption-playbook.md`, `docs/l2-transition-playbook.md`) so L1 adoption and L2 brownfield transitions now point to one explicit migration path.
- Updated the L1/L2 template surfaces so brownfield repos no longer have to infer the deprecation boundary from scattered wording:
  - L1 `README.md` + `governance/README.md`
  - L2 `tpl-project-repo`, `tpl-monorepo`, `tpl-agent-repo`, and `tpl-org-repo` README/governance docs
  - `tpl-project-repo/next_session_prompt.md` now calls snapshots frozen exports and marks legacy `AK-*.json` files as compatibility-only.
- Re-synced fixtures after the new doc and wording changes.

## Validation
- `bash ./scripts/check-doc-references.sh`
- `bash ./scripts/sync-l0-fixtures.sh`
- `bash ./scripts/check-l0.sh`

## Files
- `copier-template/docs/dev/task-scope-migration-playbook.md`
- `README.md`
- `docs/dev/README.md`
- `docs/l1-adoption-playbook.md`
- `docs/l2-transition-playbook.md`
- `copier-template/README.md.jinja`
- `copier-template/governance/README.md.jinja`
- `copier-template/copier/tpl-{project,monorepo,agent,org}-repo/{README.md.j2,governance/README.md}`
- `copier-template/copier/tpl-project-repo/next_session_prompt.md`
- synced fixtures under `fixtures/l1`, `fixtures/l2`, and `fixtures/matrix`

## Follow-up
- If `just fcos-runnable` still resolves to `FCOS-M36-06`, continue from the governance-kernel closeout/issue-completion surface rather than reopening the template docs here.
- Otherwise, follow the runtime-resolved FCOS head instead of inventing a new local slice.
