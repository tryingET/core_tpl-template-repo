# AGENTS.md — fixture-core

## Intent
Package inside monorepo: library (python)

## Guardrails
- No secrets in code.
- NO `.git` — managed by parent monorepo.
- NO `.github` — CI runs from monorepo root.
- NO release tooling — released from monorepo root.

## Deterministic tooling policy (ROCS-first)
- Run ROCS commands from monorepo root: `../../scripts/rocs.sh <args...>`
- For ontology/policy checks, use ROCS commands as the default execution path.

## Stack contract
- When this package language maps to a shared `tech-stack-core` lane, keep it explicit:
  - `policy/stack-lane.json` pins the upstream lane
  - `docs/tech-stack.local.md` records package-local overrides
  - prefer `uv tool run --from ~/ai-society/core/tech-stack-core tech-stack-core show <lane> --prefer-repo` when consulting upstream lane docs

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
This is L3 (inside monorepo L2).
- No further nesting allowed.
- All packages in monorepo share root workspace config.

## Read order
1) `docs/` — package docs
2) `src/` — source code
3) `tests/` — test files
4) `diary/` — session notes
