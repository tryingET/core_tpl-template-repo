---
summary: "Template-side migration playbook for moving existing repos from hand-authored task-scope manifests to AK-authored frozen snapshots."
read_when:
  - "Adopting the FCOS-M36-06 task-scope migration slice into an existing L1 template repo."
  - "Migrating a brownfield L2 repo away from hand-authored `governance/task-scopes/AK-*.json` files."
  - "Removing contradictory task-scope workflow text from template docs, handoffs, or CI guidance."
system4d:
  container:
    boundary: "Template/operator guidance for L1 and L2 adoption of the AK-native task-scope contract."
    edges:
      - "../../README.md.jinja"
      - "../../governance/README.md.jinja"
      - "./tpl-project-repo-file-contract.md"
      - "governance-kernel task-scope migration/deprecation contract"
  compass:
    driver: "Give template operators one bounded migration path that preserves deterministic repo validation without recreating dual authority."
    outcome: "Existing repos can adopt AK-authored task scope task by task and retire legacy manifest authoring from the happy path."
  engine:
    invariants:
      - "AK authors explicit task scope; repos consume frozen snapshot exports."
      - "Repo-default scope needs neither a snapshot nor a legacy manifest."
      - "Hand-authored `governance/task-scopes/AK-*.json` files are compatibility-only, not co-equal authority."
      - "Once a repo is using explicit AK scope plus snapshot validation, missing or stale snapshots must fail closed."
  fog:
    risks:
      - "Operators keep dual-writing AK scope and repo-local manifests."
      - "Brownfield repos delete compatibility fallback before snapshot validation is actually live."
      - "Template docs keep teaching snapshots or legacy manifests as hand-authored truth."
---

# Task-scope migration playbook

This playbook is the **template-side operator guide** for the M36 task-scope rollout.
It complements the governance-side contract published in governance-kernel for task-scope migration and deprecation.

Use this when you are:
- adopting updated template docs/helpers into an existing **L1** repo,
- migrating an existing **L2** repo away from hand-authored `governance/task-scopes/AK-*.json` files,
- or checking whether README / governance / handoff text still implies dual authority.

## One-line rule

> Author explicit task scope in AK, export frozen `AK-<TASK-ID>.snapshot.json` files for repo validation, keep legacy `AK-*.json` manifests only as temporary compatibility fallback, and remove them from the primary workflow as soon as the snapshot path is live.

## Decision table

| Situation | What to do |
|---|---|
| Task uses repo-default scope | Do nothing extra. Do **not** invent a snapshot or a legacy manifest. |
| Task needs explicit scope and the repo already has snapshot validation | Author/update scope in AK, export `AK-<TASK-ID>.snapshot.json`, validate, commit the refreshed snapshot if needed. |
| Task needs explicit scope and the repo still has legacy `AK-*.json` fallback | Author/update scope in AK, export the snapshot first, keep the legacy file only while compatibility still depends on it, then remove that legacy path from the happy path once validation passes. |
| Snapshot validation fails after migration | Restore the last known-good snapshot or temporary legacy fallback, repair docs/helpers/CI, and re-run validation before retrying cleanup. |

## L1 adoption flow

Use this when an existing company template repo is adopting the updated L0 surface.

1. Preview the L1 delta from `core/tpl-template-repo`.
2. Pull in the updated task-scope docs/helpers:
   - `README.md`
   - `governance/README.md`
   - `docs/dev/task-scope-migration-playbook.md`
   - relevant `copier/tpl-*/README.md.j2`, `governance/README.md`, and `next_session_prompt.md` surfaces
3. Verify the rendered L2 templates teach the same contract:
   - AK is the authoring surface
   - `AK-<TASK-ID>.snapshot.json` is a frozen export for repo consumers
   - legacy `AK-*.json` manifests are transitional compatibility only
   - repo-default scope does not require a snapshot
4. Run the L1 validation gate:
   ```bash
   bash ./scripts/check-template-ci.sh
   ```
5. Open the MR with explicit migration/deprecation notes so downstream adopters know this is a bounded transition, not a flag day.

## L2 brownfield migration flow

Use this when an existing repo already has local workflow text or files under `governance/task-scopes/`.

1. Render the current template baseline from the parent L1 repo.
2. Merge control-plane changes first (`README.md`, `AGENTS.md`, `governance/README.md`, `next_session_prompt.md`, `scripts/ci/*`, `scripts/ak.sh`).
3. Check whether the task actually needs explicit scope.
   - If not, stop here and keep repo-default scope.
4. If explicit scope is needed, author it in AK first:
   ```bash
   ./scripts/ak.sh task show <TASK-ID>
   ./scripts/ak.sh task scope show <TASK-ID>
   ./scripts/ak.sh task scope set <TASK-ID> ...
   # or
   ./scripts/ak.sh task scope update <TASK-ID> ...
   ```
5. Export the repo-consumption snapshot:
   ```bash
   mkdir -p governance/task-scopes
   ./scripts/ak.sh task scope export <TASK-ID> > governance/task-scopes/AK-<TASK-ID>.snapshot.json
   ```
6. Validate the repo on the snapshot path:
   ```bash
   ./scripts/check-task-scope-snapshots.sh
   ./scripts/ci/full.sh
   ```
7. If the repo still depends on a legacy `governance/task-scopes/AK-*.json` file:
   - keep it only as temporary compatibility fallback,
   - do not update it as if it were canonical,
   - remove workflow/handoff/docs text that still teaches it as the happy path,
   - and delete or retire it once the snapshot path is proven.

## Template wording checklist

When touching template docs, keep these statements aligned:

- say **AK authors explicit scope**
- say **snapshots are frozen exports for repo consumers / CI**
- say **legacy `AK-*.json` files are transitional compatibility scaffolding only**
- say **repo-default scope does not require a snapshot**
- do **not** say snapshots or legacy manifests are hand-authored authority
- do **not** imply a hidden runtime-kernel cutover or mandatory flag day

## Rollback

If the migration wording or helper changes are too aggressive for a brownfield repo:

1. restore the last known-good snapshot export from git, or regenerate the prior AK-backed snapshot if available
2. temporarily keep the last working legacy `AK-*.json` fallback only when the repo still depends on it
3. revert the docs/helper/CI assumptions that claimed the migration was already complete
4. re-run `./scripts/check-task-scope-snapshots.sh` and `./scripts/ci/full.sh` before retrying cleanup

Rollback is a repair step, not permission to restore permanent dual authority.

## Related

- governance-kernel task-scope migration/deprecation contract
- `../../README.md.jinja`
- `../../governance/README.md.jinja`
- `./tpl-project-repo-file-contract.md`
