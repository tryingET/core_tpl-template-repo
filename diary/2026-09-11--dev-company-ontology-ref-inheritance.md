---
summary: "Task5658 candidate: optional company ontology inheritance and source-level nested answer filename transport."
read_when:
  - "Reviewing task5658 inheritance, answers filename transport, or validation evidence."
type: "reference"
---

# 2026-09-11 — Company ontology ref inheritance (candidate for parent review)

## What I Did
- Worked in a new no-hardlinks isolated clone of source commit
  `84d6c81e0b1146940ded9bf1bf6ede222acf67f8`; did not modify the canonical checkout.
- Added the optional empty-default L0 question and conditional L1 answer persistence.
- Added project/monorepo/package-only selection of CLI > nonempty stored child >
  nonempty L1 > existing archetype defaults. No nested defaults were changed.
- Extracted cohesive answer handling into a scoped helper. Wrapper is 491 lines
  (was 523); guardrails remain 951 lines, with the new tests in their existing invocation.
- Used `scripts/new-l1-from-copier.sh` with Copier 9.11.1 and `HEAD` to render the
  L1 fixture into owned scratch, then applied owner normalization. Changes are
  limited to the scoped wrapper/helper, structural validator, and five nested
  answer-template filenames.
- After the parent amended scope, escaped each nested answer filename with an
  outer Jinja raw block. The inner expression prepends a relative dot/separator
  so Copier 9.11.1 does not reduce a directory-qualified answer path to its basename.
  All five template bodies are byte-identical to the base; this is filename transport,
  not new agent/org inheritance policy.
- Added L0 and original-three wrapper input validation: double quotes, backslashes,
  and nonprintable characters are rejected before rendering because the unchanged
  project manifest emits a double-quoted YAML scalar. Single quotes and shell-active
  printable characters remain literal data.

## Observed Validation
- Initial candidate `a4a8921fc3a8e6435c356f29af00ba108791090a` failed custom-answer
  output tests. Implementation stopped, then resumed only after the parent amended
  scope (task entity version 4; parent-reported failure evidence9187).
- The subsequent focused suite passed all 12 tests in 187.607s. It retains the
  original failing custom-directory assertions and adds all-five default/custom
  output and rerun tests, including an outer L0 custom filename, duplicate-output
  absence, input-boundary rejection, and byte-identical fixture/body checks.
- Final clean-candidate focused/full gate exits and canonical-byte comparison are
  recorded externally under the task scratch directory, not claimed in this note
  before execution. A final assertion extension also checks custom-path reruns
  after an explicit empty answer falls back to a nonempty L1 selection.

## Scope-v5 Validator Follow-up
- Candidate `3fdef0a3133bd3b5cdb91d878fe5383cd9276089` passed its 12 focused tests
  but only 5/7 full-gate checks. Generation and adversarial checks failed because
  the generated structural validator still required the old answer filename.
- Resumed after reading task entity version 5, which authorizes the source and
  fixture `scripts/check-template-ci.sh` paths (parent-reported evidence9188).
- Changed only the two filename references in each validator. Both file-presence
  and canonical YAML-emission assertions remain in the existing all-five loop.
  No compatibility duplicate, template-body edit, or policy/default change was added.
- Regenerated L1 using the owner wrapper and normalization. Only the authorized
  validator differed from the existing fixture; copied that rendered file, then
  verified source/fixture byte equality. Renderer exit: 0.
- Focused suite after this correction: 12 tests passed, exit 0, 192.498s. Logs:
  `focused-scope5.log` and `render-fixture-scope5.log` in the original task scratch.
- The ensuing full gate runs from a clean isolated candidate. Its actual exit and
  output are captured in `check-l0-scope5.exit` and `check-l0-scope5.log`; this diary
  does not pre-assert a pass. Final preservation evidence is compared against the
  original `canonical-before.json`, never a replacement baseline.

## Scope-v6 Existing-L1 Correction
- Independent review found that the prior 12-test/7-check pass did not prove
  existing-L1 upgrades. Parent-reported evidence9201 binds that noGO and the scope-v6
  resolution; this continuation keeps the original clone and preservation baseline.
- The actual owner refresh now forwards `company_ontology_ref` explicitly, using
  strict YAML/string parsing so malformed input cannot silently become an empty default.
- A shared stdlib transition helper pins the five historical bodies to the original
  base. Retirement requires prior/incoming template ownership, tracked/committed
  approved bytes, safe ancestors, no nested repositories/symlinks/hardlinks, and Git
  regular-file mode 100644. Safe worktree permissions 0600/0640/0644 accommodate umask;
  executable or writable-by-others modes are rejected. Serialized plans cannot replace
  the fixed fingerprints or successor paths.
- Owner refresh preflights all five and revalidates before writes and before any
  retirement. Only the exact approved obsolete paths are exceptions to target-only
  preservation. Explicit bootstrap may attest these paths but never deletes them;
  an existing adoption without their attestations still fails closed. Normal pending
  receipt, finalization, adoption-drift, and v2 provenance protections are unchanged.
- The copy wrapper preflights copier-birth v1 state before rendering. It refuses
  receipt-backed, adopting, pending, and v2 targets; companies should use owner-aware
  refresh. Bare `copier copy` is not certified for existing-L1 upgrades.
- Successful wrapper upgrades retire verified predecessors, then invoke the owner
  renderer again so the provenance seal excludes obsolete files. Interrupted copying
  is not an atomic transaction: unrelated copy writes can be partial; failed first
  rendering does not trigger retirement, and interrupted resealing is repairable by
  rerun. No post-copy-only cleanup is represented as prewrite protection.
- Pre-final focused execution passed 20 tests in 297.481s: real base-render-to-candidate
  upgrades through both interfaces, all-five single default/custom output, original-three
  post-upgrade precedence, actual refresh selected/empty/missing preservation, explicit
  adoption, modified/unsafe inputs, dry run, failed render, stale plan, and late drift.
- New render tests run in pinned Copier 9.11.1 Python with strict synthetic AK fixtures,
  not installed AK or live task5105. Safety tests remain in the 300s guardrail lane;
  the real upgrade matrix runs through the existing ownership tests in the 600s
  generation lane. Neither timeout nor a production authority resolver was weakened.
- Full-gate iteration caught an existing diagnostic-order contract: unsupported
  legacy multiline answers must fail before the stdlib-Python requirement, while
  valid legacy answers must reach that requirement before the new optional parser.
  Both cases now have a hermetic regression; the original assertions were retained.
- A global full-gate AK_CMD test override masked the gate's own scoped fixtures.
  Later runs use a PATH-level strict synthetic legacy fixture, permitting each gate
  to install its own stricter test double; no production resolver was changed.
- Final clean-candidate focused/full exits and original-baseline integrity evidence
  are recorded externally as `focused-scope6-final.*`, `check-l0-scope6.*`, and
  `integrity-scope6.log`. This diary does not pre-assert their outcome.

## Narrow Dry-run Follow-up (parent-reported evidence9215)
- Re-review identified Copier 9.11.1 short-option grouping: `-fn` requests force
  plus pretend, but the previous standalone-token guard could retire predecessors
  after Copier performed no writes. Mixed approved predecessor/successor trees
  made this destructive, despite earlier passing matrices.
- The wrapper now rejects grouped short switches before Copier runs and documents
  separate-switch syntax. It records the parsed standalone pretend flag in its
  preflight artifact, consuming option values (including attached and equals forms)
  without misclassifying data containing `n`. Forwarded argv is not rewritten.
- Wrapper Git reads set `GIT_OPTIONAL_LOCKS=0` so dry-run preflight cannot refresh
  destination index bytes. No production authority resolver or retirement policy
  was changed.
- Three focused regressions passed before the final commit: actual pinned Copier
  parser comparison, old-only/mixed-tree byte-and-index preservation for rejected
  grouped and supported standalone forms, and real-copy forwarding of `n` data.
  Group rejection is instrumented to prove Copier is never invoked. No child
  archetype matrix was duplicated; the full existing gate still covers it.
- Final clean-candidate results are recorded externally in `dryrun-focused-final.*`
  and `check-l0-dryrun-final.*`, with original-baseline proof in `integrity-dryrun.log`.
  The dispatch lease expires at 2026-09-11 15:22Z; no renewal is assumed.

## Scope-v8 Execution-Class Correction (parent-reported evidence9223)
- Continued only in the existing isolated clone from `347a6246eb14543eb80aa05a79f91a9c33f3fa98`.
  The prior stopped dispatch was not resumed. This correction touches only this
  diary, the L0 copy wrapper, its retirement helper, and its existing upgrade tests.
- Inspected actual Copier 9.11.1 `_cli.CopierCopySubApp.main`, `_cli.Worker.run_copy`,
  and Plumbum dispatch. Help, version, and completion commands can exit zero without
  calling the worker. Parsed pretend status and successor presence cannot prove copy.
- Retirement-capable invocations now run an explicitly version-locked Python adapter
  in the pinned runtime. A process-local Worker subclass observes successful return
  from real `run_copy`, rejects pretend as completion, and writes a fresh scratch
  signal only after the complete CLI exits successfully. The wrapper requires that
  positive signal before retirement or resealing; each invocation resets it.
- The actual CLI still owns argv parsing, warnings, version/help/completion output,
  and errors. No informational-switch blacklist was added. Grouped short-switch
  rejection remains a syntax guard, not execution evidence. Ordinary copies retain
  native pinned entrypoints, COPIER_VERSION overrides, and the warned PATH fallback;
  retirement requires uvx/uv plus supported Copier 9.11.1. Other runtime versions
  fail closed before rendering when obsolete files require retirement.
- Existing ownership, fixed fingerprints, stale checks, adoption, safe ancestors,
  successor checks, bare-copy uncertified status, and v2 refusal are unchanged.
  Copy/retirement/reseal remain non-atomic: actual failed rendering may leave partial
  writes; no rollback or protection against arbitrary trusted-template code is claimed.
- Regressions cover both old-only and approved mixed destinations: all seven
  informational spellings (output compared with native pinned Copier), standalone
  pretend, rejected grouping, invalid-option/input failures, and a zero-exit runtime
  that never executes copy. All no-render cases assert destination bytes and index
  bytes unchanged. Successful copies with `--exclude --help` and `--exclude=--version`
  prove switch-looking values remain values, all five predecessors retire, successors
  match approved hashes, index bytes stay unchanged, and the resulting seal validates.
  Adapter tests additionally reject stale signals, zero exit from inside the worker,
  and failed cleanup after actual rendering; successful real copy alone emits a signal.

### Executed Validation and Preservation
- First uncommitted safety run: 12/13 passed; existing adoption test refused a dirty
  L0 source. Validation commits were therefore required before clean-source gates.
- Initial full gate completed with exit 1 (3/7), not a pass. It exposed the existing
  supply-chain lexical contract and an incorrect global test environment override.
  Native pinned Copier invocations were retained as executable ordinary-copy branches,
  not comments/proxies. Removed global DISABLE_PROJECT_OWNER_HANDLE_INFERENCE; it had
  masked gate-owned owner-inference fixtures. No gate, fixture, or timeout was changed.
- Validated code commit: `2e4163172bfce8f810158fbd10165b6db3b6c188`;
  tree: `dcf139345dc5847a89cc83c528f819c7b88cfaa1`.
- Pinned focused suite: 15 tests passed in 219.954s, exit 0.
  Logs: `../execution-focused-final-v2.log` and `.exit`.
- Complete `bash scripts/check-l0.sh`: 7/7 passed, exit 0, none skipped.
  Guardrails: 42 tests, 243/300s; generation: 14 top-level tests, 549/600s;
  adversarial: 195/300s; fixtures: 23/300s. Documentation, checkpoint, and
  supply-chain checks also passed. Logs: `../check-l0-execution-final-v2.log` and `.exit`.
  Upstream pathspec DeprecationWarnings are present; the verbose gate's warning
  counter reports zero but is not evidence of warning-free output.
- Full-gate environment: strict existing `../fullgate-bin/ak` prepended to PATH,
  AK_CMD and owner-inference/timeout overrides unset, PYTHONDONTWRITEBYTECODE=1,
  L0_CHECK_VERBOSE=1. Gate-owned synthetic AK fixtures remain able to override PATH;
  no installed AK or live task5105 was used. No production authority was modified.
- All 5,862 entries, including canonical `.git/index`, matched the ORIGINAL
  `../canonical-before.json`, SHA256
  `1cbf3fd9d9e07a5e495d1a450bb2c263a010078a1b6bfe77541b1cd155967f9a`.
  Final post-diary-commit revalidation is recorded in `../integrity-execution-final.log`.
  The final documentation commit changes only this diary from the fully tested code
  commit; no claim is made that its new source SHA was used by the preceding gates.
- Ready for independent review, not canonical integration, AK completion, downstream
  propagation, ontology activation, or remote publication.

## Coverage Limits / Review Needed
- Outer L0 custom filename isolation is tested with a root filename containing
  spaces; child custom paths include directories and spaces. An exploratory outer
  directory-qualified answer path exposed Copier's basename reduction at L0 too.
  Fixing that would require renaming the L0 answer-template path, outside this scope;
  this candidate does not claim support for directory-qualified outer L0 answers.
- L1 wrapper inheritance still reads its conventional `.copier-answers.yml`; outer
  custom-name tests establish filename isolation, not custom-named L1 policy discovery.
- Monorepo/package persist metadata only; no new ontology activation is claimed.
- No arbitrary-YAML correctness claim: unsupported quote/escape/control inputs are
  rejected. Nested archetype bodies/defaults and the direct Copier interface are
  unchanged; boundary validation applies to L0 and the original-three L1 wrapper paths.
- Ordinary refresh still cannot replace established v2 transition provenance; no
  Softwareco v2 cutover or transition integration is claimed. Existing adoption
  records that omit obsolete paths require separate authorized reconciliation.
- No AK completion, downstream propagation, or canonical integration was performed.
  Parent must independently review before integrating.
