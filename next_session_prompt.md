# next_session_prompt.md

## SESSION TRIGGER (AUTO-START)
Reading this file is authorization to start immediately.
Do not ask for permission to begin.

## CURRENT MISSION: HOLDINGCO ROOT TRANSITION (BACKUP-FIRST)

Target company root:
- `~/ai-society/holdingco`

Transition goal:
- Move from legacy `holdingco/holdingco-templates`-centric layout to company-root L1 layout.
- Preserve nested child repos.
- Apply lane-root baseline + lane `.gitignore` policy (the same pattern proven in recent lane bootstrap work).

---

## HARD PRECONDITION (NON-NEGOTIABLE): CREATE BACKUP FIRST

There is currently no dedicated backup for this transition run.
Create one before any migration/swap steps.

### Required backup set

```bash
ts="$(date +%Y%m%d-%H%M%S)"
backup_root="$HOME/ai-society/bak/${ts}-holdingco-pre-transition"
mkdir -p "$backup_root"

# full snapshot
rsync -a "$HOME/ai-society/holdingco/" "$backup_root/holdingco-full/"

# explicit lane snapshots (if lanes exist)
for lane in owned contrib infra agents; do
  if [ -d "$HOME/ai-society/holdingco/$lane" ]; then
    rsync -a "$HOME/ai-society/holdingco/$lane/" "$backup_root/${lane}-pre/"
  fi
done

# git HEAD manifest for all repos under holdingco
find "$HOME/ai-society/holdingco" -type d -name .git | while read -r gitdir; do
  repo="${gitdir%/.git}"
  head="$(git -C "$repo" rev-parse --short=12 HEAD 2>/dev/null || echo NO-HEAD)"
  printf '%s %s\n' "$head" "$repo"
done | sort > "$backup_root/pre-transition-git-heads.txt"
```

### Required backup verification
- Backup root exists and is non-empty.
- `holdingco-full/` exists and is non-empty.
- `pre-transition-git-heads.txt` exists and is non-empty.
- Record `backup_root` in session checkpoint and migration notes.

If any check fails: stop.

---

## EXECUTION PLAN (AFTER BACKUP)

From `~/ai-society/core/tpl-template-repo`:

1. Preflight
   - `git status --short`
   - `bash ./scripts/check-l0.sh`

2. Run staged transition helper
   - `./scripts/migrate-l1-structure.sh holdingco "Holding Company"`

3. Validate stage
   - `cd ~/ai-society/holdingco-stage`
   - `git status --short`
   - `bash ./scripts/check-template-ci.sh`

4. Swap (manual + explicit, only after stage is green)
   - `mv ~/ai-society/holdingco ~/ai-society/holdingco-old-<ts>`
   - `mv ~/ai-society/holdingco-stage ~/ai-society/holdingco`

5. In new `~/ai-society/holdingco` parent repo
   - commit parent-lane bootstrap baseline first
   - then initialize lane-root git repos:
     - `./scripts/bootstrap-lane-root.sh owned --init-lane-git`
     - `./scripts/bootstrap-lane-root.sh contrib --init-lane-git`
     - `./scripts/bootstrap-lane-root.sh infra --init-lane-git`
     - `./scripts/bootstrap-lane-root.sh agents --init-lane-git`

6. Verify lane behavior
   - lane roots track baseline files
   - nested child repos remain ignored by lane `.gitignore`
   - no embedded-repo warnings during normal parent staging (`git add -n .`)

---

## VALIDATION GATES

- In `core/tpl-template-repo`:
  - `bash ./scripts/check-l0.sh`
- In staged/new `holdingco`:
  - `bash ./scripts/check-template-ci.sh`
- Post-swap lane smoke:
  - `git -C owned status --ignored --short` (if lane exists)
  - `git -C contrib status --ignored --short` (if lane exists)
  - `git -C infra status --ignored --short` (if lane exists)
  - `git -C agents status --ignored --short` (if lane exists)

---

## SESSION CHECKPOINT (UPDATE BEFORE /commit)

- Backup root:
  - `/home/tryinget/ai-society/bak/20260302-062823-holdingco-pre-transition`
- Backup verification results:
  - backup root exists + non-empty: ✅
  - `holdingco-full/` exists + non-empty: ✅
  - `pre-transition-git-heads.txt` exists + non-empty: ✅
- Work package executed this session:
  - Holdingco transition (backup-first) via staged migration helper
- Outcome:
  - ✅ Completed end-to-end transition and swap to company-root L1 layout.
  - ✅ New root at `~/ai-society/holdingco`; prior root moved to `/home/tryinget/ai-society/holdingco-old-20260302-062932`.
  - ✅ Parent baseline committed on branch `chore/holdingco-l1-root-transition` (`c4e8109`).
  - ✅ Lane roots (`owned`, `contrib`, `infra`, `agents`) initialized with lane-local git + ignore policy.
  - ✅ Parent staging smoke clean (`git add -n .` -> no embedded-repo warnings).
- Current priority (runtime-resolved):
  - Continue governance-kernel deterministic queue flow; keep this file mirror-only.
- Next issue (runtime-resolved):
  - Primary command: `cd ~/ai-society/holdingco/governance-kernel && just fcos-runnable`
  - Resolver command (fallback): `cd ~/ai-society/holdingco/governance-kernel && python3 scripts/rocs/fcos-scheduler.py runnable | jq -r '.[0].id // "none"'`
  - Resolved at checkpoint update time: `FCOS-M4-02`.
- Anti-drift cadence policy:
  - Loop-owned by `governance/fcos/loops-registry.json` plugin `loop.fcos.drift.audit`.
- Blockers/risks:
  - Missing backup verification must block swap (satisfied this run).
- Validation run:
  - `bash ./scripts/check-l0.sh` (pass)
  - `bash ~/ai-society/holdingco/scripts/check-template-ci.sh` (pass)
  - `git -C ~/ai-society/holdingco/{owned,contrib,infra,agents} status --ignored --short` (lane smoke pass)
- Rollback path (mirror-only correction):
  - `git restore -- next_session_prompt.md`
- KES crystallization flow:
  - Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
  - Crystallize to `docs/learnings/`
  - Propagate meta patterns to `tips/meta/`

---

## END-OF-SESSION
Run `/commit` (project-local template: `.pi/prompts/commit.md`).
