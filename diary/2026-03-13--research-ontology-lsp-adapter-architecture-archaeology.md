---
summary: "Session note: 2026 03 13 Research Ontology Lsp Adapter Architecture Archaeology."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 13 research ontology lsp adapter architecture archaeology."
type: "reference"
---

# 2026-03-13 — Ontology-LSP adapter architecture archaeology

## What I Did
- Performed an archaeology pass over `/home/tryinget/migration-from-wsl/to-sort/ontology-lsp` to extract reusable architecture learnings.
- Read the high-signal architecture docs:
  - `ADAPTER_ARCHITECTURE.md`
  - `IMPLEMENTATION_PLAN.md`
  - `VISION.md`
  - `README.md`
- Inspected representative code surfaces:
  - `core/analyzer.ts`
  - `adapters/mcp/translator.js`
  - `core/services/storage.ts`
  - `bin/ontology-lsp`
- Compared the recovered pattern to the current discussion about CLI vs tools vs frontend/RPC adapters.

## What Surprised Me
- The repo states the pattern very explicitly: protocol-agnostic core first, thin protocol adapters second.
- The stronger reusable insight was not just “thin adapters”, but also “stable use-case API in the core” plus “storage behind a port”.
- The migration snapshot still contains both aspirational docs and concrete implementation evidence, which made it usable for archaeology even though it is not in the active workspace tree.

## Patterns
- Multi-surface systems get saner when business/use-case semantics live in one core and every interface is an adapter.
- CLI, LSP, MCP, HTTP, and future frontend/RPC surfaces should translate inputs/outputs, not reimplement domain logic.
- Persistence should also be adapterized behind a port so higher layers do not learn storage-specific assumptions.

## Crystallization Candidates
- → `docs/learnings/2026-03-13-stable-core-thin-adapters-for-multi-surface-systems.md`
- → `tips/meta/tip-0010-stable-core-thin-adapters-for-multi-surface-systems.md`
