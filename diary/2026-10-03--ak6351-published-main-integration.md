---
summary: "AK6351 integration of published a9d2125: combined ownership map, fixture compatibility, new clean-source full check, and scoped docs-strict limitation."
read_when:
  - "Inspecting the published-main merge and new verification evidence for AK6351."
type: "reference"
task_id: 6351
---

# AK6351 published-main integration

## Scope and commits

- Existing branch: `feat/ak6351-pinned-l0-births`; no canonical checkout edits,
  unpublished refs, AK commands, push, PR, reset, rebase, or lifecycle closeout.
- Merge `4a01f516019d5db1dd1f6b80d5ed27e86d95eede` has exactly parents
  `01d3031a19712336c498a8a4a07b31eed664c846` and published origin/main
  `a9d2125e3d004cee3cafe2f2e57459f732d58dc0`.
- Compatibility commits: `e8d7ae77cf61e1b93b0cc0b3f11aff47ee0cba62` and
  `d09eb6647e9063db6786269db69e2e477819bf0e` (the verified source).

## Conflict resolution and compatibility

Both source and L1 fixture retain company-owned `ontology/**` and agent-owned
`copier-overlay/**`. Their pristine copier-birth states bind the actual combined
map SHA256 `800b6ff37154fe68aad6106201445f7ec3a1303ecac235a85e985a3764e863d8`.
No active company lifecycle state was created or changed.

Generation and guardrails retain both owners' tests, including finite-timeout and
pinned-source tests and the published company-ownership suite. The adjacent
wrapper, checker, and owner-library auto-merges required no production rewrite.
New disposable lifecycle fixtures bind normalized provenance to the real source
pin. The historical-reader fixture uses the checker, wrapper, and wrapper helper
from the same already-published `72828ad` revision. These are isolated tests,
not old-reader preparation or adoption in any live company.

The initial focused run revealed private checkout modes: 857 tracked files had
0600/0700 instead of Git's 0644/0755. Restored tracked checkout modes, then ran
verification with umask 022 under the heavy-job runner (whose default is 077).
No placeholder safety assertion was relaxed. The first full run retained failures
for one extra guardrail blank line and the lifecycle fixture ABI/pin mismatch;
fixed those and retained the targeted failures and passing reproductions.

## Observed verification

Raw outputs, timestamps, elapsed seconds, and exit statuses are retained in
`ak6351-published-main-integration/`. During execution all evidence was written
outside the worktree at
`/home/tryinget/.local/state/pi-quests/tmp/ak6351-published-main-proof.TQeMeC`.

The actual native `bash scripts/check-l0.sh` on clean source `d09eb66` passed
**7/7**, exit **0**, in **3277.560174875951 seconds**, using
`heavy-job run --task 6351`. No timeout overrides or exclusions: base/adversarial/
fixtures 1800 seconds; generation 3600 seconds. Leaf elapsed times: guardrails
718s, generation 2130s, adversarial 338s, fixtures 92s; the three light checks 0s.
The full source proof predates this evidence-only commit; it does not claim a
full rerun of the final evidence tree. The earlier 01d3031 proof is not reused.

Docs strict (`node .../docs-list.mjs --docs . --strict`) exited **1** with one
issue: `docs/project/2026-10-02-ak6133-system4d-handoff.md` tracks live state but
has no frontmatter AK binding (`task_id` or `decision_id`). That separately-owned
handoff remains unchanged; this is a disclosed limitation, not a green docs check.

Production birth timeout 3600s, source pinning, sandbox, descriptors, and process
safety are unchanged. No AK6352/6353 execution, copier retirement, overlay engine,
company adoption, wave release, or publication occurred. The four accepted
obsolete project outputs remain an exception: no exact birth-parity or fleet
claim is made. Parent retains publication and lifecycle authority.
