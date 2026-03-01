---
summary: "Canonical file contract for tpl-project-repo across L0 -> L1 -> L2, including deep-review findings and simplification decisions."
read_when:
  - "When changing tpl-project-repo structure"
  - "When asking 'what goes where' during L0 -> L1 -> L2 generation"
  - "When deciding whether project template files are too much or too little"
system4d:
  container:
    boundary: "tpl-project-repo file surface and generation path only."
    edges:
      - "[[README.md]]"
      - "[[scripts/new-l1-from-copier.sh]]"
      - "[[scripts/preview-l1-diff.sh]]"
      - "[[copier/tpl-project-repo/copier.yml]]"
      - "[[copier/tpl-project-repo/README.md.j2]]"
  compass:
    driver: "Make project-template structure legible, minimal, and auditable."
    outcome: "One authoritative map replaces scattered or stale explanations."
  engine:
    invariants:
      - "L0 authoring path is canonical; L1/L2 are rendered artifacts."
      - "Every shipped file must have a reason; generated artifacts must stay out of git."
      - "Schema docs must match schema files and seed data."
  fog:
    risks:
      - "Documentation drift between README/AGENTS/template files"
      - "Template bloat from accidental generated artifacts"
      - "Validation theater (schemas that look real but do not constrain output)"
---

# tpl-project-repo File Contract (L0 -> L1 -> L2)

This is the **single authoritative document** for what `tpl-project-repo` contains, why it contains it, and where each piece lives across layers.

If another doc disagrees with this one, treat this doc as the source to reconcile from.

## 0) Executive answer (what goes where)

| Layer | What lives here | Canonical path |
|---|---|---|
| **L0** | Authoring source of the project template | `core/tpl-template-repo/copier-template/copier/tpl-project-repo/` |
| **L1** | Rendered template repository embedding the project template | `<company>-templates/copier/tpl-project-repo/` |
| **L2** | Instantiated project repository | `<company>/<repo>/` |

Render chain:
1. L0 -> L1 via `[[scripts/new-l1-from-copier.sh]]` + `[[copier.yml]]`
2. L1 -> L2 via `[[scripts/new-repo-from-copier.sh]]` + `[[copier/tpl-project-repo/copier.yml]]`

---

## 1) tpl-project-repo output inventory (default, software pack off)

Default L2 output is intentionally split into 6 domains:

### A. Repo control plane (must exist)
- `.copier-answers.yml` (render provenance)
- `AGENTS.md` (repo operating contract)
- `CODEOWNERS` (review authority boundaries)
- `README.md` (entrypoint)

### B. Delivery documentation (minimal but complete)
- `docs/_core/` (core snapshot placeholder)
- `docs/org_context/` (org constraints snapshot)
- `docs/project/` (purpose/mission/vision/model/goals)
- `docs/system4d/` (container/compass/engine/fog)
- `docs/dev/` (status + next steps)
- `docs/decisions/`, `docs/learnings/`

### C. Governance model
- `governance/work-items.cue` (validation contract)
- `governance/work-items.json` (seed planning model)
- `governance/README.md` (usage + boundaries)

### D. Ontology + validation toolchain
- `ontology/manifest.yaml`, `ontology/src/**`
- `scripts/rocs.sh`
- `tools/rocs-cli/` (vendored deterministic runner source)

### E. CI surface
- `.gitlab-ci.yml`
- `gitlab/ci/rocs.yml`
- `scripts/ci/smoke.sh`, `scripts/ci/full.sh`
- `.gitlab/merge_request_templates/CHANGE.md`
- `.gitlab/issue_templates/SLICE.md`

### F. Product-code placeholders
- `src/.gitkeep`
- `tests/.gitkeep`
- `policy/.gitkeep`
- `scripts/.gitkeep`

### Conditional files (software pack)
Enabled only when `enable_software_pack=true`:
- Python: `pyproject.toml`
- Node: `package.json`
- TypeScript: `package.json`, `tsconfig.json`
- Rust: `Cargo.toml`
- Go: `go.mod`

---

## 2) Deep Review (adversarial stack)

## 2.1 INVERSION (Shadow Analysis)
- **Hidden bug:** template looked deterministic while shipping compiled artifacts (`__pycache__`, `build/`, `*.egg-info`) in L0 source.
  - Assumption that hid it: "exclude rules in L2 copier.yml are enough".
  - Pattern genus: generated-artifact contamination in template sources.
- **Hidden bug:** work-items docs/schema/seed looked coherent but were semantically misaligned.
  - Assumption that hid it: "presence of CUE file implies real validation".
  - Pattern genus: validation theater.
- **Hidden gap:** L1 docs mentioned `docs/project/governance_overlay.md` that did not exist.
  - Assumption that hid it: copied historical narrative without path verification.
  - Pattern genus: stale topology references.

## 2.2 TELESCOPIC (Micro + Macro)
- **Micro issues**
  - accidental generated artifacts in `tools/rocs-cli` source tree
  - mismatched `work-items.cue` vs `work-items.json`
  - misleading field guidance (`TODO comments`) in governance README
- **Macro issue**
  - no single file-contract doc, causing duplication and drift across README/AGENTS/template docs
- **Synthesis**
  - macro drift produced micro contradictions; micro contradictions then obscured trust in the template baseline.

## 2.3 NEXUS (Highest-Leverage Intervention)
**Intervention:** establish one canonical file-contract document and force adjacent docs to link to it.

Cascade:
1. immediate: removes ambiguity about L0/L1/L2 placement
2. secondary: exposes stale references quickly
3. tertiary: makes template changes reviewable by contract
4. fourth-order: enables deterministic drift checks as policy, not folklore

## 2.4 AUDIT (Quality Tetrahedron)
- **BUGS**
  - generated artifacts committed in template source
  - stale governance overlay references
- **DEBT**
  - duplicate descriptions of project-template layering across multiple docs
- **SMELLS**
  - parameter surfaces that imply behavior not visible in file topology
- **GAPS**
  - missing canonical map from L0 source path to L1/L2 output paths
- **Root cause**
  - documentation authority was distributed instead of centralized.

## 2.5 BLAST RADIUS (Impact Mapping)
- **Direct:** project-template docs, governance schema seed, and source cleanliness
- **Secondary:** generated L1 fixture and generated L2 fixture outputs
- **Tertiary:** operator onboarding speed and confidence in template contracts
- **Failure scenarios if wrong:** broken fixture parity or stale link targets; mitigated by `[[scripts/check-l0-fixtures.sh]]` and `[[scripts/check-l0-guardrails.sh]]`

## 2.6 ESCAPE HATCH (Rollback Design)
- **Class:** reversible
- **Rollback procedure:**
  1. `git restore -- copier-template/copier/tpl-project-repo`
  2. `git restore -- copier-template/README.md.jinja copier-template/AGENTS.md README.md`
  3. `git restore -- fixtures/l1/template-repo fixtures/l2/tpl-project-repo`

## 2.7 RANKED BUGS
| Bug | File | Severity | Underground time |
|---|---|---:|---:|
| Generated artifact contamination | `copier/tpl-project-repo/tools/rocs-cli/**` | High | Long |
| Schema/seed mismatch | `copier/tpl-project-repo/governance/work-items.*` | High | Long |
| Stale path reference | `README.md.jinja`, `AGENTS.md` (L1 template) | Medium | Long |

## 2.8 ROLLBACK COMMANDS
```bash
# If this change set is wrong, revert the touched surface:
git restore -- \
  copier-template/copier/tpl-project-repo \
  copier-template/README.md.jinja \
  copier-template/AGENTS.md \
  README.md \
  fixtures/l1/template-repo \
  fixtures/l2/tpl-project-repo
```

## 2.9 CRYSTALLIZED LEARNINGS
- Canonical docs must be singular; all other docs should point, not re-describe.
- Template repos should never carry build outputs or interpreter caches.
- A schema file is not a contract unless seed data actually conforms and validation constrains root fields.

---

## 3) Decisions in this pass

1. **Kept** the overall project template shape (docs/governance/ontology/code placeholders).
2. **Removed** generated Python build/cache metadata from template source.
3. **Aligned** `work-items.cue`, `work-items.json`, and governance README semantics.
4. **Corrected** L1 docs that referenced non-existent governance overlay paths.
5. **Consolidated** authority here; other docs now link instead of duplicating outdated explanations.

---

## 4) Maintenance rule (non-negotiable)

When changing `tpl-project-repo`, update in this order:
1. `[[copier/tpl-project-repo/**]]`
2. this file (`[[docs/dev/tpl-project-repo-file-contract.md]]`)
3. regenerate fixtures (`[[scripts/sync-l0-fixtures.sh]]`)
4. validate (`[[scripts/check-l0.sh]]`)

If step 2 is skipped, the change is incomplete.
