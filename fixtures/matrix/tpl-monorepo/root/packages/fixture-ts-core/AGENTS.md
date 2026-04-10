# AGENTS.md — fixture-ts-core

## Intent
Package inside monorepo: library (typescript)

## Guardrails
- No secrets in code.
- NO `.git` — managed by parent monorepo.
- NO `.github` — CI runs from monorepo root.
- NO release tooling — released from monorepo root.
- Deferred work and explicit task scope live at the monorepo root; do not create standalone AK/task-scope state in this member.

## Deterministic tooling policy (ROCS-first)
- Run ROCS commands from monorepo root: `../../scripts/rocs.sh <args...>`
- When package work needs AK context, run it from the monorepo root with plain installed `ak <args...>`. If the monorepo still ships `./scripts/ak.sh`, treat it as launcher implementation detail behind installed `ak`, not as a second AK family.
- For ontology/policy checks, use ROCS commands as the default execution path.

## Stack contract
- When this package language maps to a shared `tech-stack-core` lane, keep it explicit:
  - `policy/stack-lane.json` declares the upstream lane reference and the executable retrieval command
  - `docs/tech-stack.local.md` records package-local overrides on top of that lane contract
  - consult `policy/stack-lane.json` before invoking `tech-stack-core` directly; do not assume package-local `lanes/` overrides exist

## Structure
```
src/              # Source code
tests/            # Test files
docs/             # Package docs
```

Common language-specific files you may add as the package matures:
- `pyproject.toml` — Python
- `package.json` — Node / TypeScript
- `Cargo.toml` — Rust
- `go.mod` — Go
- `mix.exs` — Elixir

## Recursion policy
This package is an internal member of an L2 monorepo, not a separate render layer.
- No further nesting allowed inside this member.
- All packages in the monorepo share root workspace config.

## Read order
1) `docs/` — package docs
2) `src/` — source code
3) `tests/` — test files
4) `diary/` — session notes
