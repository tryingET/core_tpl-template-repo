# 2026-03-30 — Shared answer parsers and portable mutation primitives for template control planes

## Context
A deep adversarial review of `core/tpl-template-repo` found several green-path shell helpers failing under ordinary edge conditions:

- quoted scalar values containing `#` were reparsed as comments during preview rehydration
- multiline and escaped answer scalars were silently truncated or literalized by line-oriented shell parsing
- suffix-policy exclusions were encoded as a quoted shell string, so excluded child-repo paths were still scanned
- ROCS local-python fallback selected `python -m rocs_cli` without making `src/` importable
- lane bootstrap relied on GNU `sed -i`, then later accepted regex/shell-hostile lane names that broke idempotence and operator guidance

These failures lived in the repo’s control plane, so they propagated into generated L1/L2 surfaces.

## Pattern
When template control planes hand-roll parsing and in-place mutation logic in multiple scripts, happy-path validation is not enough. The durable move is:

1. centralize repeated parsing into a small shared helper
2. use portable temp-file rewrites instead of platform-specific in-place editors
3. turn each adversarial edge case into an executable regression

## Guardrail
Implemented in this repo:
- shared answers helper:
  - `scripts/lib/copier-answers.sh`
  - `copier-template/scripts/lib/copier-answers.sh`
  - `copier-template/copier/tpl-{agent,org,project,monorepo}/scripts/lib/copier-answers.sh`
- the helper now prefers `python3` then `python` with PyYAML for exact scalar parsing and fails closed in the shell fallback instead of corrupting multiline/escaped values
- helper consumers now include preview rehydration, L1 wrappers/CI, and L2 AK wrappers
- callers now preserve parser exit status and surface clear errors instead of degenerating into silent omission/defaulting
- AK wrappers and template CI now surface parse failures explicitly instead of silently dropping derived defaults or aborting without context
- preview rehydration now derives its replay keys from the shared helper contract, including `l2_org_docs_default`
- `copier-template/scripts/check-task-scope-snapshots.sh` now canonicalizes repo paths before repo-ownership checks so symlinked checkouts do not false-fail as foreign snapshots
- `copier-template/scripts/check-template-ci.sh` now restores pre-existing `governance/task-scopes/` content after its local probe instead of deleting the live directory
- `copier-template/scripts/lib/suffix-policy.sh` now applies structural excludes instead of word-split command fragments
- ROCS wrappers now export `PYTHONPATH=<repo>/src` for the local-python fallback and accept `python3`-only environments instead of requiring a `python` alias
- `copier-template/scripts/bootstrap-lane-root.sh` now uses portable temp-file rewrites instead of `sed -i`, rejects regex/shell-hostile lane names, and uses fixed-string idempotence checks
- `scripts/check-l0-generation.sh` now proves:
  - quoted `#` values survive L1 -> L2 inheritance
  - multiline values survive L1 -> L2 inheritance when PyYAML is available
  - escaped tab values survive L1 -> L2 inheritance
  - preview stays no-diff for quoted `#` values even when PyYAML is unavailable
  - preview and L1 -> L2 inheritance fail closed with a clear parse error for unsupported multiline fallback cases
  - preview replays `l2_org_docs_default`
  - generated L1 `check-template-ci.sh` preserves pre-existing task-scope files
  - child-repo template files under `owned/` do not false-trip suffix policy
  - lane bootstrap succeeds even when `sed -i` is unavailable
  - lane bootstrap rejects unsafe lane names and stays idempotent for safe ones
  - both generated L1 and root ROCS local-python fallbacks execute successfully

## Heuristics
- If a shell script consumes `.copier-answers.yml`, give it shared parsing or a stronger parser, not one more ad-hoc regex.
- If exact parsing is unavailable, fail closed on unsupported scalar shapes; never silently coerce multiline or escaped values.
- Once you introduce fail-closed parsing, audit every caller for `|| true`-style swallowing or the fix collapses back into silent omission.
- If a replay/preview tool claims to reconstruct config, derive its key list from a shared contract, not a hand-maintained subset.
- If a script mutates checked-in/generated files, prefer temp-file rewrite + `mv` over GNU-only in-place editing.
- Validate operator-provided path fragments before feeding them to regexes, ignore rules, or printed shell commands.
- If a wrapper advertises a fallback path, execute that fallback in CI; do not stop at `--which`.
- For exclusion rules, always include a positive regression with a matching file under an excluded path.

## Propagation
- Candidate for future TIP crystallization if the same convergence pattern appears in more template repos.
