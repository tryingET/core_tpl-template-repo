---
summary: "Repo-local override notes for the shared tech-stack-core lane used by this repo."
read_when:
  - "Aligning implementation decisions with the stack baseline for this project repo."
  - "Reconciling local workflow differences with shared lane guidance."
system4d:
  container: "Repo-local deltas on top of shared lane guidance."
  compass: "Keep project work reproducible while preserving local constraints."
  engine: "Use shared lane -> apply local override -> validate with repo scripts."
  fog: "Upstream lane guidance may evolve independently of this repo."
---

# tech-stack.local (project repo)

Primary lane:

- `elixir`
- executable upstream retrieval lives in `policy/stack-lane.json` -> `tech_stack_core.command`

Executable contract surface:

- `policy/stack-lane.json` pins the upstream lane and retrieval command.
- `docs/tech-stack.local.md` records repo-local deltas.
- Repo validation should at least verify the pinned lane metadata and may smoke the pinned command when available.

Repo-local emphasis:

- This file is the local override layer on top of the upstream lane.
- Keep workflow scripts and docs aligned with the pinned lane.
- Prefer local deterministic wrappers before ad-hoc commands.
- Update this file when local practice intentionally diverges from the upstream lane.