# L0 core files
required_files="
CODEOWNERS
.gitattributes
CONTRIBUTING.md
diary/README.md
copier.yml
.github/pull_request_template.md
docs/release-compatibility-policy.md
docs/l1-adoption-playbook.md
docs/l2-transition-playbook.md
docs/profile-governance-policy.md
docs/supply-chain-policy.md
docs/learnings/README.md
docs/vouch-td-primer.md
docs/feature-matrix-l0-l1-l2-vs-pi-template.md
docs/solo-builder-operating-cadence.md
docs/dev/README.md
copier-template/README.md.jinja
copier-template/AGENTS.md.jinja
copier-template/CONTRIBUTING.md
copier-template/.gitattributes
copier-template/contracts/layer-contract.yml
copier-template/contracts/template-ownership.yml
copier-template/contracts/template-ownership-state.json
copier-template/{{ _copier_conf.answers_file }}.jinja
copier-template/.github/VOUCHED.td.jinja
copier-template/.github/workflows/vouch-check-pr.yml.jinja
copier-template/.github/workflows/vouch-manage.yml.jinja
copier-template/.github/pull_request_template.md.jinja
copier-template/.github/ISSUE_TEMPLATE/config.yml.jinja
copier-template/.github/ISSUE_TEMPLATE/bug-report.yml.jinja
copier-template/.github/ISSUE_TEMPLATE/feature-request.yml.jinja
copier-template/CODE_OF_CONDUCT.md.jinja
copier-template/SUPPORT.md.jinja
copier-template/.github/workflows/release-please.yml
copier-template/.github/workflows/release-check.yml
copier-template/.github/workflows/publish.yml
copier-template/.release-please-config.json
copier-template/.release-please-manifest.json
copier-template/CHANGELOG.md
copier-template/SECURITY.md
copier-template/docs/.gitkeep
copier-template/docs/dev/tpl-project-repo-file-contract.md
copier-template/docs/org/operating_model.md.jinja
copier-template/docs/org/purpose.md.jinja
copier-template/docs/org/mission.md.jinja
copier-template/docs/org/vision.md.jinja
copier-template/docs/org/strategic_objectives.md.jinja
copier-template/docs/org/values_ethics.md.jinja
copier-template/docs/org/governance.md.jinja
copier-template/docs/org/glossary.md.jinja
copier-template/examples/.gitkeep
copier-template/external/.gitkeep
copier-template/ontology/.gitkeep
copier-template/policy/.gitkeep
copier-template/src/.gitkeep
copier-template/tests/.gitkeep
copier-template/diary/README.md.jinja
copier-template/scripts/new-repo-from-copier.sh
copier-template/scripts/bootstrap-lane-root.sh
copier-template/scripts/check-task-scope-snapshots.sh
copier-template/scripts/rocs.sh
copier-template/scripts/check-template-ci.sh
copier-template/scripts/install-hooks.sh
copier-template/scripts/lib/check-template-ak.py
copier-template/scripts/lib/run-local-hook.sh
copier-template/docs/dev/l1-local-extensions.md
copier-template/scripts/lib/check-l1-ownership-state.py
copier-template/scripts/lib/check-task-scope-snapshots.py
copier-template/scripts/lib/copier-answers.sh
copier-template/scripts/lib/repo-surface.sh
tests/test_agent_template_v2.py
tests/test_l1_template_ownership.py
tests/test_l1_template_transitions.py
tests/fixtures/l1-company-policy/AGENTS.md
tests/fixtures/l1-company-policy/README.md
tests/fixtures/l1-company-policy/CONTRIBUTING.md
tests/fixtures/l1-company-policy/.gitignore
tests/fixtures/l1-company-policy/.github/workflows/ci.yml
tests/fixtures/l1-company-policy/docs/org/operating_model.md
tests/fixtures/l1-company-policy/docs/org/company-charter.md
copier-template/scripts/lib/suffix-policy.sh
copier-template/scripts/ci/smoke.sh
copier-template/scripts/ci/full.sh
copier-template/scripts/release/check.sh
copier-template/scripts/release/publish.sh
copier-template/.github/workflows/template-check.yml
copier-template/.github/workflows/ci.yml
copier-template/.githooks/pre-commit
copier-template/.githooks/pre-push
scripts/preview-l1-diff.sh
scripts/propagate-l1-template.sh
scripts/lib/l1_template_ownership.py
scripts/lib/l1_template_receipts.py
scripts/lib/l1_template_transitions.py
scripts/lib/l1_template_gitlinks.py
scripts/lib/l1_template_retirements.py
contracts/l1-template-retirements.json
scripts/lib/run-l1-template-refresh.sh
scripts/rocs.sh
scripts/check-session-checkpoint.sh
scripts/check-supply-chain.sh
scripts/check-l0-adversarial.sh
scripts/check-l0-fixtures.sh
scripts/check-l0-rocs-consumer.sh
scripts/sync-l0-fixtures.sh
scripts/lib/copier-answers.sh
scripts/lib/fixture-normalization.sh
scripts/lib/repo-surface.sh
fixtures/l1/template-repo/README.md
fixtures/l1/template-repo/.copier-answers.yml
fixtures/l1/template-repo/contracts/template-ownership.yml
fixtures/l1/template-repo/contracts/template-ownership-state.json
fixtures/l1/template-repo/diary/README.md
fixtures/l1/template-repo/scripts/bootstrap-lane-root.sh
fixtures/l1/template-repo/scripts/lib/check-template-ak.py
fixtures/l1/template-repo/scripts/lib/check-l1-ownership-state.py
fixtures/l1/template-repo/scripts/lib/check-task-scope-snapshots.py
fixtures/l1/template-repo/scripts/lib/copier-answers.sh
fixtures/l1/template-repo/scripts/lib/repo-surface.sh
fixtures/l1/template-repo/scripts/lib/suffix-policy.sh
fixtures/l2/tpl-project-repo/AGENTS.md
fixtures/l2/tpl-project-repo/.copier-answers.yml
fixtures/l2/tpl-project-repo/diary/README.md
"

while IFS= read -r path; do
	[ -n "$path" ] || continue
	assert_file "$path"
done <<EOF
$required_files
EOF

assert_absent "copier-template/scripts/ak.sh"
assert_absent "copier-template/scripts/cargo-operator.sh"
assert_absent "governance/dist/managed-launcher-bundle.template-receipt.json"
assert_contains ".gitattributes" "**/tools/rocs-cli/** -whitespace" "L0 must preserve canonical vendored ROCS bytes from whitespace normalization"
assert_contains "copier-template/.gitattributes" "**/tools/rocs-cli/** -whitespace" "generated L1 must preserve canonical vendored ROCS bytes"
assert_contains "copier-template/contracts/template-ownership.yml" "schema: ai-society.template-ownership/2" "L1 ownership map must pin company ownership schema v2"
assert_contains "copier-template/contracts/template-ownership.yml" "company_owned:" "tree ontology requires explicit company ownership"
assert_files_equal "copier-template/scripts/lib/l1_ontology_ownership.py" "fixtures/l1/template-repo/scripts/lib/l1_ontology_ownership.py" "ontology ownership proof helper must stay identical"
for agent_path in AGENTS.md README.md CONTRIBUTING.md .gitignore .github/workflows/ci.yml 'docs/org/**'; do
	assert_contains "copier-template/contracts/template-ownership.yml" "- $agent_path" "L1 ownership map must preserve company-owned $agent_path"
done
# Company-owned local/ extension points: local/ stays outside the ownership map (target-only,
# never written or deleted by refresh) and every L1 root entry script hands off to it.
if grep -E '^  - local(/|$)' copier-template/contracts/template-ownership.yml >/dev/null; then
	fail "L1 ownership map must leave local/ unmapped (company-owned, target-only)"
fi
for local_hook in \
	".githooks/pre-commit:local/githooks/pre-commit" \
	".githooks/pre-push:local/githooks/pre-push" \
	"scripts/ci/smoke.sh:local/ci/smoke.sh" \
	"scripts/ci/full.sh:local/ci/full.sh" \
	"scripts/check-template-ci.sh:local/ci/check-template-ci.sh" \
	"scripts/install-hooks.sh:local/install-hooks.sh"; do
	grep -F -- " ${local_hook#*:}" "copier-template/${local_hook%%:*}" | grep -qF "scripts/lib/run-local-hook.sh" ||
		fail "L1 ${local_hook%%:*} must call its company extension ${local_hook#*:} through scripts/lib/run-local-hook.sh"
	assert_contains "copier-template/docs/dev/l1-local-extensions.md" "\`${local_hook#*:}\`" "L1 local-extension doc must document ${local_hook#*:}"
done
assert_contains "copier-template/scripts/install-hooks.sh" '"$repo_root/scripts/lib/run-local-hook.sh" \' "L1 install-hooks must normalize the local-hook runner executable bit"
assert_contains "copier-template/README.md.jinja" "docs/dev/l1-local-extensions.md" "L1 README must point at the local/ extension contract"
assert_contains "copier-template/AGENTS.md.jinja" "docs/dev/l1-local-extensions.md" "L1 AGENTS must point at the local/ extension contract"
assert_contains "scripts/preview-l1-diff.sh" "run-l1-template-refresh.sh" "L1 preview must use the shared non-public renderer"
assert_not_contains "scripts/preview-l1-diff.sh" "L1_TEMPLATE_APPLY" "L1 preview must be incapable of ambient apply"
assert_contains "scripts/lib/run-l1-template-refresh.sh" "l1_template_ownership.py" "L1 shared renderer must use the ownership engine"
assert_contains "scripts/lib/l1_template_receipts.py" "template-ownership-adoption.json" "L1 bootstrap must bind target-specific census evidence"
assert_contains "scripts/lib/l1_template_receipts.py" "template-ownership-state.json" "L1 ownership adoption must have a durable state marker"
assert_contains "copier-template/{{ _copier_conf.answers_file }}.jinja" "_ownership_state" "new L1 renders must carry a Copier birth marker"
assert_contains "scripts/lib/l1_template_ownership.py" "applied_pending_receipt" "L1 apply must stop before external receipt finalization"
assert_contains "scripts/lib/l1_template_receipts.py" "l1_contract_refresh_v1" "L1 finalization must require the controller-authorized AK evidence type"
assert_contains "scripts/lib/l1_template_receipts.py" "source_l0_commit" "L1 receipt must bind the clean L0 source commit"
assert_contains "scripts/lib/l1_template_receipts.py" "--git-common-dir" "L1 finalization must bind linked worktrees to the canonical AK repository"
assert_contains "scripts/lib/l1_template_receipts.py" "worktree\", \"list\", \"--porcelain\", \"-z" "L1 finalization must reject unregistered shared-Git-directory aliases"
assert_contains "scripts/lib/l1_template_receipts.py" "sanitized_git_environment" "L1 Git provenance probes must ignore ambient repository selectors"
assert_contains "scripts/lib/l1_template_receipts.py" "GIT_CONFIG_PARAMETERS" "L1 cleanliness checks must reject ambient Git status overrides"
assert_contains "scripts/lib/l1_template_receipts.py" "--untracked-files=all" "L1 finalization must fail on every untracked target path"
assert_contains "scripts/propagate-l1-template.sh" "--finalize-task" "L1 propagation must expose explicit external-receipt finalization"
assert_files_equal "copier-template/contracts/template-ownership-state.json" "fixtures/l1/template-repo/contracts/template-ownership-state.json" "rendered L1 ownership state must match source"
assert_contains "scripts/propagate-l1-template.sh" "explicit --apply" "L1 propagation must never apply silently"
assert_contains "scripts/lib/l1_template_ownership.py" "target-only paths are outside" "L1 refresh must preserve target-only local paths"
assert_contains "scripts/lib/l1_template_transitions.py" "ai-society.template-ownership-transition-plan/1" "successor plans must pin schema v1"
assert_contains "scripts/lib/l1_template_transitions.py" "ai-society.template-ownership-state/2" "successor state must pin schema v2"
assert_contains "scripts/lib/l1_template_transitions.py" "ownership_transition_pending_receipt" "successor apply must stop pending external receipt"
assert_contains "scripts/lib/l1_template_transitions.py" "l1_ownership_transition_v1" "successor finalize must require exact AK evidence type"
assert_contains "scripts/lib/l1_template_transitions.py" "post_adr_execution" "successor transitions must bind accepted post-ADR tasks"
assert_contains "scripts/lib/l1_template_transitions.py" "canonical_plan_sha256" "successor transitions must bind canonical plans"
assert_contains "scripts/lib/l1_template_ownership.py" "--transition-action" "ownership CLI must dispatch explicit successor lifecycle actions"
assert_not_contains "scripts/lib/l1_template_ownership.py" "--ak-command" "production ownership CLI must not accept an AK authority override"
assert_not_contains "scripts/lib/l1_template_transitions.py" "--ak-command" "production transition CLI must not accept an AK authority override"
assert_contains "scripts/lib/l1_template_transitions.py" "REQUIRED_VALIDATION" "successor evidence must enforce the required L1 gate policy"
assert_files_equal "copier-template/scripts/lib/check-l1-ownership-state.py" "fixtures/l1/template-repo/scripts/lib/check-l1-ownership-state.py" "generated ownership checkers must stay byte-identical"
assert_contains "copier-template/scripts/lib/check-l1-ownership-state.py" "EXECUTOR.fullmatch" "generated ownership checker must enforce exact v2 executor format"
assert_contains "copier-template/scripts/lib/check-l1-ownership-state.py" "HEX64.fullmatch" "generated ownership checker must enforce exact v2 digest formats"
assert_contains "copier-template/scripts/lib/check-l1-ownership-state.py" "HEX40.fullmatch" "generated ownership checker must enforce exact v2 Git OID formats"
assert_contains "copier-template/scripts/check-template-ci.sh" "assert_checkout_full_history" "generated template checks must lock full-history checkout policy"
assert_files_equal "copier-template/scripts/check-template-ci.sh" "fixtures/l1/template-repo/scripts/check-template-ci.sh" "generated L1 template-check script fixture must match source"
assert_files_equal "copier-template/.github/workflows/ci.yml" "fixtures/l1/template-repo/.github/workflows/ci.yml" "generated L1 CI workflow fixture must match source"
assert_files_equal "copier-template/.github/workflows/template-check.yml" "fixtures/l1/template-repo/.github/workflows/template-check.yml" "generated L1 template-check workflow fixture must match source"
assert_checkout_full_history "copier-template/.github/workflows/ci.yml"
assert_checkout_full_history "copier-template/.github/workflows/template-check.yml"
assert_files_equal "copier-template/contracts/template-ownership.yml" "fixtures/l1/template-repo/contracts/template-ownership.yml" "rendered L1 ownership map must match source"
