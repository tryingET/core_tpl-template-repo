---
summary: "Session note: 2026 03 30 Feat L0 Adversarial Operator Surface Suite."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 30 feat l0 adversarial operator surface suite."
type: "reference"
---

# 2026-03-30 — L0 adversarial operator-surface suite

## What I Did
- Implemented `scripts/check-l0-adversarial.sh` and wired it into `scripts/check-l0.sh`.
- Fixed `scripts/new-l1-from-copier.sh` so `l0_source_sha` resolves in git worktrees.
- Fixed `scripts/preview-l1-diff.sh` to ignore bootstrapped lane roots and nested child repos when previewing L1 adoption diffs.
- Fixed `scripts/migrate-l1-structure.sh` to use portable temp-file rewrites instead of `sed -i`.
- Fixed `scripts/preflight-repo-census.sh` to detect repos deeper than five directory levels.
- Removed the `location` choice restriction from `copier-template/copier/tpl-project-repo/copier.yml` and updated `copier-template/scripts/bootstrap-lane-root.sh` to pass `location` at render time.
- Strengthened `scripts/check-l0-generation.sh` so custom lane bootstrap now asserts README + CODEOWNERS semantics, not just `.gitignore` idempotence.
- Synced fixtures with `bash ./scripts/sync-l0-fixtures.sh`.
- Verified the full gate with `bash ./scripts/check-l0.sh`.

## What Surprised Me
- The worktree provenance bug was still reproducible after the source fix because a detached worktree starts from committed `HEAD`, not current dirty working-tree state; the adversarial suite had to overlay the current wrapper into the temp worktree.
- `preview-l1-diff.sh` needed contract-aware filtering rather than a bigger raw diff allowlist; lane roots are operator-managed state, not part of the pure L1 render surface.

## Patterns
- Operator-facing helper scripts fail in post-render states more often than in fresh-render states.
- Render-then-patch flows are fragile when the value can be passed explicitly at render time.
- Portable temp-file rewrites are the right default for shell-based metadata mutation.
- Hidden depth caps in discovery helpers create silent false negatives.

## Crystallization Candidates
- → docs/learnings/: adversarial coverage for operator-surface helpers should be a first-class template contract.
- → tips/meta/: test helper scripts in worktree/adoption/migration states, not just pristine renders.
