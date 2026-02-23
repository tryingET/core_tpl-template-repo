# softwareco Analysis

**Date:** 2026-02-21
**Status:** DO NOT REFACTOR — analysis only

## Architecture: Registry Pattern

softwareco is architecturally different from holdingco/healthco.

| Aspect | holdingco/healthco | softwareco |
|--------|-------------------|------------|
| L1 structure | Embedded `copier/tpl-*-repo/` | NO embedded templates |
| Template location | Inside L1 | Separate L2 repos |
| Resolution | Local copier | Registry lookup |

### L2 Registry

```
L1: softwareco-templates/
    └── docs/l2-registry.md (resolution table)

L2 Templates (separate repos):
    ├── tpl-agent-repo/    (git remote: softwareco/tpl-agent-repo)
    ├── tpl-org-repo/      (git remote: softwareco/tpl-org-repo)
    ├── tpl-owned-repo/    (git remote: softwareco/tpl-owned-repo)
    ├── tpl-contrib-repo/  (git remote: softwareco/tpl-contrib-repo)
    └── tpl-infra-repo/    (git remote: softwareco/tpl-infra-repo)
```

### Lane Policy Matrix

| Lane | Template | Merge Policy | CI | Release | Governance |
|------|----------|--------------|----|---------|------------|
| `owned` | tpl-owned-repo | MR required | smoke+full | allowed | high |
| `contrib` | tpl-contrib-repo | MR, lighter | smoke+full | off | light |
| `agent` | tpl-agent-repo | proposal+MR | smoke+full | no | medium |
| `infra` | tpl-infra-repo | MR+change control | strict | controlled | high |

## Template Overlap Analysis

| Template | In L0? | Sync Strategy |
|----------|--------|---------------|
| `tpl-agent-repo` | ✅ Yes | Could sync from L0 |
| `tpl-org-repo` | ✅ Yes | Could sync from L0 |
| `tpl-owned-repo` | ❌ No | Domain-specific, stays local |
| `tpl-contrib-repo` | ❌ No | Domain-specific, stays local |
| `tpl-infra-repo` | ❌ No | Domain-specific, stays local |

## KES Integration Path

**DO NOT** transition softwareco-templates to L0-generated. The registry pattern is intentional.

### Recommended Approach

1. **Keep registry pattern** — it serves the multi-lane architecture
2. **Sync overlapping templates** — tpl-agent-repo, tpl-org-repo can pull from L0
3. **Domain TIPs stay local** — owned/contrib/infra learnings don't escalate
4. **Meta TIPs escalate** — improvements to agent/org templates flow to L0

### TIP Escalation Matrix

| TIP Kind | Scope | Escalates to L0? |
|----------|-------|------------------|
| `domain` (owned/contrib/infra) | softwareco only | No |
| `domain` (agent/org) | cross-cutting | Yes |
| `meta` | system-wide | Yes |
| `infrastructure` | build/CI | Yes |

## Open Questions

1. Should softwareco adopt the TIPs pattern for its domain templates?
2. How do we handle sync when L0 and softwareco tpl-agent-repo diverge?
3. Is there value in a unified "agent template" that both reference?

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-21 | Do not refactor softwareco-templates | Registry pattern is intentional |
| 2026-02-21 | Analyze before touching | Different species requires different approach |

## Next Steps

1. ✅ Document analysis (this file)
2. ⏳ Present to user for direction on sync strategy
3. ⏳ If approved, establish sync path for overlapping templates
4. ⏳ Consider TIPs infrastructure for domain-specific learnings
