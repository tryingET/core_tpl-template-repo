# NEXT_SESSION_PROMPT.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Active branch: `feat/l0-vouch-optional-structure-pack`
- Last merged on `main`: `77ea2bd` (contrib/vouch foundation docs)
- Working tree: **dirty** with substantial staged-eligible changes (optional vouch module + structure baseline + fixtures)
- Full validation currently passes locally:
  - `bash ./scripts/check-l0.sh` ✅

---

## What changed in this in-progress branch

### 1) Optional vouch trust-gate profile
- Added `enable_vouch_gate` to L0 `copier.yml` (default `false`).
- Added vouch baseline templates in L1 scaffold:
  - `copier-template/.github/VOUCHED.td.jinja`
  - `copier-template/.github/workflows/vouch-check-pr.yml.jinja`
  - `copier-template/.github/workflows/vouch-manage.yml.jinja`
- Added vouch baseline templates in L2 source (nested template inside L1):
  - `copier-template/copier/template-repo/.github/VOUCHED.td.j2`
  - `copier-template/copier/template-repo/.github/workflows/vouch-check-pr.yml.j2`
  - `copier-template/copier/template-repo/.github/workflows/vouch-manage.yml.j2`

### 2) Folder-structure baseline alignment (requested)
- Added baseline skeleton dirs (with `.gitkeep`) in L1 + L2 sources:
  - `docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`
- Added `.gitattributes` baseline in L1 + L2 sources.

### 3) Why some structure still differs from `~/programming/pi-extensions/template`
- AI-society L0 started intentionally minimal (contracts/recursion/idempotency first).
- We are now seeding the same **skeleton shape**, but not all feature packs yet (e.g. release/public community stack).
- This is intentional layering: baseline first, richer packs later by profile.

### 4) `.git*` file policy
- Included in generated repos: `.github/`, `.githooks/`, `.gitignore`, `.gitattributes`.
- Not included (never): `.git/` directory itself.
- Generated repos keep `.copier-answers.yml` committed.

### 5) Important templating nuance (nested Copier)
- L0 renders L1 using `.jinja` suffix.
- L1 contains a nested L2 Copier template; those files must survive templating for the second pass.
- Therefore L2 source files inside `copier-template/copier/template-repo/` now use `.j2` and nested `copier.yml` sets `_templates_suffix: .j2`.

---

## Immediate objective for next session
Finalize and ship this branch (`feat/l0-vouch-optional-structure-pack`) safely:
1. review all working tree changes,
2. commit coherent diff,
3. open PR,
4. merge after green checks.

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

---

## Commit + PR workflow (expected)
```bash
git status --short
git add .
git commit -m "feat(l0): add optional vouch profile and baseline structure skeleton"
git push -u origin feat/l0-vouch-optional-structure-pack
```

Then open PR with notes:
- optional `enable_vouch_gate` behavior,
- structure baseline rationale,
- `.j2` nested-template reason,
- validation output (`bash ./scripts/check-l0.sh`).

---

## Next after merge (follow-up backlog)
1. Add optional community pack (issue templates / CoC / support) by profile.
2. Add optional release pack (release-please/publish) by profile.
3. Add policy doc that maps `internal` vs `public` template profiles in AI-society governance.
4. Re-run adoption preview against:
   - `~/ai-society/holdingco/holdingco-templates`
   - `~/ai-society/softwareco/softwareco-templates`

---

## Constraint reminders
- Keep recursion bounded: `L0 -> L1 -> L2` only.
- No nested `copier copy` in `_tasks`.
- No destructive git actions.
- No secrets in git.
