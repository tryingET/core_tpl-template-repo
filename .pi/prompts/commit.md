---
description: Project-local commit workflow for RCOS sessions (checkpoint sync + logical commits)
---

## 0) Handoff sync first
Before any commit commands:

1. Update `next_session_prompt.md` session checkpoint.
2. If present in this repo, update `docs/dev/fcos-convergence-issue-set.md` for issues touched this session.
3. If decisions changed, keep `docs/dev/fcos-convergence-rollup-plan.md` consistent.

Keep updates concise and factual.

## 1) Context
1. `git status --short`
2. if clean, stop and report no-op
3. `git diff --name-status HEAD`
4. `git log --oneline -5`
5. inspect only scoped diffs:
   - `git diff -- <files...>`

## 2) Commit workflow
- Create one or more logical commits.
- Use conventional commits (`type(scope): description`).
- Commit body must include:
  - **Why**
  - **Validation**
- If `$ARGUMENTS` includes an RCOS issue id (e.g. `RCOS-M1-02`), include it in commit body.

## 3) Validation policy
- Prefer scoped checks per logical commit.
- Run full repo validation once after final commit (or before push).

$ARGUMENTS
