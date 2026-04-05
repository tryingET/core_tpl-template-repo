# 2026-04-04 — Control-plane parser, path-trust, and bootstrap hardening

## What I Did
- Replaced the task-scope snapshot checker’s ad-hoc shell parsing with a shared parser-backed helper (`copier-template/scripts/lib/check-task-scope-snapshots.py`) and propagated it through L1 + all non-package L2 templates.
- Hardened every copied `scripts/ak.sh` so ambient `ak` binaries on `PATH` are blocked by default; explicit fallback now requires `AK_ALLOW_PATH_FALLBACK=1`.
- Made L2 smoke lanes bootstrap-safe by degrading gracefully when no `origin/<base>` or local `<base>` ref exists yet.
- Serialized the `tpl-project-repo` full lane’s AK-backed checks to remove the validation race between work-items and task-scope verification.
- Added deterministic regression coverage for:
  - blocked-by-default PATH fallback + explicit opt-in,
  - quoted repo paths in task-scope ownership checks,
  - newline-bearing snapshot filenames failing clearly,
  - bootstrap repos with no base ref,
  - serialized project full-lane AK execution.
- Raised the default `scripts/check-l0.sh` per-check timeout from `180` to `300` seconds so the current full stack completes without requiring an override.
- Synced fixtures and re-ran the full L0 validation stack.

## What Surprised Me
- The deepest failures were not domain-template bugs; they were all at the shell control-plane edge where trust, parsing, and CI orchestration meet.
- The bootstrap-smoke bug had likely been hiding because most validation paths initialize repos on `main`, so the missing-base-ref state rarely got exercised.
- The strongest fix for the task-scope checker was not “better shell”; it was moving structured-data handling out of shell entirely.

## Patterns
- If a shell wrapper touches structured JSON, path ownership, or trust selection, it should offload that work to a real parser.
- Canonical wrappers should never silently trust ambient binaries; environment-based fallbacks need explicit operator intent.
- CI strictness should stay content-focused; git-topology assumptions need a bootstrap-safe escape path.
- Recurrent control-plane failures deserve executable regressions immediately, not just docs.

## Crystallization Candidates
- → docs/learnings/: parser-backed trust boundaries and bootstrap-safe CI behavior at shell edges.
- → tips/meta/: future deep reviews should explicitly probe quoted paths, newline filenames, and ambient-binary trust fallbacks.
- → scripts/: keep pushing trust-boundary logic out of shell and into small tested helpers.
