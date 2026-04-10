# AGENTS.md — fixture-org

## Intent
Template for an org/company handbook repo (consent-gated).

## Guardrails
- No secrets in git.
- Never push to `main`; MRs only.
- Treat `docs/_core/**` as immutable.

## Deterministic tooling policy (ROCS-first)
- Prefer `./scripts/rocs.sh <args...>` before ad-hoc inline scripting.
- Use `./scripts/preflight-repo-census.sh [scope]` for shallow multi-repo status checks.
- When explicit task scope is in play, author it in AK and freeze repo-consumption snapshots via `ak task scope show|export <TASK-ID> ...`; treat `governance/task-scopes/AK-<TASK-ID>.snapshot.json` as AK exports, not hand-authored truth. If a generated repo still ships `./scripts/ak.sh`, treat it as launcher implementation detail behind plain installed `ak`, not as a second AK family.
- For ontology/policy checks, use ROCS commands as the default execution path.
- Use inline Python only as an explicit escape hatch when no deterministic command exists.

## Knowledge Crystallization Flow

```
Session → diary/ (raw) → docs/learnings/ (crystallized) → TIPs (propagated)
```

**Knowledge that isn't crystallized is knowledge that will be re-learned the hard way.**

1. During operations: Capture in `diary/YYYY-MM-DD--type-scope-summary.md`
2. End of session: Extract patterns, policy implications
3. Weekly: Promote to `docs/learnings/` and `governance/`
4. When pattern generalizes: Propose meta-TIP to L0

## Recursion policy (explicit)
Allowed:
- L1 -> L2

Forbidden:
- L1 -> L0
- L2 -> L1
- any cycle

## Read order
1) `docs/_core/`
2) `docs/org/`
3) `docs/decisions/`
4) `docs/learnings/`
5) `governance/README.md`
6) `diary/`               ← recent operational sessions
7) `docs/registers/`
8) `docs/system4d/`
