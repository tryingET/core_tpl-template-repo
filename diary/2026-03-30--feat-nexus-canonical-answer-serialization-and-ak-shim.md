---
summary: "Session note: 2026 03 30 Feat Nexus Canonical Answer Serialization And Ak Shim."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 30 feat nexus canonical answer serialization and ak shim."
type: "reference"
---

# 2026-03-30 — Nexus remediation for canonical answer serialization and deterministic AK coverage

## What I Did
- Replaced fragile hand-written answer-file quoting in the L1, tpl-monorepo, and tpl-package templates with canonical `to_nice_yaml` emission over stable intended fields.
- Hardened `copier-template/scripts/new-repo-from-copier.sh` so inherited string values preserve apostrophes and embedded quotes instead of stripping them.
- Made `scripts/rocs.sh` and propagated template copies fail closed when `ROCS_BIN` points to a missing binary.
- Updated `copier-template/scripts/release/check.sh` to validate the current manifest version instead of the bootstrap `0.1.0` literal.
- Added `copier-template/scripts/lib/check-template-ak.py`, a bounded deterministic AK test double, and rewired `check-template-ci.sh` to use it unconditionally.
- Encoded regressions in `scripts/check-l0-generation.sh` for apostrophes, embedded quotes, fail-closed ROCS diagnostics, no-ambient-`ak` template CI, and release-version bump tolerance.
- Synced fixtures and re-ran the full L0 validation lane.

## What Surprised Me
- Canonical YAML emission over the full `_copier_answers` map broke L1 idempotency because Copier injected volatile `_commit` metadata; the fix was to emit canonical YAML over an explicit stable-field map.
- The local AK test double was enough to make template CI deterministic without needing to solve external AK installation in GitHub Actions.

## Patterns
- Canonical serialization must still be selective; stable format with unstable fields is still non-deterministic.
- A small local shim is better than a silent optional branch when CI only needs a narrow tool slice.

## Crystallization Candidates
- → docs/learnings/2026-03-30-canonical-answer-serialization-and-local-tool-shims.md
- → tips/meta/tip-0011-canonical-answer-serialization-and-local-tool-shims.md
