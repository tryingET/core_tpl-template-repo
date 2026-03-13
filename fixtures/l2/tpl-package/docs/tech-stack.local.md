---
summary: "Package-local override notes for the shared tech-stack-core lane used by this package."
read_when:
  - "Aligning implementation decisions with the package stack baseline."
  - "Reconciling local workflow differences with shared lane guidance."
system4d:
  container: "Package-local deltas on top of shared lane guidance."
  compass: "Keep package work reproducible while preserving monorepo compatibility."
  engine: "Use shared lane -> apply local override -> validate via monorepo/package scripts."
  fog: "Package-local practice can drift from the pinned lane unless the contract stays explicit."
---

# tech-stack.local (package)

Primary lane:

- `tech-stack-core show py --prefer-repo`
- `uv tool run --from ~/ai-society/core/tech-stack-core tech-stack-core show py --prefer-repo`

Executable contract surface:

- `policy/stack-lane.json` pins the upstream lane and retrieval command.
- `docs/tech-stack.local.md` records package-local deltas.
- Package or monorepo validation should at least verify the pinned lane metadata.