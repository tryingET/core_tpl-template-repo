---
summary: "Package-local override notes for the shared tech-stack-core lane used by this package."
read_when:
  - "Aligning implementation decisions with the package stack baseline."
  - "Reconciling local workflow differences with shared lane guidance."
system4d:
  container: "Package-local deltas on top of shared lane guidance."
  compass: "Keep package work reproducible while preserving monorepo compatibility."
  engine: "Use shared lane -> apply local override -> validate via monorepo/package scripts."
  fog: "Package-local practice can drift from the declared lane contract unless the contract stays explicit."
---

# tech-stack.local (package)

Primary lane:

- `elixir`
- executable upstream retrieval lives in `policy/stack-lane.json` -> `tech_stack_core.command`

Executable contract surface:

- `policy/stack-lane.json` declares the upstream lane reference and retrieval command.
- `docs/tech-stack.local.md` records package-local deltas.
- Package or monorepo validation should at least verify the declared lane metadata and may smoke the declared command when available.

Package-local emphasis:

- This file is the local override layer on top of the upstream lane contract.
- Keep package docs and package-level scripts aligned with the declared lane contract.
- Prefer monorepo/package deterministic wrappers before ad-hoc commands.
- Update this file when local practice intentionally diverges from the upstream lane.
- If the upstream lane ships a conditional `tech-stack-<lane>.ts-quality.md` addendum and this package adopts `ts-quality`, keep package-local rollout truth in `docs/project/ts-quality-current-vs-target.md` and keep the detailed adoption doctrine upstream in the `ts-quality` repo.