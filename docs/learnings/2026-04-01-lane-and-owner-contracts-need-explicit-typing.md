---
summary: "2026-04-01 — Lane and owner contracts need explicit typing."
read_when:
  - "Read when you need 2026-04-01 — lane and owner contracts need explicit typing."
type: "reference"
---

# 2026-04-01 — Lane and owner contracts need explicit typing

## Context
A deep adversarial review of `core/tpl-template-repo` found two control-plane contracts being handled as loose shell strings:

- lane identity was inferred from top-level directory shape and nested repos
- owner identity was re-inferred from env fallbacks even when a valid structured handle already existed

Concrete symptoms included:
- `bootstrap-lane-root.sh` accepting reserved L1 control-plane paths like `docs` as custom lanes
- `migrate-l1-structure.sh` auto-classifying any top-level dir with nested repos as a lane candidate
- `new-repo-from-copier.sh` collapsing structured team handles like `@org/team` into `@orgteam`
- `preview-l1-diff.sh` replaying that same lossy owner path while materializing canonical lane baselines

## Pattern
If a control-plane value already has a governed shape, re-normalizing it as if it were free text creates corruption:

1. a valid typed value is serialized
2. a later helper transports it through an env/string boundary
3. another helper “infers” it again and strips semantic characters
4. previews, migrations, and refreshes drift even when the operator did the right thing

The same applies to lane names: a top-level directory with nested repos is not automatically a lane. Without an explicit contract, reserved namespaces and grouping roots become indistinguishable.

## Guardrail
Implemented in this repo:
- shared lane contract helpers now live in:
  - `scripts/lib/repo-surface.sh`
  - `copier-template/scripts/lib/repo-surface.sh`
- the shared helper now provides:
  - lane-name syntax validation
  - built-in lane detection (`owned`, `contrib`, `infra`, `agents`)
  - reserved L1 control-plane path detection (`docs`, `scripts`, `copier`, `governance`, `policy`, `ontology`, etc.)
  - lane-name list membership for explicit migration classification
- `copier-template/scripts/bootstrap-lane-root.sh` now rejects reserved control-plane paths as lane names
- `scripts/migrate-l1-structure.sh` now:
  - requires `AI_SOCIETY_CUSTOM_LANES=<lane1,lane2>` for custom grouping roots that only advertise themselves through nested repos
  - still auto-discovers already-bootstrapped lane roots
  - fails closed when reserved L1 control-plane dirs contain lane-like state
- `copier-template/scripts/new-repo-from-copier.sh` now preserves structured handles such as `@org/team` verbatim when they arrive via `PROJECT_OWNER_HANDLE` / `PI_PROJECT_OWNER_HANDLE`
- `scripts/check-l0-generation.sh` now proves:
  - reserved lane names are rejected
  - structured team handles survive lane bootstrap reruns unchanged
- `scripts/check-l0-adversarial.sh` now proves:
  - preview stays clean for team-owned canonical lane baselines
  - migration succeeds for explicitly classified custom lanes
  - migration fails clearly for missing custom-lane classification
  - migration fails clearly for reserved lane collisions

## Heuristics
- If a value already looks like a typed handle (`@org/team`), preserve it; do not run it back through human-name sanitization.
- If a top-level directory needs special ignore/bootstrap behavior, require either a baseline marker or an explicit operator classification.
- Reserved control-plane namespaces should fail closed, not be repurposed by heuristic discovery.
- Any preview or migration helper that reconstructs state must replay exact typed values, not inferred approximations.

## Propagation
- Candidate for future TIP crystallization anywhere grouping roots, CODEOWNERS handles, or env-based replay surfaces appear in other template/control-plane repos.
