# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start work immediately.
Do not ask for permission to begin.

## CURRENT MISSION: TEMPLATE ARCHITECTURE REFORM

We are reforming the template hierarchy to fix a broken chain and enable clean company-specific template derivation.

### Problem Discovered

1. **Missing L0 parameter**: `core/tpl-template-repo/copier.yml` has no `company_slug` parameter
2. **Hardcoded paths**: Company-specific paths (e.g., `holdingco/governance-kernel`) were manually hardcoded in L1 templates instead of templated
3. **Broken chain**: `softwareco/tpl-*-repo/` templates have no `.copier-answers.yml` - they're manual orphans
4. **Redundant archetype**: `tpl-individual-repo` is just `tpl-project-repo` with single maintainer - unnecessary
5. **Confused dimensions**: "flavors" (owned/contrib/infra) conflated with "structure" (single/monorepo/package)

### Target Architecture

```
L0: core/tpl-template-repo/
    └── copier/
        ├── tpl-agent-repo/      # AI agents
        ├── tpl-org-repo/        # Organization handbooks
        ├── tpl-project-repo/    # Single-project repos
        ├── tpl-monorepo/        # Monorepo repos (has packages/ apps/)
        └── tpl-package/         # Package inside monorepo (no .git)

L1: {company}/{company}-templates/
    └── copier/  (same 5 templates, company paths baked in)

L2: {company}/{archetype}/{name}/
    └── Generated from L1 templates

L3: (only inside monorepos)
    {company}/owned/{monorepo}/packages/{name}/
    {company}/owned/{monorepo}/apps/{name}/
```

### 5 Templates (Clear Purpose)

| Template | Generates | Has .git | Use Case |
|----------|-----------|----------|----------|
| `tpl-agent-repo` | AI agent repo | ✅ | `agents/agent-triage/` |
| `tpl-org-repo` | Org handbook | ✅ | `holdingco/org-handbook/` |
| `tpl-project-repo` | Single-project repo | ✅ | `owned/agent-kernel/`, `infra/workstation/` |
| `tpl-monorepo` | Monorepo workspace | ✅ | `owned/dspx/` |
| `tpl-package` | Package inside monorepo | ❌ | `owned/dspx/packages/dspx-core/` |

### Key Parameters

```yaml
# L0 copier.yml
company_slug:
  type: str
  help: "Company slug (e.g., holdingco, softwareco, healthco)"

company_name:
  type: str
  help: "Company display name (e.g., Holding Company)"

# tpl-project-repo/copier.yml
location:
  default: owned
  choices: [owned, contrib, infra]
language:
  default: python
  choices: [python, node, typescript, rust, go, bash]
enable_software_pack:
  default: false

# tpl-monorepo/copier.yml (NO language - deferred to packages)
package_manager:
  choices: [uv, npm, pnpm, cargo, go-mod]

# tpl-package/copier.yml
package_type:
  choices: [library, app, service]
language:
  choices: [python, node, typescript, rust, go]
```

### Usage Examples

```bash
# L0 → L1: Generate company templates
./scripts/new-l1-from-copier.sh ~/ai-society/softwareco/softwareco-templates \
  -d company_slug=softwareco \
  -d company_name="Software Company" \
  -d repo_slug=softwareco-templates \
  --defaults --overwrite

# L1 → L2: Create single-project repo
copier tpl-project-repo softwareco/infra/workstation/ \
  -d repo_slug=workstation \
  -d language=bash

# L1 → L2: Create monorepo
copier tpl-monorepo softwareco/owned/dspx/ \
  -d repo_slug=dspx \
  -d language=python \
  -d package_manager=uv

# L1 → L3: Add package to monorepo
copier tpl-package softwareco/owned/dspx/packages/dspx-auth/ \
  -d package_name=dspx-auth \
  -d package_type=library \
  -d language=python
```

---

## WORK PACKAGES (IN ORDER)

### WP1: Add company_slug to L0
- [x] Add `company_slug` and `company_name` parameters to `core/tpl-template-repo/copier.yml`
- [x] Create `{{ company_slug }}` variable for use in templates
- [x] Update README with new parameter documentation

### WP2: Template all company-specific paths
- [x] Audit all hardcoded company paths in L0 templates
- [x] Replace with `{{ company_slug }}` variables
- [x] Key files updated:
  - `copier-template/{{ _copier_conf.answers_file }}.jinja` - Added company fields
  - `copier-template/copier/tpl-project-repo/copier.yml` - Added company params
  - `copier-template/copier/tpl-org-repo/copier.yml` - Added company params
  - `copier-template/copier/tpl-agent-repo/copier.yml` - Added company params
  - `copier-template/copier/*/docs/_core/README.md.j2` - Templated paths
  - `copier-template/scripts/new-repo-from-copier.sh` - Inherit company params
  - `copier-template/governance/README.md.jinja` - Templated example path

### WP3: Eliminate tpl-individual-repo
- [x] Delete `core/tpl-template-repo/copier-template/copier/tpl-individual-repo/`
- [x] Remove references from L0 copier.yml `_tasks` and `_message_after_copy`
- [x] Update fixtures and tests
- [x] Document that "individual" is just `tpl-project-repo` with single maintainer

### WP4: Add tpl-monorepo archetype
- [x] Create `copier-template/copier/tpl-monorepo/` based on `tpl-project-repo`
- [x] Add monorepo-specific structure: `packages/`, `apps/`, workspace config
- [x] Add `package_manager` and `language` parameters
- [x] Update L0 copier.yml to include in archetype list
- [x] Update guardrails and scripts to include tpl-monorepo

### WP5: Add tpl-package archetype
- [x] Create `copier-template/copier/tpl-package/`
- [x] NO `.git`, NO `.github`, NO release tooling
- [x] Has `package_type` parameter: library, app, service
- [x] Has `language` parameter: python, node, typescript, rust, go
- [x] Minimal structure: `src/`, `tests/`, `docs/`, `scripts/ci/`
- [x] Update guardrails and scripts to include tpl-package

### WP6: Regenerate holdingco-templates
- [x] Run L0 → L1 with `company_slug=holdingco`
- [x] Verify `.copier-answers.yml` has company_slug
- [x] Verify paths are templated (not hardcoded)
- [x] Run validation checks

### WP7: Create softwareco-templates (proper L1)
- [x] Run L0 → L1 with `company_slug=softwareco`
- [x] Move content from orphan `softwareco/tpl-*-repo/` into `softwareco-templates/copier/`
- [x] Delete orphan template folders
- [x] Verify chain: L0 → L1 (softwareco-templates) → L2

### WP8: Regenerate healthco-templates
- [x] Run L0 → L1 with `company_slug=healthco`
- [x] Verify alignment with new architecture

### WP6.5: L2 Validation (holdingco)
- [x] Greenfield: `holdingco/infra/template-test-bed/` from tpl-project-repo
- [x] Brownfield: `holdingco/org-handbook/` migration from tpl-org-repo

### WP9: Instantiate workstation backup repo
- [x] Create `softwareco/infra/workstation/` from `tpl-project-repo`
- [x] Move backup documentation from `softwareco/infra/infra-workstation-backup/` *(legacy path not present; baseline captured in new repo docs)*
- [x] Add progressive backup plan (6 stages)
- [x] Connect to DS1621 backup target *(connection scripts + env contract added)*

### WP10: Migrate pi-extensions to monorepo *(superseded in this workspace)*
- [x] Superseded: migration performed on Steve environment; not tracked/continued from this repository session

---

## READ-FIRST ALLOWLIST (ONLY THESE, HARD)

1. This file (you're reading it)
2. `copier.yml` - L0 parameter definitions
3. `copier-template/` - Template source files
4. `fixtures/l1/template-repo/` - Expected L1 output
5. `scripts/new-l1-from-copier.sh` - L0 → L1 generation script

Do not read company-specific repos unless blocked and documented.

---

## EXECUTION MODE

1. **Pick next incomplete work package** from the list above
2. **Read only what's needed** from allowlist
3. **Implement end-to-end** for that work package
4. **Validate** with `./scripts/check-l0-guardrails.sh` and `./scripts/check-l0-generation.sh`
5. **Commit** with clear WP reference in message
6. **Update this file** to mark WP complete

---

## VALIDATION GATES

After each work package:

```bash
# L0 guardrails
./scripts/check-l0-guardrails.sh

# L0 generation (sample)
./scripts/check-l0-generation.sh

# Template CI
./scripts/check-template-ci.sh
```

---

## NAMING CONVENTIONS (FINAL)

### Archetypes (what template generates)
- `agent` → AI agent repo
- `org` → Organization handbook
- `project` → Single-project repo
- `monorepo` → Workspace with packages/apps
- `package` → Library/app inside monorepo

### NOT archetypes (just folder locations)
- `owned/` → Company-owned projects
- `contrib/` → Upstream contributions
- `infra/` → Infrastructure
- `agents/` → AI agents

### Dimensions (separate concerns)
- **Location**: `owned/`, `contrib/`, `infra/` — where you instantiate
- **Structure**: `project`, `monorepo`, `package` — what's inside
- **Language**: `python`, `node`, `rust`, `go` — tooling

---

## SESSION CHECKPOINT (UPDATE BEFORE /commit)

- Work package executed this session:
  - **WP9-REPO-INSTANTIATION**: created `softwareco/infra/workstation/` from `softwareco-templates` `tpl-project-repo` (`location=infra`, `language=bash`).
  - **WP9-BACKUP-PLAN**: added `docs/project/backup_plan.md` with a 6-stage progressive rollout.
  - **WP9-DS1621-CONNECTION**: added `scripts/backup/check-ds1621.sh` and `scripts/backup/restic-workstation-backup.sh` with non-secret env contract.
  - **WP9-PROJECT-CONTEXT**: updated `README.md`, `docs/dev/status.md`, `docs/dev/next_steps.md`, and project purpose/mission/goals for backup scope.
- Outcome:
  - New workstation repo initialized and committed at `softwareco/infra/workstation`.
  - Root commit: `8261ba6` (`WP9: scaffold workstation repo with DS1621 backup plan and scripts`).
  - WP10 marked superseded for this workspace (moved to Steve environment).
- Current priority:
  - Continue ring1 deterministic-gate enforcement in governance-kernel (FCOS queue head).
- Blockers/risks:
  - Legacy source path `softwareco/infra/infra-workstation-backup/` not present in this workspace snapshot.
  - Live DS1621 connectivity requires local credentials/env setup (intentionally not committed).
- Validation run:
  - `cd ~/ai-society/softwareco/infra/workstation && sh -n scripts/backup/check-ds1621.sh scripts/backup/restic-workstation-backup.sh`
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md` to revert session state
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/` if recurrent patterns
  - Propagate meta patterns to `tips/meta/`

---

## END-OF-SESSION

Run `/commit` (project-local template: `.pi/prompts/commit.md`).
