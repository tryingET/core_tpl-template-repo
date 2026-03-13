---
description: Create commit groups with explicit-path staging and monorepo-aware validation
system4d:
  container: "Repo-local commit workflow prompt."
  compass: "Ship coherent monorepo commits with deterministic validation gates."
  engine: "Group changes -> stage explicit paths -> validate -> commit -> final push gate."
  fog: "Broad staging and weak scopes hide regressions in multi-package repos."
---

Create commits for the requested changes.

Mandatory workflow:

1. Build commit groups with clear intent.
   - Prefer separate commits for package-local vs root-level changes when they are independently understandable.
2. Stage **explicit file paths only** for each group.
   - Allowed: `git add path/to/file`
   - Disallowed: `git add .`, `git add -A`, wildcard staging
3. Use conventional commit titles in this exact form:
   - `type(scope): summary`
   - summary must be concise, present tense, and describe the staged change only
4. Choose `scope` using monorepo-aware rules:
   - package-local changes: use the package name or package folder scope, e.g. `my-package`
   - app-local changes: use the app name
   - root monorepo/tooling changes: use one of `root`, `monorepo`, `ci`, `docs`, `release`
   - cross-package coherent changes: prefer splitting by package; if one commit must span multiple packages, use `monorepo`
5. For each commit group, run:
   - `./scripts/ci/smoke.sh`
6. **Fail fast**:
   - If validation fails, stop immediately, report the error, fix, then rerun.
   - Do not create the commit until the gate passes.
7. Create the commit once the gate passes.
8. After the final commit is created, run once:
   - `./scripts/ci/full.sh`
9. If the final gate fails, stop and fix before any push.

Output:
- Commit groups and staged paths per group
- Proposed commit title for each group
- Commands run for each gate
- Final pass/fail status
