# NEXT_SESSION_PROMPT.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Branch: `main`
- Working tree: **clean**
- Latest merged commit on `main`: `9268342` (`feat(l0): add optional release automation profile pack`)
- Recent merged PRs:
  - `#2` optional vouch gate + baseline structure skeleton
  - `#3` optional community collaboration pack
  - `#4` optional release automation pack
- Full validation passes locally:
  - `bash ./scripts/check-l0.sh` ✅

---

## What is now implemented (full context)

### 1) Optional vouch trust-gate profile
- Toggle: `enable_vouch_gate` (default `false`)
- Added in L0 and nested L2 Copier configs.
- Baseline files scaffolded for L1/L2:
  - `.github/VOUCHED.td`
  - `.github/workflows/vouch-check-pr.yml`
  - `.github/workflows/vouch-manage.yml`
- Disabled-by-default behavior preserved via template tasks.

### 2) Folder-structure baseline alignment
- L1 + L2 seeded directories (`.gitkeep`):
  - `docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`
- Git baseline included:
  - `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`

### 3) Optional community collaboration pack
- Toggle: `enable_community_pack` (default `false`)
- Added in L0 and nested L2 Copier configs.
- When enabled, generated L1/L2 include:
  - `.github/ISSUE_TEMPLATE/{bug-report,feature-request,config}`
  - `.github/pull_request_template.md`
  - `CODE_OF_CONDUCT.md`
  - `SUPPORT.md`
- Disabled-by-default behavior enforced by post-copy task cleanup when false.

### 4) Optional release automation pack
- Toggle: `enable_release_pack` (default `false`)
- Added in L0 and nested L2 Copier configs.
- When enabled, generated L1/L2 include:
  - workflows: `release-please`, `release-check`, `publish`
  - files: `.release-please-config.json`, `.release-please-manifest.json`
  - docs: `CHANGELOG.md`, `SECURITY.md`
  - scripts: `scripts/release/check.sh`, `scripts/release/publish.sh`
- Disabled-by-default behavior enforced by post-copy task cleanup when false.

### 5) Nested Copier nuance (still important)
- L0 -> L1 templates use `.jinja`.
- Nested L2 template sources inside L1 use `.j2`.
- Nested `copier.yml` sets `_templates_suffix: .j2` to preserve second-pass templating.

### 6) Inheritance + checks
- L1 `scripts/new-repo-from-copier.sh` inherits all toggles to L2 unless explicitly overridden:
  - `enable_community_pack`
  - `enable_release_pack`
  - `enable_vouch_gate`
- L0 generation smoke now validates four cases:
  - baseline (`false/false/false`)
  - community (`true/false/false`)
  - release (`false/true/false`)
  - vouch (`false/false/true`)
- Fixtures refreshed and passing.

---

## Immediate objective for next session
1. Add policy doc mapping **internal vs public profile combinations** in governance terms.
2. Link that policy doc from top-level docs/readme where appropriate.
3. Run adoption previews against:
   - `~/ai-society/holdingco/holdingco-templates`
   - `~/ai-society/softwareco/softwareco-templates`
4. Summarize adoption diffs and recommend profile defaults per target repo.

---

## Verification commands (run first)
```bash
bash ./scripts/check-l0-guardrails.sh
bash ./scripts/check-l0.sh
```

If fixture drift appears:
```bash
bash ./scripts/sync-l0-fixtures.sh
bash ./scripts/check-l0.sh
```

Adoption preview:
```bash
./scripts/preview-l1-diff.sh ~/ai-society/holdingco/holdingco-templates
./scripts/preview-l1-diff.sh ~/ai-society/softwareco/softwareco-templates
```

---

## Constraint reminders
- Keep recursion bounded: `L0 -> L1 -> L2` only.
- No nested `copier copy` in `_tasks`.
- No destructive git actions.
- No secrets in git.
