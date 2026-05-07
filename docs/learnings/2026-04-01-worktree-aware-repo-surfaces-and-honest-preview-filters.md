---
summary: "2026-04-01 — Worktree-aware repo surfaces and honest preview filters."
read_when:
  - "Read when you need 2026-04-01 — worktree-aware repo surfaces and honest preview filters."
type: "reference"
---

# 2026-04-01 — Worktree-aware repo surfaces and honest preview filters

## Context
A deep adversarial review of `core/tpl-template-repo` found a cluster of operator-surface failures sharing one root cause: repo identity and operator-managed surfaces were encoded as ad-hoc shell heuristics.

Concrete symptoms included:
- `preview-l1-diff.sh` hiding tracked lane-root drift by deleting whole lane-root directories from the comparison tree
- `migrate-l1-structure.sh` rejecting worktree-backed source repos because it only trusted `.git/` directories
- `preflight-repo-census.sh` missing git worktrees and, in rendered descendants, still missing repos deeper than five levels
- `bootstrap-lane-root.sh` serializing checkout-local absolute `_src_path` values into tracked lane answers

## Pattern
When control-plane helpers infer repo identity from filesystem shape instead of git semantics, fixes fragment:

1. one script learns about worktrees
2. another still assumes `.git` is a directory
3. previews stay green by hiding whole surfaces instead of comparing canonical baselines
4. descendant templates lag behind root fixes

The durable move is to centralize repo/worktree reasoning and make preview filters preserve tracked signal.

## Guardrail
Implemented in this repo:
- shared helper:
  - `scripts/lib/repo-surface.sh`
  - `copier-template/scripts/lib/repo-surface.sh`
  - `copier-template/copier/tpl-{agent,org,project,monorepo}/scripts/lib/repo-surface.sh.j2`
- the helper now provides:
  - git/worktree-aware repo detection via `git rev-parse`
  - repo-root enumeration from `.git` files *and* directories
  - nested child-repo discovery for preview pruning
  - stable lane-root `_src_path` contract (`../copier/tpl-project-repo`)
- `scripts/preview-l1-diff.sh` now:
  - materializes canonical lane-root baselines instead of deleting them wholesale
  - ignores nested child repos only
  - preserves target `project_owner_handle` during synthetic lane materialization to avoid false drift
- `scripts/migrate-l1-structure.sh` now clones history into the staged repo instead of copying `.git` blindly, so worktree-backed source repos migrate correctly
- root and rendered `preflight-repo-census` helpers now count deep repos and git worktrees
- `scripts/check-l0-adversarial.sh` now proves:
  - tracked lane-root drift is visible in preview output
  - worktree-backed migrations succeed even when `sed -i` is unavailable
  - both root and rendered descendant repo-census helpers see deep repos and worktrees
  - lane bootstrap stays stable across symlinked checkout paths

## Heuristics
- Treat `.git` files and `.git` directories as equally valid repo markers.
- If a preview filter removes an entire tracked surface, add a regression where a tracked file inside that surface changes.
- If a helper copies git metadata, test it on worktrees; worktree `.git` files are bindings, not portable repos.
- Serialize provenance fields in the most stable truthful form available; absolute checkout paths are usually control-plane noise.
- Root operator fixes are not complete until rendered descendants prove the same behavior.

## Propagation
- Candidate for future TIP crystallization anywhere repo discovery or preview filtering appears in other template/control-plane repos.
