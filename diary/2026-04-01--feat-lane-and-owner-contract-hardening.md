# 2026-04-01 — Lane and owner contract hardening

## What I Did
- Replaced ad-hoc lane-name checks with shared `repo-surface` helpers for syntax, built-in lanes, reserved control-plane paths, and lane-name list membership.
- Hardened `bootstrap-lane-root.sh` so reserved L1 control-plane paths like `docs` and `scripts` fail closed instead of becoming pseudo-lanes.
- Hardened `migrate-l1-structure.sh` so custom grouping roots require explicit classification via `AI_SOCIETY_CUSTOM_LANES` unless they already carry a lane baseline, and so reserved collisions fail clearly.
- Changed `new-repo-from-copier.sh` to preserve structured owner handles such as `@org/team` verbatim while still normalizing human/git-derived fallback names.
- Added executable regressions for reserved lane rejection, structured owner-handle roundtrips, preview honesty for team-owned lanes, explicit custom-lane migration, and fail-closed migration collisions.
- Regenerated fixtures with `./scripts/sync-l0-fixtures.sh` and re-ran the full L0 check stack.

## What Surprised Me
- The owner-handle corruption lived almost entirely in the env transport path; fixing that one boundary corrected bootstrap refresh and preview replay behavior together.
- The old “nested repos imply lane” heuristic was convenient but impossible to make safe around reserved top-level namespaces without either explicit classification or fail-closed behavior.

## Patterns
- Filesystem shape is not a sufficient substitute for control-plane intent.
- Structured identifiers should pass through verbatim once they are already in their typed form.
- Reserved namespace collisions should fail early instead of being silently coerced into a new meaning.
- Regression suites need both green-path portability checks and semantic namespace checks.

## Crystallization Candidates
- → docs/learnings/: lane names and owner handles should be treated as typed control-plane values, not lossy shell strings.
- → tips/meta/: add an adversarial checklist item for reserved top-level namespaces and structured team handles such as `@org/team`.
