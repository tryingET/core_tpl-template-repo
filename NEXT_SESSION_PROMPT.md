# NEXT_SESSION_PROMPT.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Branch: `feat/l2-archetype-cutover-clean`
- Working tree: **dirty** (provenance seal + guardrails + test output refactor pending commit)
- Base: `main` at `de0bf23` (`feat(l0): add profile governance policy and adoption guidance (#5)`)
- Validation: **passes** (`bash ./scripts/check-l0.sh`)

---

## What was completed in this session (currently uncommitted)

### 1) Archetype transition isolated into clean branch
- Original work on `feat/l2-archetype-cutover` had mixed scope (archetype + docs-list + session handoff docs).
- Safety snapshot created:
  - Stash: `stash@{0}` — all dirty tracked + untracked files from original branch
  - Backup branch: `backup/feat-l2-archetype-cutover-20260219-144455`
- New clean branch `feat/l2-archetype-cutover-clean` created from `main`.
- Cherry-picked archetype commit `4ea0bfb` excluding unrelated files:
  - excluded: `next_session_prompt.md`, `docs/comparability-matrix-workspace-copier-vs-l0-l2-2026-02-11.md`

### 2) L2 provenance seal implemented
- Added `template_source_sha` parameter to L2 copier config (`copier-template/copier/template-repo/copier.yml`).
- Added provenance template: `copier-template/copier/template-repo/contracts/provenance-seal.yml.j2`.
- Updated L2 smoke check (`scripts/ci/smoke.sh`) to verify:
  - `contracts/provenance-seal.yml` exists
  - schema declares `ai-society.template-provenance.v1`
  - archetype matches
  - `__RENDER_HASH__` placeholder is resolved
- Updated L2 answers template to persist `template_source_sha`.
- Updated L1 wrapper (`copier-template/scripts/new-repo-from-copier.sh`) to auto-inject `template_source_sha` from git HEAD.

### 3) Hard guardrails against legacy template trees
- Added `assert_absent` helper to `scripts/check-l0-guardrails.sh`.
- Added loop to detect legacy/unsupported template profiles under `copier-template/copier/*` (only `template-repo` allowed).
- Added `assert_absent` checks for rendered contract files in template tree.
- Mirrored guardrails in `copier-template/scripts/check-template-ci.sh` for L1 self-check.

### 4) Test output refactored for conciseness
- Rewrote `scripts/check-l0.sh` to:
  - capture output per check
  - show only warnings (deduplicated) and errors
  - display final overview summary (passed/failed/warnings + per-check status)
  - support opt-in verbose mode via `L0_CHECK_VERBOSE=1`

### 5) Fixtures synchronized
- Re-ran `scripts/sync-l0-fixtures.sh` to include provenance seal changes.
- Updated fixtures now include:
  - `fixtures/l1/template-repo/copier/template-repo/contracts/provenance-seal.yml.j2`
  - `fixtures/l2/template-repo/contracts/provenance-seal.yml`

---

## Pending files (not yet committed)
Modified:
- `copier-template/copier/template-repo/copier.yml`
- `copier-template/copier/template-repo/{{ _copier_conf.answers_file }}.j2`
- `copier-template/copier/template-repo/scripts/ci/smoke.sh`
- `copier-template/scripts/new-repo-from-copier.sh`
- `copier-template/scripts/check-template-ci.sh`
- `scripts/check-l0-guardrails.sh`
- `scripts/check-l0.sh`
- `fixtures/l1/template-repo/copier/template-repo/copier.yml`
- `fixtures/l1/template-repo/copier/template-repo/.copier-answers.yml.j2`
- `fixtures/l1/template-repo/copier/template-repo/scripts/ci/smoke.sh`
- `fixtures/l1/template-repo/scripts/new-repo-from-copier.sh`
- `fixtures/l1/template-repo/scripts/check-template-ci.sh`
- `fixtures/l2/template-repo/.copier-answers.yml`
- `fixtures/l2/template-repo/scripts/ci/smoke.sh`

New:
- `copier-template/copier/template-repo/contracts/provenance-seal.yml.j2`
- `fixtures/l1/template-repo/copier/template-repo/contracts/provenance-seal.yml.j2`
- `fixtures/l2/template-repo/contracts/provenance-seal.yml`

---

## Immediate next objective
1. Commit current changes on `feat/l2-archetype-cutover-clean` as:
   - `feat(l2): add provenance seal and hard legacy guardrails`
2. Push branch and open PR against `main`.
3. Optionally restore stashed work to `feat/l2-archetype-cutover` for separate docs-list.sh feature.

---

## Verification commands
```bash
# concise output (default)
bash ./scripts/check-l0.sh

# verbose output if needed
L0_CHECK_VERBOSE=1 bash ./scripts/check-l0.sh
```

---

## Safety/recovery references
- Stash: `stash@{0}` (from `feat/l2-archetype-cutover`)
- Backup branch: `backup/feat-l2-archetype-cutover-20260219-144455`
- Original feature branch: `feat/l2-archetype-cutover` (at `4ea0bfb`)

To restore stashed work:
```bash
git switch feat/l2-archetype-cutover
git stash pop stash@{0}
```

---

## Constraint reminders
- Keep recursion bounded: `L0 -> L1 -> L2` only.
- No nested `copier copy` in `_tasks`.
- No direct commits to `main`; use topic branches + PRs.
- No destructive git actions unless explicitly requested.
- No secrets in git.
