# L1 adoption playbook (from L0)

Operator entrypoint: docs/dev/README.md (relative from here: `./dev/README.md`)
Related L2 migration playbook: docs/l2-transition-playbook.md (relative from here: `./l2-transition-playbook.md`)
Related task-scope migration playbook: copier-template/docs/dev/task-scope-migration-playbook.md

## Goal
Adopt L0 updates into existing L1 repos with minimal drift and explicit review.

## Preconditions
- L0 checks pass: `bash ./scripts/check-l0.sh`
- Target L1 repo has a clean working tree (or explicitly snapshot `HEAD` for comparison if local edits are present).
- Profile intent is chosen up front via `./profile-governance-policy.md` (internal vs public bundle).
- Changes flow via branch + MR (no direct push to `main`).

## Preview diff (non-destructive)
```bash
./scripts/preview-l1-diff.sh /absolute/path/to/holdingco
./scripts/preview-l1-diff.sh /absolute/path/to/softwareco
```

If the target repo is dirty, capture a stable comparison against committed state:
```bash
git -C /absolute/path/to/holdingco archive HEAD | tar -x -C /tmp/holdingco-head
```
Then compare render output against that extracted snapshot.

## Adoption flow
1. Create branch in target L1 repo.
2. Render fresh L1 output from L0 into a temp dir.
3. Apply selected changes into target repo.
4. Run in target repo:
   ```bash
   bash ./scripts/check-template-ci.sh
   ```
5. Open MR with recursion + contract notes.

## Special case: task-scope migration/deprecation rollout

When the adoption slice includes the FCOS-M36-06 task-scope migration contract:

1. Pull in the updated L1 docs surface from the L0 source:
   - `../copier-template/README.md.jinja`
   - `../copier-template/governance/README.md.jinja`
   - `../copier-template/docs/dev/task-scope-migration-playbook.md`
2. Confirm the generated L2 templates say the same bounded thing:
   - AK authors explicit task scope
   - `AK-<TASK-ID>.snapshot.json` is a frozen export for repo validation
   - legacy `AK-*.json` manifests are compatibility-only, not co-equal authority
   - repo-default scope does not require either file
3. Re-render and validate in the target L1 repo:
   ```bash
   bash ./scripts/check-template-ci.sh
   ```
4. Call out the migration/deprecation boundary explicitly in the MR so downstream brownfield adopters do not mistake the rollout for a flag day.

## Special case: migrating an old `<company>-templates` layout

If the company still lives under an old:

```text
<company>/<company>-templates
```

layout, use the staged L0 helper from `core/tpl-template-repo` instead of ad-hoc moves:

```bash
./scripts/migrate-l1-structure.sh <company_slug> "<Company Name>"
```

When the old company root contains custom grouping roots that are not already bootstrapped lane baselines, classify them explicitly:

```bash
AI_SOCIETY_CUSTOM_LANES=data,ml-platform \
  ./scripts/migrate-l1-structure.sh <company_slug> "<Company Name>"
```

Guardrails:
- Reserved L1 control-plane paths such as `docs`, `scripts`, `copier`, `governance`, `policy`, and `ontology` are never valid lane names.
- The migrator fails closed rather than inferring custom lanes from nested repos alone.
- Repair reserved-path collisions manually before rerunning the migrator.

## Drift controls
- Keep contracts/layer-contract.yml untouched unless intentionally changing policy (relative from here: `../contracts/layer-contract.yml`).
- Keep generated `.copier-answers.yml` committed.
- Never add nested Copier runs in template `_tasks`.
