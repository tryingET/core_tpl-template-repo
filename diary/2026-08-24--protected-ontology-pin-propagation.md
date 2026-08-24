---
summary: "Propagate ontology-kernel v0.2.0 as the protected tpl-project-repo default."
type: diary
---

# Protected ontology pin propagation

AK task `4959` changes only the `tpl-project-repo` core-ontology default from rolling `@main` to
immutable release `@v0.2.0`, updates the assertions that guard that default, and regenerates L0
fixtures. Other template archetypes retain their independent defaults.
