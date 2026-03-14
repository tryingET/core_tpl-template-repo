# TIP-0010: Stable Core, Thin Adapters for Multi-Surface Systems

## Metadata

```yaml
tip: 0010
kind: meta
title: Keep multi-surface systems centered on a stable use-case core with thin adapters

provenance:
  source_agent: archaeology-pass
  source_l1: core/tpl-template-repo
  discovered: 2026-03-13
  validated_days: 0
  implemented: 2026-03-13

  upstream_evidence:
    repo: /home/tryinget/migration-from-wsl/to-sort/ontology-lsp
    docs:
      - ADAPTER_ARCHITECTURE.md
      - IMPLEMENTATION_PLAN.md
      - VISION.md
    code:
      - core/analyzer.ts
      - adapters/mcp/translator.js
      - core/services/storage.ts
      - bin/ontology-lsp

evidence:
  before:
    pattern: "Multi-interface systems tend to grow duplicate logic in CLI, tools, protocol servers, and UI layers"
    problem: "Behavior drifts across surfaces, token cost rises for agents, and every new interface becomes a partial reimplementation"
  after:
    pattern: "One stable use-case core with thin adapters for CLI/tools/frontend/RPC and ports for infrastructure"
    benefit: "Business semantics stay consistent, interfaces stay replaceable, and new surfaces cost less to add"
  sample_size: ontology-lsp architecture docs + representative implementation files
  confidence: high

changes:
  - file: docs/learnings/2026-03-13-stable-core-thin-adapters-for-multi-surface-systems.md
    kind: add
    patch: |
      Crystallize the architecture learning from ontology-lsp archaeology into the tpl-template-repo learning log.

  - file: tips/meta/tip-0010-stable-core-thin-adapters-for-multi-surface-systems.md
    kind: add
    patch: |
      Propagate the reusable rule for future AI Society repos with multiple user/agent/protocol surfaces.

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT
The stable thing in a multi-surface system is the **use-case core**, not any specific transport.
CLI, tools, frontend/TUI, LSP/MCP, HTTP/RPC, and batch automation should all be adapters over one shared semantic center.

## Rule
1. Define the core around **domain/use-case verbs**, not transport APIs.
2. Put business logic, lifecycle rules, validation, and deterministic result types in that core.
3. Keep adapters thin:
   - parse input
   - call core
   - translate/format output
   - map protocol-specific errors
4. Keep infrastructure behind ports too when multiple backends are plausible (for example storage adapters).
5. Prefer tools for common structured agent operations and CLI for operator completeness, but make both call the same core.

## Detection
Use this checklist whenever a repo wants both CLI and agent tools, or both local and remote/protocol interfaces:

- Are the same business rules being reimplemented in more than one surface?
- Does adding a new interface require copying domain logic instead of only adding translation code?
- Are storage/backend details leaking into high-level workflows instead of staying behind a port?
- Do tool and CLI outputs drift because they do not share one use-case API?

If yes, the repo likely needs a stronger stable-core / thin-adapter split.

## Residual limitations
- This pattern does not justify building every possible adapter up front.
- Start with the stable core and only add adapters that have real demand.
- A good CLI can be enough for a long time if there is only one serious interface.
