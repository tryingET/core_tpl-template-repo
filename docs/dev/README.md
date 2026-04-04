---
summary: "Single operator and agent entrypoint for repo creation and migration (L0 -> L1 -> L2)."
read_when:
  - "When asking: which doc should I read to create repos?"
  - "When transitioning existing repos to current templates"
  - "When onboarding a coding agent to template operations"
system4d:
  container:
    boundary: "Repo setup and migration workflow for tpl-template-repo users."
    edges:
      - "[[README.md]]"
      - "[[docs/l1-adoption-playbook.md]]"
      - "[[docs/l2-transition-playbook.md]]"
      - "[[copier-template/docs/dev/task-scope-migration-playbook.md]]"
      - "[[copier-template/docs/dev/tpl-project-repo-file-contract.md]]"
  compass:
    driver: "Eliminate setup/migration ambiguity with one authoritative entrypoint."
    outcome: "Operators can create or migrate repos without hunting across stale docs."
  engine:
    invariants:
      - "Use wrappers (`new-l1-from-copier.sh`, `new-repo-from-copier.sh`) instead of ad-hoc copier commands."
      - "Changes flow through branch + MR, not direct main pushes."
      - "Existing repo migration is scaffold-first; no magic in-place migrator."
  fog:
    risks:
      - "Outdated references from older docs/sessions"
      - "Partial migration that updates scaffolding but misses governance/CI contracts"
---

# Repo Setup + Transition Guide (Operator Entrypoint)

If you or your agent only read one file, read this one.

---

## 1) What to read (exactly)

### Minimal read order
1. `[[docs/dev/README.md]]` (this file)
2. `[[docs/dev/architecture/layer-taxonomy-and-propagation-architecture.md]]` (what L0/L1/L2 render lineage and monorepo membership actually mean)
3. `[[docs/l1-adoption-playbook.md]]` (L1 update flow)
4. `[[docs/l2-transition-playbook.md]]` (L2 migration flow)
5. `[[docs/dev/single-file-propagation-playbook.md]]` (safe one-file rollout pattern)
6. `[[copier-template/docs/dev/task-scope-migration-playbook.md]]` (brownfield task-scope migration/deprecation path)
7. `[[copier-template/docs/dev/tpl-project-repo-file-contract.md]]` (detailed project-template contract)

### Agent handoff line
Use this exact prompt with your coding agent:

```text
Read [[docs/dev/README.md]] completely, then execute the relevant section for my task (new L1, new L2, L1 transition, or L2 transition). Keep all work on a branch and validate with deterministic checks.
```

---

## 2) Fast routing

- Create a **new L1 company template repo** → [Section 3](#3-create-a-new-l1-company-template-repo-l0---l1)
- Create a **new L2 repo** (agent/project/org/monorepo/package) → [Section 4](#4-create-a-new-l2-repo-l1---l2)
- Update an **existing L1** to latest L0 → [Section 5](#5-transition-an-existing-l1-template-repo)
- Migrate an **old `<company>-templates` layout** to company-root L1 → [Section 5a](#5a-transition-an-old-company-templates-layout-to-company-root-l1)
- Migrate an **existing L2** to template baseline → [Section 6](#6-transition-an-existing-l2-repo)

---

## 3) Create a new L1 company repo (L0 -> L1)

Run from `core/tpl-template-repo`:

```bash
./scripts/new-l1-from-copier.sh ~/ai-society/<company> \
  -d repo_slug=<company> \
  -d company_slug=<company> \
  -d company_name="<Company Name>" \
  -d l1_org_docs_profile=rich \
  -d enable_community_pack=false \
  -d enable_release_pack=false \
  -d enable_vouch_gate=false \
  --defaults --overwrite
```

Then initialize git:

```bash
cd ~/ai-society/<company>
git init
git add .
git commit -m "Init from L0"
bash ./scripts/check-template-ci.sh
```

Bootstrap lane roots (recommended before nesting child repos):

```bash
# 1) Materialize baseline lane control-planes in parent repo
for lane in owned contrib infra agents; do
  ./scripts/bootstrap-lane-root.sh "$lane"
done

# 2) Commit lane baselines in parent repo
git add .gitignore owned contrib infra agents
git commit -m "chore: bootstrap lane root baselines"

# 3) Initialize lane-root git repos
for lane in owned contrib infra agents; do
  ./scripts/bootstrap-lane-root.sh "$lane" --init-lane-git
done
```

For custom lanes (example: `data`), use the same two-phase pattern:

```bash
./scripts/bootstrap-lane-root.sh data
git add .gitignore data
git commit -m "chore: bootstrap data lane baseline"
./scripts/bootstrap-lane-root.sh data --init-lane-git
```

Reserved L1 control-plane paths such as `docs`, `scripts`, `copier`, `governance`, `policy`, and `ontology` are not valid lane names.

**L1 Structure:**
```
<company>/
├── .git/                  ← company repo
├── .gitignore             ← lane policies (ignore child repos by default)
├── .copier-answers.yml    ← L0 provenance
├── AGENTS.md              ← company context (loaded by pi)
├── scripts/               ← shared tooling
│   ├── rocs.sh
│   ├── docs-list.sh
│   ├── new-repo-from-copier.sh
│   └── bootstrap-lane-root.sh
├── copier/                ← L2 templates
│   ├── tpl-project-repo/
│   ├── tpl-agent-repo/
│   ├── tpl-org-repo/
│   ├── tpl-monorepo/
│   └── tpl-package/
├── owned/                 ← lane root (optional, bootstrap script)
├── contrib/               ← lane root (optional, bootstrap script)
├── infra/                 ← lane root (optional, bootstrap script)
└── agents/                ← lane root (optional, bootstrap script)
```

---

## 4) Create a new L2 repo (L1 -> L2)

Run from your company repository (e.g., `~/ai-society/softwareco`):

```bash
# project (in owned/)
./scripts/new-repo-from-copier.sh tpl-project-repo ./owned/<repo> \
  -d repo_slug=<repo> --defaults --overwrite

# agent (in agents/)
./scripts/new-repo-from-copier.sh tpl-agent-repo ./agents/agent-<slug> \
  -d repo_slug=agent-<slug> --defaults --overwrite

# org handbook (at company root)
./scripts/new-repo-from-copier.sh tpl-org-repo ./<org>-handbook \
  -d repo_slug=<org>-handbook --defaults --overwrite

# monorepo (at company root)
./scripts/new-repo-from-copier.sh tpl-monorepo ./<monorepo> \
  -d repo_slug=<monorepo> -d language=python -d package_manager=uv \
  --defaults --overwrite

# package (inside monorepo)
./scripts/new-repo-from-copier.sh tpl-package ./<monorepo>/packages/<name> \
  -d package_name=<name> -d package_type=library -d language=python \
  --defaults --overwrite
```

**L2 Placement:**
| Type | Location | Has own .git? |
|------|----------|---------------|
| Project | `./owned/<repo>/` | Yes |
| Agent | `./agents/agent-<slug>/` | Yes |
| Org handbook | `./<org>-handbook/` | Yes |
| Monorepo | `./<monorepo>/` | Yes |
| Package | `./<monorepo>/packages/<name>/` | No (in monorepo) |

Note: grouping/lane-root folders are not `tpl-package` targets. Keep grouping-root ignore policies in the parent/lane bootstrap flow.

---

## 5) Transition an existing L1 company repo

Authoritative playbook:
- `[[docs/l1-adoption-playbook.md]]`
- `[[copier-template/docs/dev/task-scope-migration-playbook.md]]` when task-scope manifests or snapshot adoption are part of the L1 rollout

Minimum deterministic flow:

```bash
# from core/tpl-template-repo
./scripts/preview-l1-diff.sh ~/ai-society/<company>
```

`preview-l1-diff.sh` compares the pure L1 render surface, materializes canonical lane-root baselines when they exist, and ignores nested child repos so adoption diffs stay reviewable without hiding tracked lane-baseline drift.

Then in target L1 repo (on branch):
- apply selected changes
- run `bash ./scripts/check-template-ci.sh`
- open MR with recursion/contract notes

---

## 5a) Transition an old `<company>-templates` layout to company-root L1

Use the staged migrator from `core/tpl-template-repo` when a company still uses the older:

```text
<company>/<company>-templates
```

layout.

Basic flow:

```bash
./scripts/migrate-l1-structure.sh <company_slug> "<Company Name>"
```

If the old company root contains custom grouping roots that are not already bootstrapped lane baselines, classify them explicitly:

```bash
AI_SOCIETY_CUSTOM_LANES=data,ml-platform \
  ./scripts/migrate-l1-structure.sh <company_slug> "<Company Name>"
```

Fail-closed rules:
- Reserved L1 control-plane paths such as `docs`, `scripts`, `copier`, `governance`, `policy`, and `ontology` are never valid lanes.
- If one of those paths contains lane-like state or nested repos, repair it manually before rerunning the migrator.
- If a custom grouping root only reveals itself via nested child repos, the migrator requires `AI_SOCIETY_CUSTOM_LANES=...` instead of guessing.

The migrator is staged and non-destructive: verify the generated `<company>-stage` repo, then perform the explicit switch manually.

---

## 6) Transition an existing L2 repo

Authoritative playbook:
- `[[docs/l2-transition-playbook.md]]`
- `[[copier-template/docs/dev/task-scope-migration-playbook.md]]` when retiring legacy `governance/task-scopes/AK-*.json` files or teaching the AK-native snapshot path

Important: there is currently **no in-place auto-migrator**. Use scaffold-first migration.

For grouping/lane-root repos with nested child repos, follow the playbook’s dedicated special-case section (backup manifest, nested `.git` preservation, and control-plane merge policy for `README.md` / `AGENTS.md` / `next_session_prompt.md`).

---

## 7) Session-derived clarifications (to avoid old confusion)

The referenced session surfaced these recurring traps. This guide resolves them:

1. **"Where is the howto?"**
   - Answer: this file is now the canonical entrypoint.
2. **"What goes where in L0/L1/L2?"**
   - Answer: use this file for operations + `tpl-project-repo-file-contract` for detailed project-template topology.
3. **"Can I migrate old repos in place automatically?"**
   - Answer: not yet; use scaffold-first deterministic migration.
4. **"Some docs feel stale/out-of-date."**
   - Answer: treat this file as authority for setup/transition, then follow linked playbooks.

---

## 8) Definition of done (for setup or migration)

You are done when:
- target repo is on a branch,
- wrapper-driven generation/migration completed,
- deterministic checks pass,
- MR is opened with evidence + rollback notes.
