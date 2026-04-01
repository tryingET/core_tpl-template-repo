# 2026-04-01 — Repo-surface nexus hardening

## What I Did
- Reproduced the deep-review findings around false-clean lane-root previews, worktree-blind migration/census logic, and checkout-path-sensitive lane `_src_path` churn.
- Added a shared `repo-surface` helper for git repo/worktree discovery and lane-root source-path normalization.
- Reworked `scripts/preview-l1-diff.sh` to materialize canonical lane-root baselines and ignore only nested child repos.
- Reworked `scripts/migrate-l1-structure.sh` to accept worktree-backed source repos and transplant history through a clone-based `.git` handoff.
- Updated L2 `preflight-repo-census` templates to use worktree-aware repo discovery.
- Regenerated fixtures with `./scripts/sync-l0-fixtures.sh` and re-ran the full L0 check stack.

## What Surprised Me
- The original “ignore lane roots” logic was clean on paper but hid tracked drift immediately once a lane baseline changed.
- Supporting worktrees required more than loosening repo detection; copying a worktree `.git` file directly would have preserved the wrong worktree binding.
- Preview lane-baseline materialization surfaced a second-order diff source: project-owner inference noise between synthetic baselines and committed lane roots.

## Patterns
- Repo identity must come from `git rev-parse`, not `.git` directory heuristics.
- Preview filters should suppress operator-managed noise, not tracked baseline signal.
- Volatile provenance fields (`_src_path`) need a stable serialized contract or symlinked/moved checkouts turn into fake drift.
- Root fixes are incomplete until rendered descendants and fixtures prove the same behavior.

## Crystallization Candidates
- → docs/learnings/: repo/worktree discovery and preview-filtering rules should become a named control-plane heuristic.
- → tips/meta/: add an adversarial checklist item for git worktrees, symlinked checkouts, and tracked-drift-vs-noise preview assertions.
- → scripts/: keep repo-surface logic centralized instead of reintroducing `.git` path heuristics in new helpers.
