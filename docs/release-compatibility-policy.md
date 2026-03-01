# L0 release + compatibility policy

## Purpose
Keep `tpl-template-repo` safe to evolve while existing L1 company repos (`holdingco`, `softwareco`, future org roots) remain upgradable.

## Versioning model
- **Major**: contract-breaking changes for generated L1/L2 layout or policies.
- **Minor**: backward-compatible additions (new optional files, docs, checks).
- **Patch**: bug fixes and non-contract refactors.

## Compatibility contract
A release is publishable only if:
1. `bash ./scripts/check-l0.sh` passes.
2. A generated L1 sample passes `scripts/check-template-ci.sh`.
3. L0->L1 idempotency passes.
4. Recursion policy remains bounded (`L0 -> L1 -> L2`, no reverse/cycle).

## Release checklist (manual)
1. Update docs for behavior changes.
2. Run full checks locally:
   ```bash
   bash ./scripts/check-l0.sh
   ```
3. Tag release candidate on a branch and open MR.
4. After approval, create release tag (`vX.Y.Z`).
5. Confirm intended profile bundle in `docs/profile-governance-policy.md` (internal/public + trust/release posture).
6. Run adoption preview against target L1 repos:
   ```bash
   ./scripts/preview-l1-diff.sh /path/to/holdingco
   ./scripts/preview-l1-diff.sh /path/to/softwareco
   ```
7. Roll out via branch + MR in each L1 repo.
