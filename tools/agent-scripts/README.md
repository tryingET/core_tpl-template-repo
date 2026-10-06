---
summary: "Minimal pinned docs-ref-check owner runtime for credential-free L0 CI."
read_when:
  - "Updating or inspecting the L0 hosted documentation-check dependency."
type: "reference"
---

# Pinned documentation checker

This is the minimal runtime import closure of `docs-ref-check` from
`https://github.com/tryingET/agent-scripts` at commit
`81fa62b9fcf312a9939f8b4e8f6270951f1dfab0`. The executable and six imported modules
are copied byte-for-byte from that Git object, not locally reimplemented.
`source-pin.json` records their SHA-256 hashes; `tests/test_hosted_ci.py` checks them
and exercises passing tracked references and missing-reference refusal.

The operator explicitly authorized publishing this bounded subset from the private
owner repository in this public PR on 2026-10-03. It needs Node >=18.2.0 and Git;
no npm packages, credentials, workspace checkout, or private database are needed.

Agent-scripts remains the implementation owner. Changes must originate there;
update the commit, exact runtime import closure, hashes, and pin test together.
This bundle is L0-only and is not propagated into company or product templates.
