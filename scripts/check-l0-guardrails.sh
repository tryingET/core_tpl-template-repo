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
docs/profile-governance-policy.md
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
copier-template/.github/workflows/release-please.yml
copier-template/.github/workflows/release-check.yml
copier-template/.github/workflows/publish.yml
copier-template/.release-please-config.json
copier-template/.release-please-manifest.json
copier-template/CHANGELOG.md
copier-template/SECURITY.md
copier-template/docs/.gitkeep
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
copier-template/scripts/new-repo-from-copier.sh
copier-template/scripts/check-template-ci.sh
copier-template/scripts/install-hooks.sh
copier-template/scripts/ci/smoke.sh
copier-template/scripts/ci/full.sh
copier-template/scripts/release/check.sh
copier-template/scripts/release/publish.sh
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
copier-template/copier/template-repo/.github/workflows/release-please.yml
copier-template/copier/template-repo/.github/workflows/release-check.yml
copier-template/copier/template-repo/.github/workflows/publish.yml
copier-template/copier/template-repo/.release-please-config.json
copier-template/copier/template-repo/.release-please-manifest.json
copier-template/copier/template-repo/CHANGELOG.md
copier-template/copier/template-repo/SECURITY.md
copier-template/copier/template-repo/docs/.gitkeep
copier-template/copier/template-repo/docs/org/operating_model.md.j2
copier-template/copier/template-repo/docs/org/project-docs-intake.questions.json
copier-template/copier/template-repo/docs/org/purpose.md.j2
copier-template/copier/template-repo/docs/org/mission.md.j2
copier-template/copier/template-repo/docs/org/vision.md.j2
copier-template/copier/template-repo/docs/org/strategic_objectives.md.j2
copier-template/copier/template-repo/docs/org/values_ethics.md.j2
copier-template/copier/template-repo/docs/org/governance.md.j2
copier-template/copier/template-repo/docs/org/glossary.md.j2
copier-template/copier/template-repo/docs/project/foundation.md.j2
copier-template/copier/template-repo/docs/project/vision.md.j2
copier-template/copier/template-repo/docs/project/strategic_goals.md.j2
copier-template/copier/template-repo/docs/project/tactical_goals.md.j2
copier-template/copier/template-repo/docs/project/incentives.md.j2
copier-template/copier/template-repo/docs/project/resources.md.j2
copier-template/copier/template-repo/docs/project/skills.md.j2
copier-template/copier/template-repo/examples/.gitkeep
copier-template/copier/template-repo/external/.gitkeep
copier-template/copier/template-repo/ontology/.gitkeep
copier-template/copier/template-repo/policy/.gitkeep
copier-template/copier/template-repo/src/.gitkeep
copier-template/copier/template-repo/tests/.gitkeep
copier-template/copier/template-repo/scripts/install-hooks.sh
copier-template/copier/template-repo/scripts/ci/smoke.sh
copier-template/copier/template-repo/scripts/ci/full.sh
copier-template/copier/template-repo/scripts/release/check.sh
copier-template/copier/template-repo/scripts/release/publish.sh
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
copier-template/scripts/release/check.sh
copier-template/scripts/release/publish.sh
copier-template/.githooks/pre-commit
copier-template/.githooks/pre-push
copier-template/copier/template-repo/scripts/install-hooks.sh
copier-template/copier/template-repo/scripts/ci/smoke.sh
copier-template/copier/template-repo/scripts/ci/full.sh
copier-template/copier/template-repo/scripts/release/check.sh
copier-template/copier/template-repo/scripts/release/publish.sh
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
assert_contains "copier.yml" "l1_org_docs_profile" "L0 copier config must expose L1 org docs profile toggle"
assert_contains "copier.yml" "l2_org_docs_default" "L0 copier config must expose L2 org docs default toggle"
assert_contains "copier.yml" "enable_community_pack" "L0 copier config must expose community pack toggle"
assert_contains "copier.yml" "enable_release_pack" "L0 copier config must expose release pack toggle"
assert_contains "copier.yml" "enable_vouch_gate" "L0 copier config must expose vouch gate toggle"
assert_contains "copier-template/{{ _copier_conf.answers_file }}.jinja" "l1_org_docs_profile:" "L1 answers template must persist L1 org docs profile"
assert_contains "copier-template/{{ _copier_conf.answers_file }}.jinja" "l2_org_docs_default:" "L1 answers template must persist L2 org docs default"
assert_contains "copier-template/copier/template-repo/copier.yml" "org_docs_profile" "L2 copier config must expose org docs profile toggle"
assert_contains "copier-template/copier/template-repo/copier.yml" "org_docs_canonical_ref" "L2 copier config must expose canonical org docs reference"
assert_contains "copier-template/copier/template-repo/{{ _copier_conf.answers_file }}.j2" "org_docs_profile:" "L2 answers template must persist org docs profile"
assert_contains "copier-template/copier/template-repo/{{ _copier_conf.answers_file }}.j2" "org_docs_canonical_ref:" "L2 answers template must persist canonical org docs reference"
assert_contains "copier-template/copier/template-repo/copier.yml" "enable_community_pack" "L2 copier config must expose community pack toggle"
assert_contains "copier-template/copier/template-repo/copier.yml" "enable_release_pack" "L2 copier config must expose release pack toggle"
assert_contains "copier-template/copier/template-repo/copier.yml" "enable_vouch_gate" "L2 copier config must expose vouch gate toggle"
assert_contains "CODEOWNERS" "/copier-template/**" "CODEOWNERS must protect copier-template/"
assert_contains "AGENTS.md" "check-l0.sh" "AGENTS validation section should use consolidated L0 check"
assert_contains ".github/pull_request_template.md" "check-l0-guardrails.sh" "PR template must require guardrail checks"
assert_contains ".github/pull_request_template.md" "check-l0-generation.sh" "PR template must require generation checks"
assert_contains ".github/pull_request_template.md" "check-l0-fixtures.sh" "PR template should require fixture checks"
assert_contains ".github/pull_request_template.md" "check-supply-chain.sh" "PR template should require supply-chain checks"
assert_contains "CONTRIBUTING.md" "check-l0.sh" "L0 contributing guide should reference full L0 checks"
assert_contains "CONTRIBUTING.md" "profile-governance-policy.md" "L0 contributing guide should link profile governance policy"
assert_contains "README.md" "Organization docs profiles" "README should document org docs profile behavior"
assert_contains "README.md" "Profile governance policy" "README should link profile governance policy"
assert_contains "README.md" "Community pack" "README should document optional community pack behavior"
assert_contains "README.md" "Release pack" "README should document optional release pack behavior"
assert_contains "README.md" "Structure baseline" "README should document baseline scaffold structure"

for doc in copier-template/README.md.jinja copier-template/AGENTS.md; do
  assert_contains "$doc" "Recursion policy" "generated L1 docs must include recursion policy section"
  assert_contains "$doc" "L1 -> L2" "generated L1 docs must allow L1 -> L2"
  assert_contains "$doc" "L1 -> L0" "generated L1 docs must forbid L1 -> L0"
  assert_contains "$doc" "L2 -> L1" "generated L1 docs must forbid L2 -> L1"
done
assert_contains "copier-template/README.md.jinja" "Organization docs profile" "generated L1 README should describe org docs profile"
assert_contains "copier-template/copier/template-repo/README.md.j2" "Organization docs profile" "generated L2 README template should describe org docs profile"

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
assert_contains "copier-template/.github/workflows/release-please.yml" "googleapis/release-please-action@v4" "L1 release-please workflow should invoke release-please action"
assert_contains "copier-template/.github/workflows/publish.yml" "softprops/action-gh-release@v2" "L1 publish workflow should upload release artifacts"
assert_contains "copier-template/copier/template-repo/.github/workflows/release-please.yml" "googleapis/release-please-action@v4" "L2 release-please workflow should invoke release-please action"
assert_contains "copier-template/copier/template-repo/.github/workflows/publish.yml" "softprops/action-gh-release@v2" "L2 publish workflow should upload release artifacts"

if grep -nE 'copier[[:space:]]+(copy|update)' copier.yml copier-template/copier/template-repo/copier.yml >/dev/null 2>&1; then
  fail "nested copier invocations are not allowed in template config files"
fi

echo "ok: l0 guardrails"
