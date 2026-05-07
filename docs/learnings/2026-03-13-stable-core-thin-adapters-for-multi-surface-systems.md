---
summary: "2026-03-13 — Stable core + thin adapters is the durable multi-surface pattern."
read_when:
  - "Read when you need 2026-03-13 — stable core + thin adapters is the durable multi-surface pattern."
type: "reference"
---

# 2026-03-13 — Stable core + thin adapters is the durable multi-surface pattern

## Context
A follow-up architecture discussion asked whether systems like Prompt Vault / AK / similar repos should expose CLI, agent tools, frontend, RPC, and other interfaces as separate surfaces over one stable core. To avoid inventing the answer from scratch, I did an archaeology pass over the earlier `ontology-lsp` work at:

- `/home/tryinget/migration-from-wsl/to-sort/ontology-lsp/ADAPTER_ARCHITECTURE.md`
- `/home/tryinget/migration-from-wsl/to-sort/ontology-lsp/IMPLEMENTATION_PLAN.md`
- `/home/tryinget/migration-from-wsl/to-sort/ontology-lsp/VISION.md`
- `/home/tryinget/migration-from-wsl/to-sort/ontology-lsp/core/analyzer.ts`
- `/home/tryinget/migration-from-wsl/to-sort/ontology-lsp/adapters/mcp/translator.js`
- `/home/tryinget/migration-from-wsl/to-sort/ontology-lsp/core/services/storage.ts`

## Evidence
- `ADAPTER_ARCHITECTURE.md` explicitly names the winning shape as a **unified core architecture with thin protocol adapters** for LSP, MCP, HTTP, and CLI.
- `IMPLEMENTATION_PLAN.md` separates a **protocol-agnostic core** from `adapters/` and treats the adapter layer as translation, not business logic.
- `core/analyzer.ts` is a concrete example of a **use-case API core**: `findDefinition`, `findReferences`, `getHover`, `getRenameEdits`, `learnPattern`, `provideFeedback`, etc.
- `adapters/mcp/translator.js` shows what adapters should do: convert transport-shaped requests and responses, not implement analysis semantics.
- `bin/ontology-lsp` is only a thin executable entrypoint into the built CLI surface.
- `VISION.md` and the storage code make the persistence lesson explicit too: put storage behind a **port/adapter boundary** rather than leaking DB details upward.

## Pattern
When a system needs multiple interfaces, the durable architecture is:

1. **stable use-case core first**
   - the core owns business semantics, validation, lifecycle rules, and deterministic result shapes
2. **thin adapters second**
   - CLI, tools, frontend/TUI, LSP/MCP, HTTP/RPC translate into the core and back out again
3. **ports for infrastructure**
   - persistence and similar dependencies should also sit behind stable ports, not bleed into higher layers

The key insight is that the stable thing is not “HTTP” or “CLI” or “RPC”.
The stable thing is the **use-case API**.
Transport and presentation are replaceable.

## Guardrail
For future multi-surface repos in AI Society:
- do not duplicate business logic across CLI, tools, frontend, RPC, or protocol servers
- define the core around domain verbs/use cases first
- keep each adapter responsible only for parsing, translation, formatting, and protocol-specific error handling
- prefer tools for common structured agent operations and CLI for operator completeness, but make both call the same core
- put storage/integration dependencies behind ports when multiple backends or environments are plausible

## Propagation
- Propagated: `tips/meta/tip-0010-stable-core-thin-adapters-for-multi-surface-systems.md`

## Related learning
- DSL/formalization sub-pattern: `docs/learnings/2026-03-13-recurring-operation-languages-should-become-explicit.md`
