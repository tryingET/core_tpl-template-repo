# L1 Restructure Checklist: `<company>-templates/` → `<company>/`

**Goal:** Make the company folder THE git repo, with templates living inside it. AGENTS.md and scripts at company level work for all projects via pi's upward traversal.

---

## Phase 1: L0 Template Changes

### 1.1 Update L1 copier template structure
- [x] Rename `copier-template/` → stays as-is (this IS the L1 template source)
- [x] Verify L1 template creates company-root structure, not `<company>-templates/`

### 1.2 Update `copier.yml` (L0 root)
- [x] Change `repo_slug` default from `<company>-templates` to `{{ company_slug }}`
- [x] Update `_message_after_copy` with new structure

### 1.3 Update `copier-template/.gitignore`
- [x] Add `owned/` to gitignore (each project has own .git)
- [x] Add `contrib/` to gitignore
- [x] Add `infra/` to gitignore
- [x] Add `agents/` to gitignore
- [x] Keep `copier/` tracked (templates are part of company repo)
- [x] Keep `scripts/` tracked
- [x] Keep `AGENTS.md` tracked

### 1.4 Update `copier-template/AGENTS.md.jinja`
- [x] Rename AGENTS.md → AGENTS.md.jinja
- [x] Add "Shared tooling" section referencing `./scripts/rocs.sh`, `./scripts/docs-list.sh`
- [x] Update paths to be relative to company root
- [x] Add note about working in `owned/`, `contrib/`, `infra/` subfolders
- [x] Use {{ company_slug }}, {{ company_name }} template variables

### 1.5 Update `scripts/new-l1-from-copier.sh`
- [x] Change destination path hint from `<company>-templates` to `<company>`
- [x] Update usage examples in script

### 1.6 Update `docs/dev/README.md`
- [x] Change all `~/ai-society/<company>/<company>-templates` → `~/ai-society/<company>/`
- [x] Update L1 creation examples
- [x] Update L2 creation examples with owned/, agents/ paths
- [x] Add L1 structure diagram

### 1.7 Update fixtures
- [x] Regenerate fixtures via `scripts/sync-l0-fixtures.sh`

---

## Phase 1 Status: ✅ COMPLETE

---

## Phase 2: L2 Template Changes (inside copier/)

### 2.1 Verify L2 templates live at `copier/tpl-*/`
- [x] Confirm `copier-template/copier/tpl-project-repo/` structure (unchanged)
- [x] Confirm `copier-template/copier/tpl-agent-repo/` structure (unchanged)
- [x] Confirm `copier-template/copier/tpl-org-repo/` structure (unchanged)
- [x] Confirm `copier-template/copier/tpl-monorepo/` structure (unchanged)
- [x] Confirm `copier-template/copier/tpl-package/` structure (unchanged)

### 2.2 Remove orphan template
- [x] Verify `tpl-owned-repo` does NOT exist in L0 `copier-template/copier/` (confirmed: not there)

### 2.3 Update L2 AGENTS.md.j2 templates
- [x] `tpl-project-repo/AGENTS.md.j2` - already references `./scripts/rocs.sh`
- [x] `tpl-agent-repo/AGENTS.md.j2` - already references `./scripts/rocs.sh`
- [x] `tpl-org-repo/AGENTS.md.j2` - already references `./scripts/rocs.sh`
- [x] `tpl-monorepo/AGENTS.md.j2` - already references `./scripts/rocs.sh`
- [x] `tpl-package/AGENTS.md.j2` - already references `../../scripts/rocs.sh`

### 2.4 Add docs-list.sh to L2 templates
- [ ] DECISION NEEDED: propagate to L2 OR keep at company level only?
  - Current: docs-list.sh only at company level (L1)
  - L2 projects use company's docs-list.sh via upward traversal
  - Recommendation: keep at company level only (simpler, less duplication)

---

## Phase 3: Migrate Existing L1 Companies

**Companies to migrate:**
- softwareco (has AGENTS.md + softwareco-templates/)
- healthco (has healthco-templates/)
- holdingco (has holdingco-templates/)

### 3.0 Pre-flight
- [x] Create migration script: `scripts/migrate-l1-structure.sh`

### 3.1 Migrate softwareco
- [ ] Run: `./scripts/migrate-l1-structure.sh softwareco "Software Company"`
- [ ] Verify git history preserved
- [ ] Run: `bash ./scripts/check-template-ci.sh`
- [ ] Swap folders

### 3.2 Migrate healthco
- [ ] Run: `./scripts/migrate-l1-structure.sh healthco "Health Company"`
- [ ] Verify git history preserved
- [ ] Run: `bash ./scripts/check-template-ci.sh`
- [ ] Swap folders

### 3.3 Migrate holdingco
- [ ] Run: `./scripts/migrate-l1-structure.sh holdingco "Holding Company"`
- [ ] Verify git history preserved
- [ ] Run: `bash ./scripts/check-template-ci.sh`
- [ ] Swap folders
- [ ] Check for any uncommitted changes in company folder

### 3.1 Backup current state
- [ ] `cd ~/ai-society/softwareco && git status` - note any uncommitted
- [ ] `cd ~/ai-society/healthco && git status` - note any uncommitted  
- [ ] `cd ~/ai-society/holdingco && git status` - note any uncommitted
- [ ] Record current branch names for each

### 3.2 Create migration script (reusable for all companies)
- [ ] Create `scripts/migrate-l1-structure.sh` that:
  - Takes company name as argument
  - Creates temp folder with new structure
  - Copies git history, copier/, scripts/, .copier-answers.yml
  - Moves owned/, contrib/, infra/, agents/
  - Swaps folders

### 3.3 Migrate softwareco
- [ ] Run migration script for softwareco
- [ ] Move existing `softwareco/AGENTS.md` to new structure
- [ ] Verify git history preserved

### 3.4 Migrate healthco
- [ ] Run migration script for healthco
- [ ] Verify git history preserved

### 3.5 Migrate holdingco
- [ ] Run migration script for holdingco
- [ ] Verify git history preserved

### 3.6 Remove tpl-owned-repo from all migrated L1s
- [ ] `rm -rf ~/ai-society/softwareco/copier/tpl-owned-repo` (if exists)
- [ ] `rm -rf ~/ai-society/healthco/copier/tpl-owned-repo` (if exists)
- [ ] `rm -rf ~/ai-society/holdingco/copier/tpl-owned-repo` (if exists)

### 3.7 Cleanup
- [ ] Remove `*-old/` folders after verification
- [ ] Remove `*-templates/` folders after verification

---

## Phase 4: Update /tpl Prompt

### 4.1 Fix paths
- [ ] Change `~/ai-society/<company>/<company>-templates` → `~/ai-society/<company>/`
- [ ] Update L1 creation example
- [ ] Update L2 creation example (run from `~/ai-society/<company>/`)

### 4.2 Add template selection guidance
- [ ] Add "Which template?" section with matrix:
  | Template | Use When | Key Features |
  |----------|----------|--------------|
  | tpl-project-repo | Full project with governance | governance/, ontology/, docs/project/ |
  | tpl-agent-repo | Agent/AI repos | Agent-specific structure |
  | tpl-org-repo | Org handbooks | Documentation focus |
  | tpl-monorepo | Multi-package | packages/ structure |
  | tpl-package | Inside monorepo | Language-specific |

### 4.3 Add transition workflow
- [ ] Add section for migrating existing repos (scaffold-first)
- [ ] Add warning about NEVER copying files manually

### 4.4 Add critical rules
- [ ] ALWAYS use copier - enables future template updates
- [ ] NEVER copy files manually - breaks provenance
- [ ] `.copier-answers.yml` MUST be committed

### 4.5 Update docs reference
- [ ] Point to `~/ai-society/<company>/docs/dev/README.md` (company-level)

---

## Phase 5: Update Workspace-Level Files

### 5.1 Update `~/ai-society/AGENTS.md`
- [ ] Update any paths referencing `<company>-templates`
- [ ] Verify cognitive tools section is still correct

### 5.2 Update `~/ai-society/.gitignore`
- [ ] Already ignores `softwareco/` - verify this is still correct
- [ ] Each company folder is its own git repo

---

## Phase 6: Validation

### 6.1 L0 validation
- [ ] Run `bash ./scripts/check-l0.sh`
- [ ] Run `bash ./scripts/check-l0-generation.sh`
- [ ] Run `bash ./scripts/check-l0-fixtures.sh`

### 6.2 L1 validation (all migrated companies)
- [ ] softwareco: `cd ~/ai-society/softwareco && bash ./scripts/check-template-ci.sh`
- [ ] healthco: `cd ~/ai-society/healthco && bash ./scripts/check-template-ci.sh`
- [ ] holdingco: `cd ~/ai-society/holdingco && bash ./scripts/check-template-ci.sh`

### 6.3 L2 validation (existing projects)
- [ ] `cd ~/ai-society/softwareco/owned/typREPL && bash ./scripts/ci/smoke.sh`
- [ ] Verify pi loads correct AGENTS.md chain for softwareco projects

### 6.4 Template creation test (for each company)
- [ ] softwareco: Create test L2 project, verify `.copier-answers.yml`, verify `scripts/rocs.sh`
- [ ] healthco: Create test L2 project
- [ ] holdingco: Create test L2 project

---

## Phase 7: Documentation Updates

### 7.1 Update L0 docs
- [ ] `docs/dev/README.md` - main entrypoint
- [ ] `docs/l1-adoption-playbook.md` - L1 update flow
- [ ] `docs/l2-transition-playbook.md` - L2 migration flow

### 7.2 Update any cross-references
- [ ] Search for `<company>-templates` in all docs
- [ ] Update to new structure

---

## Rollback Plan

If migration fails:
```bash
# Restore old structure
mv ~/ai-society/softwareco ~/ai-society/softwareco-broken
mv ~/ai-society/softwareco-old ~/ai-society/softwareco
```

---

## Notes

- **Why this is better:**
  1. `softwareco/AGENTS.md` is versioned, not orphan
  2. `./scripts/rocs.sh` works from ANY project under softwareco/
  3. No weird `-templates` suffix - just `copier/` folder inside company
  4. pi chain: `typREPL/AGENTS.md` → `softwareco/AGENTS.md` → `ai-society/AGENTS.md`
  5. One git repo per company, not one for templates + orphan AGENTS.md

- **What stays the same:**
  - L0 structure (tpl-template-repo)
  - L2 project structure (generated from templates)
  - The copier mechanism itself
