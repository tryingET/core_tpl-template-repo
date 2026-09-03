# Provider-qualified resource reference v1

A strict reference is `{provider, kind, name, revision, content_digest}` with optional canonical tree digest, invocation policy, logical identity, and physical locator. Provider/name/revision identify who publishes what; digests identify exact bytes/trees. Physical paths are materialization locators, not portable identity or authority. Imports set `authority_transfer: false`.

Strict resolution forbids bare-name precedence, ambient fallback, mutable `latest`, and model-selected provider or revision. A resolved release contains complete artifacts before Pi runs; Pi does not perform hidden skill inheritance. Invocation policy, including disabled model invocation, is part of identity and survives materialization.
