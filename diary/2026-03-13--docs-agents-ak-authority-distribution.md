---
summary: "Session note: 2026 03 13 Docs Agents Ak Authority Distribution."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 13 docs agents ak authority distribution."
type: "reference"
---

# 2026-03-13 — AGENTS distribution for AK authority model

## What I Did
- Verified AGENTS loader behavior from `softwareco/contrib/pi-mono/packages/coding-agent/src/core/resource-loader.ts`:
  - global `~/.pi/agent/AGENTS.md` first
  - then ancestor `AGENTS.md` / `CLAUDE.md` from filesystem root down to cwd
  - concatenated as markdown sections with no special precedence tags
- Updated workspace `~/ai-society/AGENTS.md` with a concise universal invariant:
  - Agent Kernel is authoritative for repo-local task/issue/work-item state
  - checked-in artifacts like `governance/work-items.json` are deterministic projections/mirrors
  - do not manually treat projections as authoritative
  - prefer repo-local deterministic wrappers when present
  - CI must not silently skip AK/projection drift validation
- Updated this repo's `AGENTS.md` so L0 maintenance explicitly preserves AK-first generated repo behavior and avoids silent drift-check skips.

## Why This Matters
- Because parent AGENTS files are concatenated into descendant sessions, the AK authority model now distributes from the workspace level as ambient policy.
- Concrete commands and template-specific workflow still remain in repo/template surfaces, which keeps the parent AGENTS concise while making the universal rule explicit.

## Validation
- Loader source read successfully.
- No code-path changes in this follow-up slice; no additional repo validation commands were necessary.

## Crystallization Candidates
- Parent AGENTS files should carry universal authority models.
- Repo/template AGENTS should carry executable local workflow details.
