---
summary: "Session note: 2026 04 05 Feat Negative Path Nexus Hardening."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 04 05 feat negative path nexus hardening."
type: "reference"
---

# 2026-04-05 — Negative-path nexus hardening

## What I Did
- Fixed `scripts/check-doc-references.sh` so invalid override paths fail closed instead of silently falling back.
- Hardened `scripts/rocs.sh` so an empty/invalid vendored `tools/rocs-cli/` no longer hijacks runner selection.
- Hardened `scripts/lib/repo-surface.sh` to follow symlinked repo surfaces during census discovery.
- Added early `rsync` dependency preflight to `scripts/migrate-l1-structure.sh`.
- Propagated shared helper/wrapper changes into `copier-template/` and nested L2 template copies.
- Regenerated fixtures with `bash ./scripts/sync-l0-fixtures.sh`.
- Verified the full suite with `bash ./scripts/check-l0.sh`.

## What Surprised Me
- The ROCS hardening landed cleanly by strengthening the existing local-project fallback tests: adding empty vendored dirs turned a happy-path test into a real adversarial regression test.
- Repo census symlink handling propagated broadly because the helper is mirrored across root, L1, and L2 surfaces.

## Patterns
- Negative-path tests are cheapest when they piggyback on existing happy-path setup.
- Shared shell helpers should be treated like APIs: fix once, propagate everywhere, then regenerate fixtures.

## Crystallization Candidates
- → docs/learnings/: fail-closed override and launcher-selection patterns for shell wrappers
- → tips/meta/: add a standing regression checklist for invalid override paths, invalid vendored tool dirs, missing copy utilities, and symlinked discovery surfaces
