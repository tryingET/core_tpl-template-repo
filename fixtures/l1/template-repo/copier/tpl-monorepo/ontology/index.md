---
summary: "Ontology Index repo."
read_when:
  - "Read when changing or validating generated tpl-monorepo documentation for ontology index repo."
type: "reference"
---

# Ontology Index (repo)

Start here when browsing manually.

- `ontology/manifest.yaml` — which layers apply
- `ontology/src/system4d.yaml` — monorepo-root System4D (packages/apps inherit it)
- `ontology/src/reference/concepts/` — repo-local concepts (only when needed)
- `ontology/src/bridge/mapping.yaml` — map concepts to code symbols
- `ontology/dist/` — generated artifacts (tool-first)

Tip: use `./scripts/rocs.sh pack <concept_id> --repo .` instead of opening many files (the launcher resolves ref layers from the enclosing workspace; set `ROCS_WORKSPACE_ROOT` only when the repo lives outside it).
