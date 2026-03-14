# 2026-03-13 — Recurring operation languages should become explicit inside the core

## Context
After crystallizing the stable-core / thin-adapter pattern from `ontology-lsp`, the follow-up question was whether DSLs should be part of the main architecture lesson.

The answer is: yes, but as a **sub-pattern inside the stable core**, not as the top-level architecture headline.

## Evidence
- `ontology-lsp` already moved toward explicit internal languages and contracts:
  - `API_SPECIFICATION.md` defines request/response contracts between core and adapters
  - `core/analyzer.ts` and `src/core/unified-analyzer.ts` expose stable use-case verbs instead of transport-shaped calls
  - `docs/STORAGE_PORT.md` and `src/ontology/storage-port.ts` define an explicit storage contract rather than leaking persistence details upward
- The failure mode in multi-surface systems is usually not “missing HTTP” or “missing CLI”.
  It is **hidden mini-languages** spread across flags, JSON blobs, command shapes, glue scripts, and adapter-local conditionals.
- When those hidden languages remain implicit, adapters start owning semantics they should only be translating.

## Pattern
A stable core is not just shared code.
It is also the place where recurring operation languages become explicit.

Typical candidates:
- query schemas
- workflow/state contracts
- projection formats
- graph traversal/query structures
- rename / transformation plans
- governed metadata vocabularies

The right move is not “invent a DSL for everything.”
The right move is:
- keep the language implicit while it is cheap and volatile
- formalize it once repetition, failure cost, and tooling leverage justify the cost

## Guardrail
When recurring semantics are hiding in:
- flags
- loosely shaped JSON blobs
- shell command conventions
- adapter-specific request/response shapes
- copy-pasted validation logic

then evaluate whether that language should be promoted into an explicit core contract.

Use the lightest sufficient formalization first:
1. glossary / naming contract
2. schema / type definition
3. lint rule
4. executable policy / test harness
5. parser / dedicated DSL only if the language is truly rich enough to deserve it

## Propagation
- Linked from: `docs/learnings/2026-03-13-stable-core-thin-adapters-for-multi-surface-systems.md`
- TIP candidate: not yet; keep as a linked learning until we see the same threshold decision recur across more repos
