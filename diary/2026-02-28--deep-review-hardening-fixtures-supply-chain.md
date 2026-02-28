# 2026-02-28 — Deep Review + Hardening: Fixtures & Supply Chain

## What I Did

- Applied full adversarial deep review (TWO PASSES) using cognitive stack
- **Pass 1 fixes**:
  - Fixed Copier pin bypass race in both L0 and L1 wrappers
  - Added `set -eu` header to fixture normalization library
  - Added L2 fixture coverage for `tpl-monorepo` and `tpl-package`
- **Pass 2 fixes**:
  - Added `tpl-package` to L1 CI validation loop (5 places in check-template-ci.sh)
  - Added `template_source_sha` normalization to fixture-normalization.sh
- Re-synced all fixtures after changes

## What Surprised Me

- **Static Confidence Anti-Pattern**: The system had strong guardrails but they checked text, not runtime behavior. Copier wrappers could fall back silently to unpinned versions.
- **Incomplete Fixture Coverage**: Only 1 of 5 L2 templates had fixture validation. `tpl-monorepo` and `tpl-package` could break without detection.
- **Template List Drift**: The template list was hardcoded in 5 different places in check-template-ci.sh, and `tpl-package` was missing from all of them.
- **Provenance Chain Gap**: `template_source_sha` was not normalized, causing fixture drift.

## Patterns

- **Supply chain checks need runtime validation**: Static assertions about command strings don't guarantee runtime behavior.
- **Fixture normalization can hide bugs**: Aggressive normalization of volatile fields can mask structural issues.
- **Template lists must be DRY**: Hardcoded lists in multiple places will drift.

## Crystallization Candidates

- → `docs/learnings/` — "Static Confidence" anti-pattern (DONE)
- → `tips/meta/` — TIP-0008 for fixture coverage expansion (DONE)
- → `tips/meta/` — TIP-0009 for template list DRY principle (PENDING)

## Changes Made

| File | Kind | Description |
|------|------|-------------|
| `scripts/lib/fixture-normalization.sh` | fix | Added `set -eu` header + `template_source_sha` normalization |
| `scripts/new-l1-from-copier.sh` | fix | Exit on pinned runtime failure instead of silent fallback |
| `copier-template/scripts/new-repo-from-copier.sh` | fix | Same fix for L1 wrapper |
| `copier-template/scripts/check-template-ci.sh` | enhance | Added tpl-package to all 5 validation loops |
| `scripts/check-l0-fixtures.sh` | enhance | Added monorepo/package fixture generation and comparison |
| `scripts/sync-l0-fixtures.sh` | enhance | Added monorepo/package fixture sync |
| `fixtures/l2/tpl-monorepo/` | new | Monorepo L2 fixture |
| `fixtures/l2/tpl-package/` | new | Package L2 fixture |

## Deferred With Contract

| Finding | Rationale | Deadline | Blast Radius |
|---------|-----------|----------|--------------|
| Add shellcheck to CI | Non-blocking enhancement | 2026-03-14 | Shell bugs may escape detection |
| Runtime validation script | Architectural change | 2026-03-21 | Supply chain confidence remains static-only |
| Work-items schema consolidation | Requires coordination | 2026-03-21 | Tooling complexity |
| Extract template list to variable | DRY improvement | 2026-03-21 | Manual synchronization required |
