# Shared Helper Copies Need Parity Checks

**Date:** 2026-04-05
**Trigger:** Nexus follow-through found `copier-answers.sh` had diverged between L0 and generated L1/L2 template copies, so fallback parsing behavior differed by layer and by environment.

## Pattern
When a repo deliberately copies a shell helper across L0, L1, and embedded L2 template surfaces, the copies are part of one contract even if they live in different directories.

If one copy is hardened and the others are not, the system becomes split-brain:
- developer machines may pass because richer dependencies bypass the fallback path
- minimal CI or downstream generated repos may still execute the stale fallback logic
- reviews miss the issue because the file names look “shared” while the contents are not

## Heuristic
For every helper that is intentionally duplicated across template layers:
1. choose one canonical source
2. add deterministic parity checks (`git diff --no-index --quiet`) between all copies
3. add at least one runtime test that exercises the fallback path without optional dependencies

## Example from this repo
`copier-answers.sh` must stay behaviorally identical across:
- `scripts/lib/copier-answers.sh`
- `copier-template/scripts/lib/copier-answers.sh`
- `copier-template/copier/*/scripts/lib/copier-answers.sh`

Without parity checks, YAML fallback hardening can land in L0 while generated L1/L2 repos continue to accept unsupported tagged values.
