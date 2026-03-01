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
2. `[[docs/l1-adoption-playbook.md]]` (L1 update flow)
3. `[[docs/l2-transition-playbook.md]]` (L2 migration flow)
4. `[[copier-template/docs/dev/tpl-project-repo-file-contract.md]]` (detailed project-template contract)

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
- Migrate an **existing L2** to template baseline → [Section 6](#6-transition-an-existing-l2-repo)

---

## 3) Create a new L1 company template repo (L0 -> L1)

Run from `core/tpl-template-repo`:

```bash
./scripts/new-l1-from-copier.sh /absolute/path/to/<company>-templates \
  -d repo_slug=<company>-templates \
  -d company_slug=<company> \
  -d company_name="<Company Name>" \
  -d l1_org_docs_profile=rich \
  -d l2_org_docs_default=compact \
  -d enable_community_pack=false \
  -d enable_release_pack=false \
  -d enable_vouch_gate=false \
  --defaults --overwrite
```

Validate in generated L1:

```bash
cd /absolute/path/to/<company>-templates
bash ./scripts/check-template-ci.sh
```

---

## 4) Create a new L2 repo (L1 -> L2)

Run from your `<company>-templates` repository:

```bash
# project
./scripts/new-repo-from-copier.sh tpl-project-repo /path/to/<repo> \
  -d repo_slug=<repo> --defaults --overwrite

# agent
./scripts/new-repo-from-copier.sh tpl-agent-repo /path/to/agent-<slug> \
  -d repo_slug=agent-<slug> --defaults --overwrite

# org
./scripts/new-repo-from-copier.sh tpl-org-repo /path/to/<org>-handbook \
  -d repo_slug=<org>-handbook --defaults --overwrite

# monorepo
./scripts/new-repo-from-copier.sh tpl-monorepo /path/to/<monorepo> \
  -d repo_slug=<monorepo> -d language=python -d package_manager=uv \
  --defaults --overwrite

# package (inside monorepo)
./scripts/new-repo-from-copier.sh tpl-package /path/to/packages/<name> \
  -d package_name=<name> -d package_type=library -d language=python \
  --defaults --overwrite
```

---

## 5) Transition an existing L1 template repo

Authoritative playbook:
- `[[docs/l1-adoption-playbook.md]]`

Minimum deterministic flow:

```bash
# from core/tpl-template-repo
./scripts/preview-l1-diff.sh /absolute/path/to/<company>-templates
```

Then in target L1 repo (on branch):
- apply selected changes
- run `bash ./scripts/check-template-ci.sh`
- open MR with recursion/contract notes

---

## 6) Transition an existing L2 repo

Authoritative playbook:
- `[[docs/l2-transition-playbook.md]]`

Important: there is currently **no in-place auto-migrator**. Use scaffold-first migration.

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
