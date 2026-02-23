# AGENTS.md — fixture-product-repo

## Intent
Template for a delivery project repo (project context + code + tests).

## Guardrails
- No secrets in git.
- Never push to `main`; MRs only.
- Treat `docs/_core/**` as immutable.

## Knowledge Crystallization Flow

```
Session → docs/diary/ (raw) → docs/learnings/ (crystallized) → TIPs (propagated)
```

**Knowledge that isn't crystallized is knowledge that will be re-learned the hard way.**

1. During work: Capture in `docs/diary/YYYY-MM-DD.md`
2. End of session: Extract patterns, decisions, learnings
3. Weekly: Promote to `docs/learnings/` and `docs/decisions/`
4. When pattern generalizes: Propose TIP

## Recursion policy (explicit)
Allowed:
- L1 -> L2

Forbidden:
- L1 -> L0
- L2 -> L1
- any cycle

## Read order
1) `docs/_core/`
2) `docs/org_context/`
3) `docs/project/`
4) `docs/decisions/`
5) `docs/learnings/`
6) `docs/diary/`          ← recent work sessions
7) `docs/system4d/`
