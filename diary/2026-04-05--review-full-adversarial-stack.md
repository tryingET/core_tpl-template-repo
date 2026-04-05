# 2026-04-05 — Full adversarial stack review

## What I Did
- Ran `bash ./scripts/check-l0.sh` from repo root; full suite passed.
- Reproduced a silent override failure in `scripts/check-doc-references.sh` with `DOC_REF_CHECK_SCRIPT=/definitely/missing`.
- Reproduced repo-census undercount for symlinked repo surfaces with `./scripts/preflight-repo-census.sh <scope>`.
- Reproduced ROCS runner misselection by copying `scripts/rocs.sh` into a temp repo with an empty `tools/rocs-cli/`; `--which` returned success while `version` failed.
- Reproduced late migration failure by running `scripts/migrate-l1-structure.sh` in an environment whose `PATH` excluded `rsync`; failure occurred at the first copy step after stage creation.
- Collected `git blame` for implicated lines to back Underground Time in the review output.

## What Surprised Me
- The main L0 validation suite stayed fully green while all four edge cases remained exploitable.
- `check-doc-references.sh` self-heals into workspace fallback behavior, which makes the override bug easy to miss.
- `scripts/rocs.sh --which` can report a valid vendored runner even when the vendored directory is not a runnable project.
- `migrate-l1-structure.sh` gets far enough to create and partially populate a stage before failing on missing `rsync`.

## Patterns
- Fail-open override handling hidden behind command substitution.
- Path-existence checks used as runtime-validity checks.
- Discovery helpers hardened for deep repos/worktrees but not for symlinked surfaces.
- Migration scripts rely on external tools without preflight checks, so errors arrive after side effects.

## Crystallization Candidates
- → docs/learnings/: shell wrapper fail-open patterns (`$(...)` swallowing intended exits; directory existence != valid tool/project)
- → tips/meta/: add adversarial checks for invalid override paths, empty vendored tool dirs, symlinked repo census, and missing external tool dependencies
