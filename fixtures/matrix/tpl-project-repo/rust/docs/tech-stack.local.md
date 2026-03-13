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

- `tech-stack-core show rust --prefer-repo`
- `uv tool run --from ~/ai-society/core/tech-stack-core tech-stack-core show rust --prefer-repo`

Executable contract surface:

- `policy/stack-lane.json` pins the upstream lane and retrieval command.
- `docs/tech-stack.local.md` records repo-local deltas.
- Repo validation should at least verify the pinned lane metadata.

Repo-local emphasis:

- Keep workflow scripts and docs aligned with the pinned lane.
- Prefer local deterministic wrappers before ad-hoc commands.
- Update this file when local practice intentionally diverges from the upstream lane.