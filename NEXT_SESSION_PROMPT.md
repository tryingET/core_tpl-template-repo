# NEXT_SESSION_PROMPT.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Branch: `main`
- Working tree: **dirty** (policy + rollout/adoption docs changes pending commit)
- Latest local commit: `8ca9038` (`docs(session): refresh next-session handoff prompt`)
- Latest feature commit before this session: `29902b2` (`feat(l0): add organization docs profiles for template stacks`)
- Full validation passes locally:
  - `bash ./scripts/check-l0.sh` ✅

---

## What was completed in this session (currently uncommitted)

### 1) Added profile governance policy (internal vs public)
- New doc: `docs/profile-governance-policy.md`
- Defines governance meaning of toggles:
  - `l1_org_docs_profile`
  - `l2_org_docs_default`
  - `enable_community_pack`
  - `enable_release_pack`
  - `enable_vouch_gate`
- Adds recommended bundles (including explicit `internal-standard` = current L0 default posture).
- Maps profile changes to consent/change-control tiers.

### 2) Linked policy into top-level docs and release/adoption flow
Updated:
- `README.md`
- `CONTRIBUTING.md`
- `docs/l1-adoption-playbook.md`
- `docs/release-compatibility-policy.md`

Notable additions:
- docs now point to `docs/profile-governance-policy.md`
- adoption playbook now includes dirty-target handling via `git archive HEAD` snapshot compare
- release checklist now requires confirming intended profile bundle

### 3) Guardrail checks updated
- Updated `scripts/check-l0-guardrails.sh` to:
  - require `docs/profile-governance-policy.md`
  - assert README/CONTRIBUTING link policy

### 4) Adoption previews run and summarized
- Ran requested previews:
  - `./scripts/preview-l1-diff.sh ~/ai-society/holdingco/holdingco-templates`
  - `./scripts/preview-l1-diff.sh ~/ai-society/softwareco/softwareco-templates`
- Because both target repos are dirty, also ran normalized comparisons against `HEAD` snapshots.
- Added report:
  - `docs/adoption-preview-holdingco-softwareco-2026-02-11.md`

---

## Key adoption findings

Normalized (`render` vs target `HEAD` snapshot) summary:

| Target repo | A (target-only) | D (render-only) | M (overlap modified) |
|---|---:|---:|---:|
| `holdingco-templates` | 234 | 85 | 4 |
| `softwareco-templates` | 74 | 85 | 4 |

Interpretation:
- Both targets diverge structurally from current single-profile L0 `template-repo` output.
- One-shot overwrite is unsafe.
- Safe path is incremental adoption slices (policy/docs first, then scripts, then optional scaffolding).

Recommended default bundle for both target repos:
- **`internal-standard`**
  - `l1_org_docs_profile=rich`
  - `l2_org_docs_default=compact`
  - `enable_community_pack=false`
  - `enable_release_pack=false`
  - `enable_vouch_gate=false`

---

## Pending files (not yet committed)
- `CONTRIBUTING.md`
- `README.md`
- `docs/l1-adoption-playbook.md`
- `docs/release-compatibility-policy.md`
- `scripts/check-l0-guardrails.sh`
- `docs/profile-governance-policy.md` (new)
- `docs/adoption-preview-holdingco-softwareco-2026-02-11.md` (new)

---

## Immediate next objective
1. Create clean commit(s) for the pending policy/docs/guardrail/report changes.
2. Open PR with explicit note: adoption report is informational and does **not** imply direct overwrite rollout.
3. Start first adoption slice in each target L1 repo (policy/docs convergence only).

---

## Verification commands
```bash
bash ./scripts/check-l0-guardrails.sh
bash ./scripts/check-l0.sh
```

Adoption preview (baseline):
```bash
./scripts/preview-l1-diff.sh ~/ai-society/holdingco/holdingco-templates
./scripts/preview-l1-diff.sh ~/ai-society/softwareco/softwareco-templates
```

If target repos are dirty, compare against `HEAD` snapshot instead of working tree.

---

## Constraint reminders
- Keep recursion bounded: `L0 -> L1 -> L2` only.
- No nested `copier copy` in `_tasks`.
- No destructive git actions.
- No secrets in git.