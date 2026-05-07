---
summary: "Refreshed the managed launcher-bundle propagation from agent-kernel into tpl-template-repo source surfaces, regenerated fixtures, and revalidated the L0 template gate after the newer owner-side hardening drift surfaced."
read_when:
  - "Read when reconstructing the launcher-bundle propagation refresh from agent-kernel into tpl-template-repo."
type: "reference"
---

# 2026-04-09 — launcher-bundle propagation refresh

## What changed

Completed the bounded propagation refresh for `task:1053` (`[FCOS-M44-01] Refresh managed launcher-bundle template propagation after latest owner-side hardening`).

This pass:
- refreshed the template repo launcher sources from `softwareco/owned/agent-kernel` for:
  - `scripts/ak.sh`
  - `scripts/cargo-operator.sh`
  - `copier-template/scripts/*`
  - `copier-template/copier/tpl-{agent,monorepo,org,project}-repo/scripts/*`
- updated `governance/dist/managed-launcher-bundle.template-receipt.json` to the current normalized owner-side fingerprints and bundle fingerprint
- regenerated all generated fixture copies via `./scripts/sync-l0-fixtures.sh`

## Validation

Passed:

```bash
./scripts/sync-l0-fixtures.sh
bash ./scripts/check-l0.sh
```

Also rechecked normalized propagation parity against the owner-side launcher manifest after regeneration.

## Notes

- The repo already had an unrelated modified `next_session_prompt.md` before this pass; that file was left untouched.
- This pass only refreshed the launcher-bundle propagation surfaces and their generated fixture copies.
