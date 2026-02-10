# L1 adoption playbook (from L0)

## Goal
Adopt L0 updates into existing L1 repos with minimal drift and explicit review.

## Preconditions
- L0 checks pass: `bash ./scripts/check-l0.sh`
- Target L1 repo has a clean working tree.
- Changes flow via branch + MR (no direct push to `main`).

## Preview diff (non-destructive)
```bash
./scripts/preview-l1-diff.sh /absolute/path/to/holdingco-templates
./scripts/preview-l1-diff.sh /absolute/path/to/softwareco-templates
```

## Adoption flow
1. Create branch in target L1 repo.
2. Render fresh L1 output from L0 into a temp dir.
3. Apply selected changes into target repo.
4. Run in target repo:
   ```bash
   bash ./scripts/check-template-ci.sh
   ```
5. Open MR with recursion + contract notes.

## Drift controls
- Keep `contracts/layer-contract.yml` untouched unless intentionally changing policy.
- Keep generated `.copier-answers.yml` committed.
- Never add nested Copier runs in template `_tasks`.
