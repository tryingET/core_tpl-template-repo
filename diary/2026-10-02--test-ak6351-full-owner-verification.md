---
summary: "AK6351 full owner check passes on committed finite defaults; exact measurements, exceptions and coverage limits."
read_when:
  - "Inspecting the final AK6351 owner verification before lifecycle or rollout decisions."
type: reference
---

# AK6351 — full owner verification

Continued only the owned `feat/ak6351-pinned-l0-births` branch. Parent retains the
claim and AK lifecycle authority. No AK writes, canonical/company mutations,
push, merge, PR, branch/worktree deletion, catalog retirement, overlays, AK6352/3
or rollout. Existing tests' isolated fixture transitions are not live mutations.

## Accepted boundaries

Operator evidence 12202, as identified by dispatch, accepts the four obsolete
project-only omissions: `.gitlab-ci.yml`, `gitlab/ci/rocs.yml`,
`governance/work-items.cue`, `governance/work-items.json` (and absent GitLab dirs).
This is a birth-parity exception, **not exact equivalence**. The original delta
JSON remains byte-identical with `acceptance_satisfied=false`. Fleet and original
company-index equivalence remain unproved. The eight prior Markdown metadata
repairs are preserved; no document exclusions or test waivers were introduced.

## Repairs and calibration

Started from parent repair `c14e232`: raw YAML parent bytes retain explicit tags;
safe parsing, digests and drift checks remain. Restored three existing contracts:

- `chmod a-x` makes the generation test's non-executable fixtures independent of
  the private runner umask. No production permission policy changed.
- The divergent-company ownership test materializes normalized answer/seal pins
  in its runtime copies using actual L0 HEAD. Golden fixture meaning is unchanged.
- Company entrypoints pass their own physical root (`pwd -P`), restoring alias
  invocation/rerun compatibility. Explicit source/destination no-follow checks,
  descriptor binds and lineage protections are unchanged. Real alias/rerun and
  explicit source-symlink refusal tests both passed (2 tests, 14.008s).

Successful finite lane measurements (7200s cap, 30s temporary kill escalation):

| Leaf | Actual elapsed seconds | Measurement source | Committed default seconds |
|---|---:|---|---:|
| Guardrails | 778.654000745 | 64b63ba | 1800 |
| Generation | 1653.568129274 | 0ee107f | 3600 |
| Adversarial | 367.709930772 | edf06ba | 1800 |
| Fixtures | 93 (final owner report) | 40d2d05 | 1800 |

Base defaults are 1800s; generation is 3600s. Explicit base overrides retain
historical generation doubling, and per-lane overrides still take precedence.
Four new budget regression tests run in the generation leaf, covering finite
numeric defaults, overrides, invalid input and fail/abort on actual timeout.
No checks were removed. Production birth/execution 3600s, process-group teardown,
sandbox and lineage remain unchanged. Single-host timing is not an SLA.

Failed attempts are preserved in `diary/ak6351-verification-final/`:
chmod failure (972.007055839s), normalized fixture-pin failure (1518.704002402s),
alias failure (365.092593417s), and the first full owner guardrail timeout at
1200s. A later guard calibration failed because this agent left untracked prior
measurement JSON/exit evidence in the source; the clean-source check correctly
refused it. Committed that evidence and reran cleanly rather than weakening the
check. Initial 1200s calibration was insufficient; successful full-leaf timing
and the failed cap informed the final 1800s default. Historical stopped proofs
remain historical, not rewritten green.

## Actual full owner command and result

Started with clean branch at `40d2d05f5bd997b54785e051e3875aaa0a1ea61a`, after
committing revised defaults, test/source fixes and prior evidence:

```bash
heavy-job run --label ak6351-full-owner-recalibrated-defaults-$(date +%s) \
  --task 6351 -- python3 -B diary/ak6351-verification-final/measure.py \
  diary/ak6351-verification-final/full-owner.json \
  env -u L0_CHECK_TIMEOUT_SECONDS -u L0_CHECK_TIMEOUT_GENERATION_SECONDS \
  -u L0_CHECK_TIMEOUT_ADVERSARIAL_SECONDS -u L0_CHECK_TIMEOUT_FIXTURES_SECONDS \
  L0_CHECK_VERBOSE=1 bash scripts/check-l0.sh
```

**Exit 0; 7 passed / 0 failed / 0 skipped; 2893.039813572s total.**
Reported leaf wall times: guardrails 830s, doc references 0s, session checkpoint
0s, supply chain 0s, generation 1628s, adversarial 342s, fixtures 93s. Guardrails
ran 96 + 4 tests and shell checks; generation ran its 21-test behavior selection
and all generation smoke coverage. Fixture equality passed without broad sync.
The aggregate was run once to successful completion with committed defaults;
focused proofs and synthetic timeout tests are not substitutes for this result.

Verbose mode preserves leaf output but does not count warnings; zero aggregate
warning counters do **not** establish warning-free execution. Logs retain re-init
warnings, pathspec deprecations, optional UBS-helper-unavailable diagnostics and
the heavy runner's protected-process inspection warning. Heavy-job reports
success and owned scratch removed. Only owned verification process teardown is
claimed, not absence of unrelated workstation processes.

## Final evidence and limits

`diary/ak6351-verification-final/summary.json` records actual timings/config and
accepted boundaries; raw logs and monotonic measurement JSON retain command argv,
UTC start/end and exit status. Final docs strict, residual/source fixture identity,
line budgets, canonical checkout observation and owned-process checks are retained
there too. The final evidence-only commit does not modify verified code.

Full owner verification and repo docs strict pass. No unresolved bounded-owner
check blocker remains. This does not authorize fleet propagation, publication,
exact-equivalence acceptance, or AK completion. Parent must inspect before any
lifecycle action.

Canonical checkout observation at handoff: clean `49e34ac4556cd9a708b878233f40c3e530d0381e`
on `feat/ak6328-company-ontology-ownership`, not the earlier c14/main checkout.
It changed concurrently outside this slice; this agent issued no canonical
mutation or reset. The full owner proof binds the owned branch's 40d2d05 code,
not that concurrent branch. No claim is made that canonical main remained c14.

Touched non-artifact paths in this resumed continuation: `CONTRIBUTING.md`,
`scripts/check-l0.sh`, `scripts/check-l0-generation.sh`,
`copier-template/scripts/new-repo-from-copier.sh`, its L1 fixture counterpart,
`tests/test_company_ontology_ref_inheritance.py`,
`tests/test_l1_template_ownership.py`, `tests/test_l0_check_timeouts.py`, this
final diary and `diary/ak6351-verification-final/` evidence. Parent c14e232 raw
snapshot code and the eight prior metadata repairs were not rewritten.
