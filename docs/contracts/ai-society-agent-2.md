# `ai-society.agent/2` contract

## Purpose and complexity removed

Schema 2 removes path-as-identity, bare provider names, persona placement ambiguity, and unsafe whole-template migration. It does not create authority, a registry, or a runtime state machine.

## Required semantics

- stable UUID `agent_id`, unique across jurisdictions;
- explicit society/company jurisdiction and accountable appointment reference;
- home derived from appointing jurisdiction: society `~/ai-society/agents/agent-*`, company `~/ai-society/<company>/agents/agent-*`;
- repository path is a locator and never authority;
- provider-qualified exact prompt, profile, and complete skill-tree references;
- persona authored sources separated from generated projection and actual delivery placement;
- exact runtime ceiling for tools, extensions, ambient resources, and fresh/resumed session;
- schema-1 compatibility and inspect → plan → explicit owner apply migration;
- no broad Copier overwrite of agent-owned files.

## Ownership

Template-owned shape/scaffolding may be refreshed through reviewable propagation. Agent-owned manifest values, persona, diary, learnings, decisions, and activities are never overwritten by template propagation. Company parents own only lane baseline files and ignore standalone child repositories.

## Compatibility and rollback

Readers continue to accept schema 1. Schema 2 is non-default during Gate A. Migration renders to scratch, validates, compares generated persona, classifies every diff, and requires explicit apply. Rollback restores schema-1 selection and strict-mode feature flag without deleting schema-2 evidence.

## Acceptance scenarios

The two same-local-name fixtures validate because UUID, jurisdiction, appointment, and home differ. The duplicate UUID fixture fails. The parent/child ownership fixture proves no dual Git ownership. No live fleet default or agent migration changes in Gate A.
