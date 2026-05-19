---
summary: "Canonical contract for propagating engineering-core lane metadata and local overrides through L0 -> L1 -> L2 templates."
read_when:
  - "Adding or changing engineering guidance in templates."
  - "Asking where policy/engineering-lane.json and docs/engineering.local.md should exist."
  - "Auditing whether generated repos have an explicit engineering contract."
system4d:
  container: "Stack-contract propagation only; does not redefine the lane docs themselves."
  compass: "Make stack selection inspectable, repeatable, and machine-checkable across generated repos."
  engine: "Declare upstream lane reference -> record local override -> validate metadata -> optionally smoke the CLI."
  fog: "Drift appears when lane prose exists without explicit per-repo artifacts."
---

# Engineering contract (L0 -> L1 -> L2)

This is the canonical document for how `engineering-core` should appear in generated repositories.

## Contract surface

When a repo or package maps to a shared `engineering-core` lane, prefer this explicit surface:

1. `policy/engineering-lane.json`
   - declares the upstream lane reference
   - records the executable retrieval command
   - records catalog/list commands used by `engineering-core scan-adoption`
   - records the default selected disciplines for the generated repo/package
   - records how that command resolves the upstream lane provenance
   - is the machine-readable source of truth
2. `docs/engineering.local.md`
   - records repo/package-local deltas on top of the upstream lane contract
   - is the human-readable local override
3. validation scripts
   - must at least verify declared lane metadata
   - should smoke the declared `engineering_core.command` when the local workspace can resolve `engineering-core`

## Read / consult order

When an operator or agent needs engineering guidance, use this order:

1. `policy/engineering-lane.json`
   - source of truth for lane identity + executable upstream retrieval
2. `docs/engineering.local.md`
   - source of truth for repo/package-local deltas
3. upstream lane output returned by `policy/engineering-lane.json` -> `engineering_core.command`

## Conditional lane companions

Upstream lane docs may ship conditional companions for narrower concerns.

Current relevant pattern:
- `engineering-<lane>.ts-quality.md` is a lane-specific `ts-quality` adoption addendum
- generated repos/packages should read it only when they are explicitly adopting deterministic screening with `ts-quality`
- generated repos/packages should keep only lightweight local rollout truth and link back to the upstream `ts-quality` adoption docs instead of copying that doctrine into every repo

## Retrieval rule

- Generated repos currently resolve `engineering-core` from a workspace-local checkout.
- Record that honestly in `policy/engineering-lane.json` as `ref: workspace-local-unpinned` for local AI Society generation. External consumers may revise the policy to a released tag such as `v0.3.3` after generation.
- Prefer `uv tool -n run --from ...` for that workspace-local command so uv does not silently reuse a stale cached build.
- Include `catalog_command`, `list_disciplines_command`, and `list_templates_command` so adoption scanners can distinguish complete engineering-core adoption from older tech-stack-style lane notes.
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
- project repos: add `policy/engineering-lane.json` + `docs/engineering.local.md` when a lane exists
- monorepos: root ships `policy/engineering-lane.json` with `lane_status: monorepo_control_plane` plus `docs/engineering.local.md`; generated members carry language-specific lane artifacts
- packages/apps: add `policy/engineering-lane.json` + `docs/engineering.local.md` when a lane exists

## Current lane mapping used in templates

- Python -> `py`
- TypeScript -> `ts`
- Node -> `ts` (closest shared lane until a dedicated node lane exists)
- Go -> `go`
- Rust -> `rust`
- Elixir -> `elixir`

## Default discipline selection

Generated stack-bearing repos/packages start with these portable disciplines:

- `validation`
- `testing`
- `security-privacy`
- `documentation`
- `dependency-governance`

Repo/package owners should add narrower disciplines such as `accessibility`, `design-system`, `service-api`, `local-first-data`, `observability`, `data-governance`, `ai-ml`, or `performance` when the generated surface proves that concern.

## Downstream rollout rule

When propagating one affected file into downstream generated repos, use:
- `[[docs/dev/single-file-propagation-playbook.md]]`

Do not recopy whole repos casually for stack-contract updates with large blast radius.

## Maintenance rule

When changing the engineering contract:
1. update the L0 template source files
2. update this doc if the contract meaning changes
3. refresh baseline fixtures and the language/member matrix
4. run `engineering-core scan-adoption` against generated fixtures when scanner semantics are affected
5. run L0 validation
