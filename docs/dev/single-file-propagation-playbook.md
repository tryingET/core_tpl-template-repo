---
summary: "Deterministic pattern for propagating one template file (e.g. scripts/ci/full.sh) across L0/L1/L2 without touching unrelated files."
read_when:
  - "When you need to roll out one template file only"
  - "When Copier update/recopy would otherwise change too many files"
---

# Single-File Propagation Playbook

## Goal
Roll out exactly one file change across many generated repos (example: `scripts/ci/full.sh`) while preserving all other repo content.

## Safety invariants
1. Work on a branch in each repo.
2. Stage only the target file.
3. Validate staged paths before commit.
4. Never keep unrelated `copier` output.

## Canonical flow per target repo

```bash
# 0) Start clean
git status --porcelain

# 1) Re-render from template (non-interactive)
copier recopy --trust --skip-answered --defaults --skip-tasks --overwrite

# 2) Keep only one file's diff
git restore --worktree --staged -- . ':(exclude)scripts/ci/full.sh'

# 3) Remove recopy-created untracked files
git clean -fd

# 4) Confirm only target file changed
git status --porcelain

# 5) Stage only target file
git add -- scripts/ci/full.sh
git diff --cached --name-only

# 6) Run fast gate
./scripts/ci/smoke.sh

# 7) Commit
git commit -m "chore(ci): sync full gate from template"
```

## If `copier recopy` cannot run
Some repos have stale `_src_path` values in `.copier-answers.yml` and cannot recopy.
For those repos:

- apply the file diff manually to `scripts/ci/full.sh`
- stage only that file
- run `./scripts/ci/smoke.sh`
- commit with same message pattern

## Verification sweep
After rollout, verify no remaining `scripts/ci/full.sh` drift in target repos.

## Notes
- This pattern does **not** delete repository content; it only discards unwanted recopy diffs.
- Use `copier update` when provenance metadata supports it; otherwise `recopy` is more predictable for one-file propagation.
