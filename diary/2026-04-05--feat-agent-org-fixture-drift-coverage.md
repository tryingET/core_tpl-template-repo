# 2026-04-05 — Expand tpl-agent-repo and tpl-org-repo fixture drift coverage

## What I Did
- Added `tpl-agent-repo` and `tpl-org-repo` to the deterministic L2 fixture sync/check flow in `scripts/sync-l0-fixtures.sh` and `scripts/check-l0-fixtures.sh`.
- Generated and normalized new checked-in fixtures at `fixtures/l2/tpl-agent-repo/` and `fixtures/l2/tpl-org-repo/` from the current L0 -> L1 -> L2 render path.
- Re-ran focused validation with `bash ./scripts/check-l0-fixtures.sh` and `bash ./scripts/check-l0-generation.sh`.

## What Surprised Me
- The generation smoke already covered `tpl-agent-repo` and `tpl-org-repo`, but the checked-in fixture drift gate still only enforced `tpl-project-repo`, `tpl-monorepo`, and `tpl-package`.
- Adding the missing L2 fixtures was enough to close the coverage gap without introducing another matrix axis.

## Patterns
- When a template archetype is already in generation smoke, it should usually also have a checked-in fixture snapshot so drift is caught by both render smoke and no-index fixture comparison.
- L0 fixture sync/check scripts need to evolve together; otherwise one side silently knows about more archetypes than the other.

## Crystallization Candidates
- → docs/learnings/ if fixture coverage gaps recur across other template archetypes.
- → tips/meta/ if the "generation smoke implies fixture mirror" rule becomes a stable template-maintenance pattern.
