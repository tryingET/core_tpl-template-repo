---
summary: "Historical task-851 note for the old copied launcher-wrapper distribution model. Kept only as bounded history after generic `scripts/ak.sh` / `scripts/cargo-operator.sh` distribution was retired in favor of plain installed `ak`."
read_when:
  - "You are reviewing task 851 history."
  - "You need to know why older docs mention tpl-template-repo as a distribution authority for copied AK launcher wrappers."
type: "note"
---

# Historical generic launcher wrapper template authority

This note is **historical**.
It records the old task-851 boundary used while generic copied launcher wrappers were still distributed through templates.

Current truth is simpler:
- generic copied `scripts/ak.sh` / `scripts/cargo-operator.sh` distribution is being removed from template/generated repos
- plain installed `ak` is the public/operator path
- `softwareco/owned/agent-kernel` remains the owner of the shared launcher behavior that plain `ak` enters
- template repos should not reintroduce copied launcher-resolution bundles as a generic pattern

What remains historically true about the old packet:
- `softwareco/owned/agent-kernel` was the runtime/reference owner
- `core/tpl-template-repo` distributed copied wrapper artifacts through templates/fixtures
- `holdingco/infra/template-propagator` owned rollout/proof reporting for live downstream repos

Do not use this note to justify reviving copied generic launcher wrappers.
Use it only to interpret older receipts, diary entries, or historical rollout language.
