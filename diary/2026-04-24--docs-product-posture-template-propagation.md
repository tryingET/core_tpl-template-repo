---
summary: "Session note: 2026 04 24 Docs Product Posture Template Propagation."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 04 24 docs product posture template propagation."
type: "reference"
---

# 2026-04-24 — Product posture template propagation

## What I Did
- Added `docs/project/product_posture.md` to the `tpl-project-repo` authoring template as a generic product-wide maturity posture bridge.
- Updated `docs/project/model.md` for the template, L1 fixture, L2 fixture, and project language matrix fixtures to describe product posture without making it runtime authority.
- Updated the tpl-project-repo file contract in the L0 source and L1 fixture copy to list `product_posture.md` in the project docs surface.
- Kept existing unrelated launcher/wrapper/task-scope dirty work untouched.

## What Surprised Me
- The repo already had broad unrelated dirty work, including launcher-wrapper simplification changes and fixture updates. Full fixture validation would have mixed this slice with that existing work.

## Patterns
- Product posture belongs between durable vision and active direction: status-bearing, but not live execution authority.
- `current-vs-target` is useful as a section/pattern inside product posture and as a seam-specific boundary concept, not as the product-wide filename.

## Crystallization Candidates
- Consider documenting the product posture pattern in a reusable learning only after one or two more repos adopt it successfully.
