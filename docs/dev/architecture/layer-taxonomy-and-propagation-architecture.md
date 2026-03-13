---
summary: "Canonical layer taxonomy and propagation architecture for L0/L1/L2/L3 changes, including how to treat lane roots, standalone repos, monorepos, and monorepo members without collapsing them into one naming scheme."
read_when:
  - "When deciding what L0, L1, L2, and L3 actually mean in AI Society templates"
  - "When designing single-file or multi-file propagation across template generations"
  - "When a physically nested repo makes the layer model feel ambiguous"
type: "explanation"
system4d:
  container:
    boundary: "Layer naming and propagation architecture for template-derived repos only; not runtime task semantics."
    edges:
      - "[[README.md]]"
      - "[[docs/dev/README.md]]"
      - "[[docs/dev/single-file-propagation-playbook.md]]"
      - "[[docs/l1-adoption-playbook.md]]"
      - "[[docs/l2-transition-playbook.md]]"
  compass:
    driver: "Separate render lineage from physical nesting so propagation rules stay correct."
    outcome: "A change can target the right descendants without confusing lane roots, standalone repos, and monorepo members."
  engine:
    invariants:
      - "L0/L1/L2/L3 name render lineage, not just filesystem depth."
      - "Lane roots and group roots do not automatically create a new render layer."
      - "L3 is reserved for members generated inside an L2 monorepo, not every repo nested under another repo path."
  fog:
    risks:
      - "People overloading L0/L1/L2/L3 to mean AGENTS scope, git nesting, and generation lineage at the same time."
      - "Blind descendant propagation that touches repos with the wrong authority boundary."
---

# Layer Taxonomy and Propagation Architecture

## Problem

The current naming pressure comes from several different concepts being informally collapsed into one stack:

- template generation lineage (`L0 -> L1 -> L2 -> L3`)
- filesystem ancestry
- AGENTS scope layering (workspace/company/group/repo)
- git nesting (for example lane-root repos containing child repos)
- monorepo membership

That collapse is what makes propagation planning feel ambiguous.

The architecture below separates those concerns so a propagation plan can target the correct population without inventing fake layers.

---

## 1) Canonical meaning of L0 / L1 / L2 / L3

### L0 — meta-template authoring source

**What it is**
- the authoring source that renders company template repos

**Canonical example**
- `~/ai-society/core/tpl-template-repo`

**Authority**
- owns template-generation contracts
- owns propagation playbooks
- owns fixture truth for generated baselines

**Allowed outbound transition**
- `L0 -> L1`

---

### L1 — company template repo generated from L0

**What it is**
- a company-root template/control-plane repo generated from L0
- embeds L2 templates and company-specific policy

**Canonical examples**
- `~/ai-society/softwareco`
- `~/ai-society/holdingco`

**Authority**
- company policy
- lane layout
- embedded L2 template catalog
- company-level deterministic wrappers

**Allowed outbound transition**
- `L1 -> L2`

---

### L2 — standalone repo generated from L1

**What it is**
- a repo generated from an L1 template and managed as its own repo boundary
- may be a project repo, agent repo, org repo, monorepo root, or a special lane-root/group-root control-plane repo

**Canonical examples**
- `softwareco/owned/agent-kernel`
- `softwareco/infra/issue-tracker`
- `softwareco/fork/pi-mono`
- a lane-root control-plane repo created under `fork/` or another lane
- a monorepo root created from `tpl-monorepo`

**Important rule**
A repo does **not** stop being L2 just because it is physically nested under a lane root or grouping root.
If it is a standalone repo generated from L1 and has its own repo authority boundary, it is still L2.

---

### L3 — member generated inside an L2 monorepo

**What it is**
- a package/app/member generated inside an L2 monorepo root
- managed by the monorepo, not by its own `.git`

**Canonical examples**
- `packages/<name>/`
- `apps/<name>/`
- anything generated from `tpl-package` inside a monorepo L2

**Important rule**
L3 is **not** “any repo nested under another repo path”.
L3 is specifically the monorepo-internal layer.

---

## 2) What is *not* a layer

These are real concepts, but they are **orthogonal** to L0/L1/L2/L3.

### A. AGENTS scope layering
Examples:
- workspace-level AGENTS
- company-level AGENTS
- group/lane-level AGENTS
- repo-level AGENTS

This is a **policy scope hierarchy**, not a generation-layer hierarchy.

### B. Filesystem ancestry
A path being nested three directories deep does not make it L3.

### C. Git nesting or lane-root nesting
A standalone repo under a lane-root repo is still L2 unless it is a monorepo member.

### D. Lane / group identity
`owned/`, `infra/`, `contrib/`, `agents/`, `fork/` are routing/grouping categories, not generation layers by themselves.

---

## 3) Special-case clarification: lane roots and grouping roots

Lane roots are easy to misname because they can be both:
- a grouping surface in a company repo
- and sometimes a standalone git repo with its own control-plane baseline

### Architectural rule
Treat a lane-root/group-root as a **kind of L2 control-plane repo** when it is initialized as its own repo.

But do **not** infer that child repos inside it become L3.

### Why
Because the render lineage is still:
- L0 authoring source
- L1 company template repo
- L2 standalone repo(s)

The lane root changes grouping and local policy context, but not the fundamental render-layer meaning of its standalone child repos.

---

## 4) Canonical propagation graph

### Render-lineage graph

```text
L0 meta-template source
  -> L1 company template repos
     -> L2 standalone repos
        -> L3 monorepo members only
```

### Important boundary
There is **no general rule** that says:

```text
L2 repo -> another standalone child repo = L3
```

That is false except for the monorepo-member case.

---

## 5) Propagation architecture

The propagation system should target **render lineage + entity type**, not just path depth.

### Propagation dimensions
A change should declare all of the following:

1. **source layer**
   - L0, L1, or local-only
2. **target layers**
   - L1 only
   - L1 + L2
   - L2 monorepo roots + L3 members
3. **target entity kinds**
   - company template repo
   - standalone project repo
   - lane-root control-plane repo
   - monorepo root
   - monorepo member
4. **provenance requirement**
   - has `.copier-answers.yml`
   - generated from known template
   - still compatible with source feature set
5. **validation contract**
   - which gate proves adoption is healthy
6. **rollback unit**
   - exact file set or feature unit to revert

### Why this model is needed
Because “apply to all descendants” is too coarse.
The right question is:

> Which layer + entity-kind population is actually eligible for this change?

---

## 6) Single-file vs multi-file propagation in this model

### Single-file propagation
Use when:
- one file is the whole feature surface
- no additional CI/doc/contract wiring is required
- target entity kinds are uniform enough to treat the file as standalone

Example:
- `scripts/docs-list.sh --quiet-success`

### Multi-file propagation
Use when the change is a **feature unit** rather than a file.

A multi-file feature unit usually includes:
- one or more scripts
- one contract/manifest file
- one or more CI checks
- one or more docs links or policy references

Example candidate:
- validation command registry

This should **not** be rolled out via the single-file playbook.
It needs a dedicated multi-file propagation architecture.

---

## 7) Architectural plan for multi-file propagation

### Phase 1 — stabilize naming
Create and adopt this taxonomy as the canonical naming model:
- L0 = authoring source
- L1 = company template repo
- L2 = standalone generated repo
- L3 = monorepo member only

### Phase 2 — define propagation unit contract
Add a feature-manifest format at L0 that declares:
- unit name
- source layer
- target layers
- target entity kinds
- exact file set
- required validations
- exclusions / incompatibilities
- rollback procedure

### Phase 3 — define eligibility engine
The propagation engine should classify repos by:
- render lineage
- entity kind
- provenance confidence
- adoption mode
  - auto-safe
  - manual-review
  - excluded

### Phase 4 — rollout modes
Support three rollout modes:
1. **preview only**
2. **apply to auto-safe targets**
3. **emit manual-adoption plan for the rest**

### Phase 5 — evidence and reporting
For each propagation run, emit:
- targets considered
- targets applied
- targets skipped
- validation results
- rollback references

---

## 8) Brownfield rules

Because many repos already exist with divergence:

- do not assume every repo with a matching path is eligible
- do not treat missing provenance as safe for automatic mutation
- do not treat nested physical placement as proof of L3
- do not apply monorepo-member rules to standalone repos under lane roots

Brownfield default should be:
- fail closed
- classify explicitly
- prefer preview and manual adoption when provenance is uncertain

---

## 9) Resulting naming guide

When speaking precisely:

- say **L0 authoring source** for `core/tpl-template-repo`
- say **L1 company template repo** for `softwareco` / `holdingco`
- say **L2 standalone repo** for normal generated repos and lane-root repos with their own repo boundary
- say **L3 monorepo member** only for package/app members inside an L2 monorepo

Avoid saying:
- “L3 because it is nested under another repo”
- “L2 because it is just two directories deep”
- “lane root creates a new generation layer automatically”

---

## 10) Recommended next step

Create a dedicated multi-file propagation playbook and make its first section depend on this taxonomy.

That playbook should assume:
- layer lineage is canonical
- entity kind is separate from layer
- rollout eligibility is provenance-aware
- monorepo-member propagation is the only default `L2 -> L3` path
