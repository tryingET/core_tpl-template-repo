## Summary
- What changed and why?

## L0 validation checklist
- [ ] `bash ./scripts/check-l0-guardrails.sh`
- [ ] `bash ./scripts/check-l0-generation.sh`
- [ ] No nested Copier runs added in `_tasks`
- [ ] Recursion contract still enforces: `L0 -> L1 -> L2` only
- [ ] `.copier-answers.yml` policy remains explicit in layer contracts

## Risk + rollout
- Risk level: Low / Medium / High
- Rollout plan:
- Rollback plan:
