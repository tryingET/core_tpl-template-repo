# Migration: `agent/1` to `agent/2`

1. **Inspect:** read schema-1 manifest, persona sources/projection, repository ownership, appointment evidence, provider resources, and current registry behavior. Do not modify files.
2. **Plan:** assign an owner-approved UUID and appointment ref; derive jurisdiction home; resolve exact provider-qualified resources; render schema 2 to scratch; generate a classified diff; verify no agent-owned path is overwritten.
3. **Explicit apply:** only the agent owner, after upstream contracts and Gate transition, applies reviewed changes. Gate A must leave `apply: false`.
4. **Validate:** schema, canonical vectors, persona projection equality, complete skill tree/invocation policy, parent-child Git separation, strict runtime compatibility.
5. **Rollback:** restore schema-1 selection and compatibility path; disable strict mode; retain evidence and the rejected plan. Never erase persona/history to roll back.

Unknown or ambiguous ownership halts planning. No bulk Copier rerender is allowed for existing agent repositories.
