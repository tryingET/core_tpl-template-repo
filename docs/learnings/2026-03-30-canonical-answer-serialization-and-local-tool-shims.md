# 2026-03-30 — Canonical answer serialization and local tool shims for template CI

## Context
An adversarial review of `core/tpl-template-repo` found two related control-plane failures:

1. hand-written `.copier-answers.yml` templates corrupted valid string values with apostrophes/quotes
2. template CI silently skipped AK-backed regression coverage when `ak` was not installed on PATH

Because this repo is an L0 fan-out surface, both issues multiplied into generated L1/L2 repos.

## Evidence
- `copier-template/{{ _copier_conf.answers_file }}.jinja` rendered invalid YAML for names like `O'Connor Labs` when answers were single-quoted by hand.
- `copier-template/scripts/new-repo-from-copier.sh` stripped embedded quotes from inherited string values.
- `copier-template/scripts/check-template-ci.sh` previously enabled task-scope regression coverage only when ambient `ak` was available.
- New deterministic checks now prove:
  - apostrophes and embedded double quotes survive L0 -> L1 -> L2 inheritance
  - release baseline checks survive a normal version bump (`0.1.0` -> `0.1.1`)
  - `check-template-ci.sh` succeeds even when a failing dummy `ak` shadows PATH
  - `ROCS_BIN=/definitely/missing` causes `--doctor` and `--which` to fail closed

## Pattern
Template control planes should not hand-roll serialization or depend on ambient external tools when deterministic local substitutes are possible.

Two durable rules emerged:
- use canonical YAML emission (`to_nice_yaml`) for answer files instead of manually quoting scalars
- when CI needs a small slice of an external CLI to validate template behavior, prefer a bounded repo-local test double over PATH-dependent optional coverage

## Guardrail
Implemented guardrails:
- L1, tpl-monorepo, and tpl-package answer templates now use canonical YAML emission while keeping only stable intended fields.
- `copier-template/scripts/new-repo-from-copier.sh` now preserves quoted scalar content instead of deleting quote characters.
- `scripts/rocs.sh` and propagated template copies now fail closed for invalid `ROCS_BIN` overrides.
- `copier-template/scripts/release/check.sh` now validates the current manifest version instead of hardcoding the bootstrap version.
- `copier-template/scripts/check-template-ci.sh` now uses `scripts/lib/check-template-ak.py`, a deterministic local AK test double.
- `scripts/check-l0-generation.sh` now encodes regressions for apostrophes, embedded quotes, release-version bumps, fail-closed ROCS diagnostics, and no-ambient-`ak` template CI.

## Propagation
- TIP candidate: `tips/meta/tip-0011-canonical-answer-serialization-and-local-tool-shims.md`
