---
summary: "Session note: 2026 03 13 Docs Global Agents Intent Over Wording."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 13 docs global agents intent over wording."
type: "reference"
---

# 2026-03-13 — Add intent-over-wording rule to global AGENTS

## What I Did
- Updated `~/.pi/agent/AGENTS.md` with a durable interpretation rule for operator input.
- Added guidance to prioritize operator intent over exact wording when likely meaning is recoverable from context.
- Made the rule explicit that the operator may use English as a second language, so minor phrasing or terminology mismatch should not force unnecessary clarification.

## Why
- This is a cross-session operator/agent contract, so the right home is the global AGENTS layer rather than a repo-local doc.
- It helps preserve the real instruction when wording is slightly off, especially in architectural discussions where the operator's meaning matters more than perfect phrasing.

## Validation
- Re-read `~/.pi/agent/AGENTS.md` after the edit.

## Crystallization Candidates
- This likely stays as a global AGENTS rule rather than becoming a tpl-template-repo TIP, because it is about operator interpretation at the parent context layer.
