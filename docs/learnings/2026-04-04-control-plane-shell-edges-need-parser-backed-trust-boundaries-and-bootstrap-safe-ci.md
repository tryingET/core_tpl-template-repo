# 2026-04-04 — Control-plane shell edges need parser-backed trust boundaries and bootstrap-safe CI

## Context
A deep adversarial review of `core/tpl-template-repo` found a cluster of control-plane bugs concentrated in copied shell surfaces rather than template content:

- task-scope verification parsed AK JSON with `awk`, so valid escaped quotes in repo paths broke repo-ownership checks
- snapshot discovery replayed filenames through newline-delimited shell strings, so one hostile filename could corrupt the whole validation pass
- the canonical AK wrapper implicitly trusted ambient `ak` binaries from `PATH`
- `tpl-project-repo` full CI ran two AK-backed validations concurrently
- L2 smoke lanes hard-failed in fresh repos that had no resolvable base branch yet

## Evidence
Implemented and verified in this repo:

- task-scope verification now delegates structured-data handling to `copier-template/scripts/lib/check-task-scope-snapshots.py`, a shared parser-backed helper propagated into L1 + non-package L2 repos
- the shell wrappers now fail clearly when `python3` / `python` or the shared helper is missing instead of misparsing JSON or filenames
- every copied `scripts/ak.sh` now blocks ambient `ak` binaries on `PATH` by default; explicit fallback requires `AK_ALLOW_PATH_FALLBACK=1`
- `tpl-project-repo/scripts/ci/full.sh` now runs AK-backed checks sequentially so validation no longer depends on runner timing
- shared L2 `scripts/ci/smoke.sh` now warns and skips the protected `docs/_core` diff when no base ref exists yet, instead of failing bootstrap repos outright
- deterministic checks now cover quoted repo paths, newline-bearing snapshot filenames, bootstrap repos with no base ref, explicit PATH-fallback opt-in, and serialized project full-lane AK execution
- `scripts/check-l0.sh` now defaults `L0_CHECK_TIMEOUT_SECONDS` to `300`, which matches current full-stack runtime instead of timing out at the previous default
- verification passed with:
  - `bash ./scripts/check-l0-generation.sh`
  - `bash ./scripts/check-l0-fixtures.sh`
  - `bash ./scripts/check-l0.sh`

## Pattern
Shell is good at orchestration and bad at trust-boundary semantics.

When a copied shell wrapper starts doing any of the following, it should be treated as a control-plane risk surface:

1. parsing structured JSON
2. deciding whether an external binary is trusted
3. comparing ownership-sensitive paths
4. enumerating attacker-controlled filenames
5. turning git-topology assumptions into hard CI preconditions

Those risks multiply in template repos because the same shell fragment is copied across L0, L1, fixtures, and downstream generated repos.

## Guardrail
Use these rules for future template/control-plane work:

- never parse JSON at a shell trust boundary with `awk`, `sed`, or line slicing; use a parser-backed helper
- never enumerate repo-owned artifact paths through newline-delimited shell strings; use a helper that owns path handling end-to-end
- default-deny ambient binary fallbacks for canonical wrappers; any `PATH` fallback must be explicit and operator-signaled
- if two CI branches touch the same mutable tool/runtime surface, serialize them unless concurrency is explicitly proven safe
- smoke lanes should validate repo content first and degrade gracefully when bootstrap git topology is missing
- whenever a deep review finds a shell-edge bug, add an executable adversarial regression immediately

## Propagation
- TIP candidate: yes — a reusable deep-review checklist for shell control planes should always probe structured-data parsing, ambient-binary trust, hostile filenames, and bootstrap git states.
