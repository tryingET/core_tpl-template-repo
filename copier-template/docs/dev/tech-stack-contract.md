---
summary: "Canonical contract for propagating tech-stack-core lane metadata and local overrides through L0 -> L1 -> L2 templates."
read_when:
  - "Adding or changing stack guidance in templates."
  - "Asking where policy/stack-lane.json and docs/tech-stack.local.md should exist."
  - "Auditing whether generated repos have an explicit stack contract."
system4d:
  container: "Stack-contract propagation only; does not redefine the lane docs themselves."
  compass: "Make stack selection inspectable, repeatable, and machine-checkable across generated repos."
  engine: "Pin upstream lane -> record local override -> validate metadata -> optionally smoke the CLI."
  fog: "Drift appears when lane prose exists without explicit per-repo artifacts."
---

# Tech-stack contract (L0 -> L1 -> L2)

This is the canonical document for how `tech-stack-core` should appear in generated repositories.

## Contract surface

When a repo or package maps to a shared `tech-stack-core` lane, prefer this explicit surface:

1. `policy/stack-lane.json`
   - pins the upstream lane name
   - records the executable retrieval command
   - records how that command resolves the upstream lane provenance
   - is the machine-readable source of truth
2. `docs/tech-stack.local.md`
   - records repo/package-local deltas on top of the upstream lane
   - is the human-readable local override
3. validation scripts
   - must at least verify pinned lane metadata
   - should smoke the pinned `tech_stack_core.command` when the local workspace can resolve `tech-stack-core`

## Read / consult order

When an operator or agent needs stack guidance, use this order:

1. `policy/stack-lane.json`
   - source of truth for lane identity + executable upstream retrieval
2. `docs/tech-stack.local.md`
   - source of truth for repo/package-local deltas
3. upstream lane output returned by `policy/stack-lane.json` -> `tech_stack_core.command`

## Retrieval rule

- Generated repos currently resolve `tech-stack-core` from a workspace-local checkout.
- Record that honestly in `policy/stack-lane.json` as `ref: workspace-local-unpinned` until a real released ref is pinned.
- Do **not** append `--prefer-repo` unless the generated repo actually ships trusted local `lanes/` overrides.

## Layer rules

### L0 (`core/tpl-template-repo`)
- author the contract in template sources
- document the contract once, centrally
- keep fixtures in sync so drift is visible
- maintain a language/member matrix for stack-bearing archetypes:
  - `fixtures/matrix/tpl-project-repo/<language>/`
  - `fixtures/matrix/tpl-monorepo/root/` with language-varied generated members under `packages/`

### L1 (company template repos)
- inherit the L0 contract artifacts
- keep company-specific overrides minimal

### L2 (generated repos)
- project repos: add `policy/stack-lane.json` + `docs/tech-stack.local.md` when a lane exists
- monorepos: root ships `docs/tech-stack.local.md`; generated members carry language-specific lane artifacts
- packages/apps: add `policy/stack-lane.json` + `docs/tech-stack.local.md` when a lane exists

## Current lane mapping used in templates

- Python -> `py`
- TypeScript -> `ts`
- Node -> `ts` (closest shared lane until a dedicated node lane exists)
- Go -> `go`
- Rust -> `rust`
- Elixir -> `elixir`

## Downstream rollout rule

When propagating one affected file into downstream generated repos, use:
- `[[docs/dev/single-file-propagation-playbook.md]]`

Do not recopy whole repos casually for stack-contract updates with large blast radius.

## Maintenance rule

When changing the stack contract:
1. update the L0 template source files
2. update this doc if the contract meaning changes
3. refresh baseline fixtures and the language/member matrix
4. run L0 validation
