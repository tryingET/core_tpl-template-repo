# L2 transition playbook (existing repo -> templated baseline)

## Goal
Migrate an existing L2 repository to the current template baseline without losing business code or breaking governance/CI contracts.

## Non-negotiables
- Branch + MR only (no direct `main` pushes).
- Keep migration reversible until final merge.
- Adopt scaffolding contracts first, then reconcile business code.
- Do not leave deferred work in ad-hoc TODOs; track in authoritative models.

## Preconditions
- You have the correct L1 company repo for your company (e.g. `~/ai-society/softwareco`).
- Working tree is clean in target existing repo (or explicitly snapshot current HEAD).
- You know the intended archetype (`tpl-project-repo`, `tpl-agent-repo`, `tpl-org-repo`, `tpl-monorepo`, `tpl-package`).

## Special case: grouping/lane-root repositories (nested child repos)

If the target repo is a **grouping root** (for example, an infra lane root) and contains child repositories with their own `.git`, migrate with extra safeguards:

1. Backup child repos first into `.migration-backup/<timestamp>/projects/<child>/` and write a manifest with child path + `HEAD` SHA.
2. Preserve child `.git` directories/history; never delete nested `.git` during parent migration.
3. Re-template parent and each child repo independently, then reconcile code/docs per repo.
4. Keep grouping-root `.gitignore` as a lane/root policy artifact (ignore child repos by default); do not assume `tpl-project-repo` root ignore rules are sufficient for grouping roots.
5. Do not use `tpl-package` for grouping folders (`tpl-package` is only for monorepo-internal packages without their own `.git`).

## Migration strategy: scaffold-first

### 1) Render clean baseline from L1

From `<company>` (company root L1 repo):

```bash
./scripts/new-repo-from-copier.sh <template-name> /tmp/<repo>-template \
  -d repo_slug=<repo> \
  --defaults --overwrite
```

Example for project repos:

```bash
./scripts/new-repo-from-copier.sh tpl-project-repo /tmp/<repo>-template \
  -d repo_slug=<repo> \
  --defaults --overwrite
```

### 2) Compare baseline vs existing repo

```bash
git diff --no-index -- /tmp/<repo>-template /absolute/path/to/<existing-repo>
```

### 3) Adopt control-plane contracts first

Adopt/update these first:
- `AGENTS.md`
- `CODEOWNERS`
- `scripts/ci/*`
- `scripts/rocs.sh`
- governance models (`governance/*` where archetype applies)
- baseline docs topology (`docs/*`)
- ontology topology (`ontology/*`)

Then reconcile product code (`src/`, `tests/`, package/app dirs).

### 3a) Merge policy for high-context control-plane files

When adopting template scaffolding, merge these files intentionally (do not blindly overwrite):

- `docs/_core/**`: treat as immutable by default during migration; only refresh in an explicit core-snapshot update.
- `README.md`: preserve repo-specific operational/runbook context; merge in template baseline sections where missing.
- `AGENTS.md`: preserve repo-specific operating instructions and add required guardrails (no secrets, MR-only, immutable core, deferred-work contract).
- `next_session_prompt.md`: preserve active handoff context unless intentionally resetting session state.

### 4) Validate migrated repo

Run baseline checks:
- repo smoke/full scripts (`scripts/ci/*`)
- project-specific test/lint/build commands
- governance/model validation where applicable

### 5) Open MR with explicit migration notes

MR should include:
- archetype used
- baseline render command
- diff summary (contracts/docs/code)
- risks + rollback path

## Rollback pattern

If migration diverges unexpectedly:

```bash
git restore -- .
git clean -fd
```

Or reset to migration branch start:

```bash
git reset --hard <migration-branch-start-sha>
```

## Common failure modes
- Copying only `src/` and forgetting governance/CI contracts.
- Mixing archetypes (e.g., applying monorepo skeleton to single-project repo).
- Running ad-hoc copier directly instead of wrapper scripts (losing inheritance/provenance behavior).
- Treating generated docs as canonical and hand-editing contracts inconsistently.
- Blindly overwriting `README.md` / `AGENTS.md` and losing repo-specific operational context.
- Modifying `docs/_core/**` during routine migration (breaks immutable-core guardrails).
- Re-templating grouping roots without backup manifests or nested `.git` preservation.

## Related
- Operator entrypoint: `docs/dev/README.md`
- L1 update playbook: `docs/l1-adoption-playbook.md`
- tpl-project detailed contract: `copier-template/docs/dev/tpl-project-repo-file-contract.md`
