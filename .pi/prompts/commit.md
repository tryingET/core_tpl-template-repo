---
description: Project-local commit workflow for FCOS sessions (model-first sync + logical commits)
---

## 0) Preflight + context snapshot (required)
Set canonical root once and keep all model/projection commands root-safe:

```bash
GK_ROOT=~/ai-society/holdingco/governance-kernel
[ -d "$GK_ROOT" ] || { echo "Missing $GK_ROOT"; exit 1; }
[ -f "$GK_ROOT/governance/fcos/fcos-work-items.json" ] || { echo "Missing FCOS canonical model"; exit 1; }
[ -f "$GK_ROOT/governance/fcos/state-machine.yaml" ] || { echo "Missing state machine authority"; exit 1; }
```

1. `git status --short`
2. if clean, stop and report no-op
3. `git diff --name-status HEAD`
4. `git log --oneline -5`
5. inspect only scoped diffs:
   - `git diff -- <files...>`
6. if this commit closes a claimed FCOS issue, inspect lease state before sync:
   - `cd "$GK_ROOT" && just fcos-context <FCOS-ISSUE-ID>`
7. derive canonical runnable head (anti-drift context):
   - `cd "$GK_ROOT" && just fcos-runnable | jq -r '.[0].id // "none"'`

## 1) Sync canonical state first (model-first)
Before creating commit(s):

1. Update `next_session_prompt.md` Session Checkpoint in this repo (mirror only; canonical model wins on conflict).
   - Keep `CURRENT PRIORITY` + `Next issue` runtime-resolved via `just fcos-runnable` (do not hardcode FCOS IDs).
   - Treat periodic anti-drift cadence as loop-owned policy (`governance/fcos/loops-registry.json` plugin `loop.fcos.drift.audit`).
2. If FCOS issue state/progress changed, update canonical state model first:
   - `$GK_ROOT/governance/fcos/fcos-work-items.json`
   - State machine authority: `$GK_ROOT/governance/fcos/state-machine.yaml`
   - Valid states: `triage | queued | doing | review | done`
   - if issue was claimed for this session, release lease only when `state=doing` or `state=review` and owner matches:
     - `cd "$GK_ROOT" && just fcos-context <FCOS-ISSUE-ID>`
     - `cd "$GK_ROOT" && just fcos-release <FCOS-ISSUE-ID> <owner> <queued|done|review>`
   - run model invariants:
     - `cd "$GK_ROOT" && just fcos-check`
   - then refresh projection:
     - `cd "$GK_ROOT" && scripts/rocs/render-fcos-issue-set.py`
3. If PRD / 10,000-ft views / holdingco README projections / loops changed, edit model files first (not projection markdown):
   - `$GK_ROOT/governance/fcos/prd-lite.json`
   - `$GK_ROOT/governance/fcos/views-10000ft.json`
   - `$GK_ROOT/governance/fcos/holdingco-readmes.json`
   - `$GK_ROOT/governance/fcos/loops-registry.json`
   - then refresh projections:
     - `cd "$GK_ROOT" && scripts/rocs/render-holdingco-projections.py`
     - `cd "$GK_ROOT" && scripts/rocs/render-loops-plugin-system.py`

Keep updates concise and factual.

## 2) Commit workflow
- Commit one repo at a time (no cross-repo mixed commit).
- Create one or more logical commits.
- Use conventional commits (`type(scope): description`).
- Commit body must include:
  - **Why**
  - **Validation**
  - **Model/Projection Sync** (if applicable)
  - **Lease/Lock Sync** (if issue claim/release was used)
- If invocation arguments include an FCOS issue id (e.g. `FCOS-M1-03`), include it in commit body.

## 3) Validation policy
- Prefer scoped checks per logical commit.
- For `core/tpl-template-repo` changes, run:
  - `bash ./scripts/check-l0.sh`
- When governance-kernel model/projection files are touched, run:
  - `cd "$GK_ROOT" && just fcos-check`
  - `cd "$GK_ROOT" && bash scripts/rocs/check-fcos-doc-drift.sh`
  - `cd "$GK_ROOT" && bash scripts/rocs/check-naming-boundaries.sh`
  - `cd "$GK_ROOT" && bash scripts/rocs/check-holdingco-model-drift.sh`
    - includes model-language conformance; run standalone check only for targeted debugging
  - when moving/operating in blocking enforcement stages:
    - `cd "$GK_ROOT" && bash scripts/rocs/check-model-language-conformance.sh`
- Run full repo validation once after final logical commit (or before push).

$ARGUMENTS
