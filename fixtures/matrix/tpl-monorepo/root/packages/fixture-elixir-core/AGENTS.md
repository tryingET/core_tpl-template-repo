# AGENTS.md — fixture-elixir-core

## Intent
Package inside monorepo: library (elixir)

## Guardrails
- No secrets in code.
- NO `.git` — managed by parent monorepo.
- NO `.github` — CI runs from monorepo root.
- NO release tooling — released from monorepo root.
- Deferred work and explicit task scope live at the monorepo root; do not create standalone AK/task-scope state in this member.

## AK-native route guardrails
- If the parent monorepo declares AK-native task, direction, or route authority, run package AK route checks from the monorepo root: read the root AK task and route/open-frame status before inventing package work.
- Generic operator input such as `proceed` continues the active root execution task when one exists; it does not authorize lifecycle closeout, source-owner mutation, publication, or knowledge promotion.
- Treat package docs and generated files as projections unless the monorepo declares otherwise; hand off Prompt Vault, ROCS, Pi/runtime, KES, steward/publication, template propagation, Oracle/DSPx, and other repo facts to their owners.
- Prefer parent/root `docs/project/vision.md` as durable product direction where present and `docs/project/product_posture.md` as a product-maturity bridge, not a queue, roadmap, changelog, or execution authority.
- Do not revive SG/TG/OP markdown planning where AK-native direction authority is declared; legacy `strategic_goals.md`, `tactical_goals.md`, `operating_plan.md`, or `operational_plan.md` files are archive/projection only unless a repo-local owner decision explicitly says otherwise.

## Deterministic tooling policy (ROCS-first)
- Run ROCS commands from monorepo root: `../../scripts/rocs.sh <args...>`
- When package work needs AK context, run it from the monorepo root with plain installed `ak <args...>`.
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
