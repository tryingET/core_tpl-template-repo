# softwareco Analysis (archived)

**Date:** 2026-02-21  
**Status:** Superseded

This document captured an older exploration that assumed a registry-based `softwareco-templates` model with lane-specific templates (`tpl-owned-repo`, `tpl-contrib-repo`, `tpl-infra-repo`).

That model is no longer authoritative.

## Current authority
- `docs/dev/README.md`
- `docs/l1-adoption-playbook.md`
- `docs/l2-transition-playbook.md`
- `diary/2026-03-01--refactor-l1-structure-checklist.md`

## Canonical direction
- L1 is the **company root repo** (`~/ai-society/<company>`), not `<company>-templates`.
- L2 templates are embedded under `copier/`.
- No `tpl-owned-repo` / `tpl-contrib-repo` / `tpl-infra-repo` archetypes in the canonical L0 surface.
- Lane placement is achieved via path + `location` parameter when using `tpl-project-repo`.
