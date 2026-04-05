# ROCS PATH Fallback Consent Gate

**Date:** 2026-04-04
**Type:** feat
**Scope:** scripts/rocs.sh + copier-template + fixtures

## What
Added `ROCS_ALLOW_PATH_FALLBACK` consent gate to `scripts/rocs.sh`, mirroring the `AK_ALLOW_PATH_FALLBACK` pattern already in `scripts/ak.sh`. Propagated to all template layers (L1, L2) and fixture snapshots.

## Why
Deep adversarial review identified that `rocs.sh` fell back to executing `rocs` from PATH without any consent gate, while `ak.sh` required explicit `AK_ALLOW_PATH_FALLBACK=1`. A poisoned PATH could silently execute a malicious `rocs` binary with full user privileges, potentially corrupting ontology state across all repos.

This was the #1 ranked bug from the adversarial review — **40 days underground** since `a500be2a` (2026-02-24).

## Changes
- `scripts/rocs.sh`: Added `path_fallback_enabled()`, split `path-rocs` into `path-rocs`/`path-rocs-blocked`, updated `runner_desc`, `doctor`, `--which`, and exec case
- `copier-template/scripts/rocs.sh`: Identical L1 template
- `copier-template/copier/tpl-{project,agent,org,monorepo}/scripts/rocs.sh.j2`: L2 templates
- All fixture snapshots regenerated via `sync-l0-fixtures.sh`

## Verification
- `check-l0.sh`: 7/7 passed, 0 failures, 0 warnings
- Manual: PATH rocs blocked without consent (exit 1), allowed with `ROCS_ALLOW_PATH_FALLBACK=1` (exit 0)
- `--doctor` shows `path fallback enabled: yes/no` diagnostic

## Trust boundary contract
Both wrappers now follow the same contract:
- `*_BIN`: explicit override (absolute path or resolvable command)
- `*_ALLOW_PATH_FALLBACK=1`: explicit consent for ambient PATH resolution
- Otherwise: die with actionable error message
