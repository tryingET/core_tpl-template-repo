# 2026-04-05 — Nexus helper parity, language matrix, and stack wording

## What I Did
- Claimed repo-local AK task `#792` for the language/package-manager matrix follow-through.
- Fixed `tpl-project-repo` software-pack cleanup so Node and TypeScript project renders preserve `package.json` and TypeScript keeps `tsconfig.json`.
- Hardened `scripts/lib/copier-answers.sh` to fail closed on tagged YAML fallback values and propagated the canonical helper into L1/L2 template copies.
- Added parity checks so shared `copier-answers.sh` and `repo-surface.sh` copies must stay identical across L0/L1/L2 template surfaces.
- Expanded the project-language matrix to include Node and TypeScript in generation checks, fixture sync, and fixture drift validation.
- Reworded stack-contract docs from “pinned” to “declared” where the emitted provenance is `workspace-local-unpinned`.
- Refreshed fixtures, ran `bash ./scripts/check-l0-generation.sh`, `bash ./scripts/check-l0-fixtures.sh`, and `bash ./scripts/check-l0.sh`, and recorded evidence `#416` (`validation:check-l0 = pass`).

## What Surprised Me
- The first `check-l0.sh` failure was not semantic but ordering: a new assertion in generated `check-template-ci.sh` ran before the helper function it needed existed.
- The project-language matrix had good coverage for Python/Rust/Elixir, but Node/TypeScript were entirely absent despite sharing the same cleanup branch that controlled `package.json`.

## Patterns
- Shared shell helpers are dangerous when copied without parity checks.
- Fallback parser bugs hide behind developer environments with richer dependencies.
- Contract prose drifts unless tests assert semantics, not just file presence.

## Crystallization Candidates
- → docs/learnings/2026-04-05-shared-helper-copies-need-parity-checks.md
- → future TIP if more shared helper families start drifting the same way
