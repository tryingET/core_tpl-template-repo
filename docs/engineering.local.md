---
summary: "Repository-local engineering-core v0.6 adoption posture and authority boundary."
read_when:
  - "Before planning, advising, or validating engineering work in this repository."
type: "reference"
---

# Local engineering guidance

## Upstream

- Source: `core/engineering-core`
- Release pin: `v0.7.0`
- Policy: `policy/engineering-lane.json`

## Selected guidance

- No language lane is selected; this repository currently adopts cross-language disciplines only.
- Disciplines: `validation`, `security-privacy`, `documentation`

## Declared capabilities

- `planning`, `advisor`
- `closed_loop` is not declared under v0.6.

These declarations authorize deterministic static observation only. They do not prove command execution, model use, CI compliance, release readiness, or verified runtime evidence. Repository and AK owner surfaces retain those facts.

## Validation posture

Use the repository's existing owner-declared validation commands. This adoption adds no hard CI gate and executes no consumer-declared command.
