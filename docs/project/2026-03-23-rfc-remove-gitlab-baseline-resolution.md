---
summary: "Decision note to remove template-shipped GitLab baseline-resolution paths from ROCS CLI and drive repo-local removal through AK tasks."
read_when:
  - "When coordinating removal of rocs_cli.gitlab baseline-resolution support across template lineage and live repos"
---

# RFC: Remove GitLab baseline-resolution from template-shipped ROCS CLI

## Why

AI Society is explicitly transitioning away from GitLab as an operational forge dependency.
Template-shipped ROCS CLI still carries `rocs_cli.gitlab` fetch and baseline-resolution paths, which keeps GitLab behavior alive in generated repos even when the target architecture is forge-agnostic.

Recent hardening made the still-shipped GitLab path safer, but that does not answer the strategic question of whether the path should continue to exist.
The answer for this RFC is: remove it unless a repo makes an explicit local decision to retain a justified compatibility layer.

## Decision

1. `core/tpl-template-repo` should remove template-shipped GitLab baseline-resolution support from `tpl-project-repo` ROCS CLI.
2. L1 template repos should remove the embedded template surface after L0 lands.
3. Live repos that still ship `tools/rocs-cli/src/rocs_cli/gitlab.py` should remove or replace that path through repo-local work tracked in Agent Kernel.
4. Stronger downstream variants should not be blindly flattened; each owning repo must decide whether to delete, replace, or explicitly retain with rationale.

## Scope

- `core/tpl-template-repo`
- L1 template repos: `holdingco`, `softwareco`, `healthco`, `teachingco`
- Live repos still shipping `tools/rocs-cli/src/rocs_cli/gitlab.py`

## Non-goals

- keeping GitLab support by inertia
- blind cross-repo propagation without repo-local authority
- treating transitional hardening as the final architecture

## Validation

- L0: `PATH=/usr/bin:/bin bash ./scripts/check-l0.sh`
- L1: `bash ./scripts/check-template-ci.sh`
- L2: repo-local smoke/full gates plus any ROCS CLI tests covering baseline resolution or layer loading

## Exit criteria

- template lineage no longer generates GitLab baseline-resolution by default
- repo-local AK tasks exist for every live owning repo still carrying the surface
- remaining GitLab support, if any, is explicitly justified rather than implicit inheritance
