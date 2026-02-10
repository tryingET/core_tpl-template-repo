#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

fail() {
  echo "error: $*" >&2
  exit 1
}

assert_file() {
  path="$1"
  [ -f "$path" ] || fail "missing required file: $path"
}

assert_exec() {
  path="$1"
  [ -x "$path" ] || fail "expected executable file: $path"
}

assert_contains() {
  path="$1"
  needle="$2"
  label="$3"
  grep -qF -- "$needle" "$path" || fail "$label (missing '$needle' in $path)"
}

required_files="
CODEOWNERS
CONTRIBUTING.md
copier.yml
.github/pull_request_template.md
docs/release-compatibility-policy.md
docs/l1-adoption-playbook.md
docs/supply-chain-policy.md
docs/vouch-td-primer.md
docs/feature-matrix-l0-l1-l2-vs-pi-template.md
docs/solo-builder-operating-cadence.md
copier-template/README.md.jinja
copier-template/AGENTS.md
copier-template/CONTRIBUTING.md
copier-template/.gitattributes
copier-template/contracts/layer-contract.yml
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
copier-template/docs/.gitkeep
copier-template/examples/.gitkeep
copier-template/external/.gitkeep
copier-template/ontology/.gitkeep
copier-template/policy/.gitkeep
copier-template/src/.gitkeep
copier-template/tests/.gitkeep
copier-template/scripts/new-repo-from-copier.sh
copier-template/scripts/check-template-ci.sh
copier-template/scripts/install-hooks.sh
copier-template/scripts/ci/smoke.sh
copier-template/scripts/ci/full.sh
copier-template/.github/workflows/template-check.yml
copier-template/.githooks/pre-commit
copier-template/.githooks/pre-push
copier-template/copier/template-repo/copier.yml
copier-template/copier/template-repo/README.md.j2
copier-template/copier/template-repo/AGENTS.md
copier-template/copier/template-repo/CONTRIBUTING.md
copier-template/copier/template-repo/.gitattributes
copier-template/copier/template-repo/contracts/layer-contract.yml
copier-template/copier/template-repo/{{ _copier_conf.answers_file }}.j2
copier-template/copier/template-repo/.github/VOUCHED.td.j2
copier-template/copier/template-repo/.github/workflows/vouch-check-pr.yml.j2
copier-template/copier/template-repo/.github/workflows/vouch-manage.yml.j2
copier-template/copier/template-repo/.github/pull_request_template.md.j2
copier-template/copier/template-repo/.github/ISSUE_TEMPLATE/config.yml.j2
copier-template/copier/template-repo/.github/ISSUE_TEMPLATE/bug-report.yml.j2
copier-template/copier/template-repo/.github/ISSUE_TEMPLATE/feature-request.yml.j2
copier-template/copier/template-repo/CODE_OF_CONDUCT.md.j2
copier-template/copier/template-repo/SUPPORT.md.j2
copier-template/copier/template-repo/docs/.gitkeep
copier-template/copier/template-repo/examples/.gitkeep
copier-template/copier/template-repo/external/.gitkeep
copier-template/copier/template-repo/ontology/.gitkeep
copier-template/copier/template-repo/policy/.gitkeep
copier-template/copier/template-repo/src/.gitkeep
copier-template/copier/template-repo/tests/.gitkeep
copier-template/copier/template-repo/scripts/install-hooks.sh
copier-template/copier/template-repo/scripts/ci/smoke.sh
copier-template/copier/template-repo/scripts/ci/full.sh
copier-template/copier/template-repo/.githooks/pre-commit
copier-template/copier/template-repo/.githooks/pre-push
scripts/preview-l1-diff.sh
scripts/check-supply-chain.sh
scripts/check-l0-fixtures.sh
scripts/sync-l0-fixtures.sh
fixtures/l1/template-repo/README.md
fixtures/l1/template-repo/.copier-answers.yml
fixtures/l2/template-repo/README.md
fixtures/l2/template-repo/.copier-answers.yml
"

while IFS= read -r path; do
  [ -n "$path" ] || continue
  assert_file "$path"
done <<EOF
$required_files
EOF

required_exec="
scripts/preview-l1-diff.sh
scripts/check-supply-chain.sh
scripts/check-l0-fixtures.sh
scripts/sync-l0-fixtures.sh
copier-template/scripts/new-repo-from-copier.sh
copier-template/scripts/check-template-ci.sh
copier-template/scripts/install-hooks.sh
copier-template/scripts/ci/smoke.sh
copier-template/scripts/ci/full.sh
copier-template/.githooks/pre-commit
copier-template/.githooks/pre-push
copier-template/copier/template-repo/scripts/install-hooks.sh
copier-template/copier/template-repo/scripts/ci/smoke.sh
copier-template/copier/template-repo/scripts/ci/full.sh
copier-template/copier/template-repo/.githooks/pre-commit
copier-template/copier/template-repo/.githooks/pre-push
"

while IFS= read -r path; do
  [ -n "$path" ] || continue
  assert_exec "$path"
done <<EOF
$required_exec
EOF

assert_contains "copier.yml" "_subdirectory: copier-template" "L0 copier source must target copier-template/"
assert_contains "copier.yml" "- template-repo" "L0 must expose the template-repo profile"
assert_contains "copier.yml" "enable_community_pack" "L0 copier config must expose community pack toggle"
assert_contains "copier.yml" "enable_vouch_gate" "L0 copier config must expose vouch gate toggle"
assert_contains "copier-template/copier/template-repo/copier.yml" "enable_community_pack" "L2 copier config must expose community pack toggle"
assert_contains "copier-template/copier/template-repo/copier.yml" "enable_vouch_gate" "L2 copier config must expose vouch gate toggle"
assert_contains "CODEOWNERS" "/copier-template/**" "CODEOWNERS must protect copier-template/"
assert_contains "AGENTS.md" "check-l0.sh" "AGENTS validation section should use consolidated L0 check"
assert_contains ".github/pull_request_template.md" "check-l0-guardrails.sh" "PR template must require guardrail checks"
assert_contains ".github/pull_request_template.md" "check-l0-generation.sh" "PR template must require generation checks"
assert_contains ".github/pull_request_template.md" "check-l0-fixtures.sh" "PR template should require fixture checks"
assert_contains ".github/pull_request_template.md" "check-supply-chain.sh" "PR template should require supply-chain checks"
assert_contains "CONTRIBUTING.md" "check-l0.sh" "L0 contributing guide should reference full L0 checks"
assert_contains "README.md" "Community pack" "README should document optional community pack behavior"
assert_contains "README.md" "Structure baseline" "README should document baseline scaffold structure"

for doc in copier-template/README.md.jinja copier-template/AGENTS.md; do
  assert_contains "$doc" "Recursion policy" "generated L1 docs must include recursion policy section"
  assert_contains "$doc" "L1 -> L2" "generated L1 docs must allow L1 -> L2"
  assert_contains "$doc" "L1 -> L0" "generated L1 docs must forbid L1 -> L0"
  assert_contains "$doc" "L2 -> L1" "generated L1 docs must forbid L2 -> L1"
done

contract="copier-template/contracts/layer-contract.yml"
assert_contains "$contract" "layer: L1" "generated L1 contract must declare layer L1"
assert_contains "$contract" "L0 -> L1" "generated L1 contract must include inbound transition"
assert_contains "$contract" "L1 -> L2" "generated L1 contract must include allowed outbound transition"
assert_contains "$contract" "L1 -> L0" "generated L1 contract must include forbidden reverse transition"
assert_contains "$contract" "L2 -> L1" "generated L1 contract must include forbidden reverse transition"
assert_contains "$contract" "nested_copier_tasks_allowed: false" "generated L1 contract must forbid nested copier tasks"
assert_contains "$contract" "max_layer_depth: 2" "generated L1 contract must cap layer depth"

assert_contains "copier-template/.github/workflows/vouch-check-pr.yml.jinja" "mitchellh/vouch/action/check-pr@5713ce1baedf75e2f830afa3dac813a9c48bff12" "L1 vouch-check workflow should pin action SHA"
assert_contains "copier-template/.github/workflows/vouch-manage.yml.jinja" "mitchellh/vouch/action/manage-by-issue@5713ce1baedf75e2f830afa3dac813a9c48bff12" "L1 vouch-manage workflow should pin action SHA"
assert_contains "copier-template/copier/template-repo/.github/workflows/vouch-check-pr.yml.j2" "mitchellh/vouch/action/check-pr@5713ce1baedf75e2f830afa3dac813a9c48bff12" "L2 vouch-check workflow should pin action SHA"
assert_contains "copier-template/copier/template-repo/.github/workflows/vouch-manage.yml.j2" "mitchellh/vouch/action/manage-by-issue@5713ce1baedf75e2f830afa3dac813a9c48bff12" "L2 vouch-manage workflow should pin action SHA"

if grep -nE 'copier[[:space:]]+(copy|update)' copier.yml copier-template/copier/template-repo/copier.yml >/dev/null 2>&1; then
  fail "nested copier invocations are not allowed in template config files"
fi

echo "ok: l0 guardrails"
