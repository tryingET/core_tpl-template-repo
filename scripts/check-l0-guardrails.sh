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

assert_dir() {
  path="$1"
  [ -d "$path" ] || fail "missing required directory: $path"
}

assert_absent() {
  path="$1"
  [ ! -e "$path" ] || fail "legacy path must be absent: $path"
}

assert_contains() {
  path="$1"
  needle="$2"
  label="$3"
  grep -qF -- "$needle" "$path" || fail "$label (missing '$needle' in $path)"
}

assert_not_contains() {
  path="$1"
  needle="$2"
  label="$3"
  if grep -qF -- "$needle" "$path"; then
    fail "$label (found '$needle' in $path)"
  fi
}

# L0 core files
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
copier-template/scripts/rocs.sh
copier-template/scripts/check-template-ci.sh
copier-template/scripts/install-hooks.sh
copier-template/scripts/ci/smoke.sh
copier-template/scripts/ci/full.sh
copier-template/scripts/release/check.sh
copier-template/scripts/release/publish.sh
copier-template/.github/workflows/template-check.yml
copier-template/.githooks/pre-commit
copier-template/.githooks/pre-push
scripts/preview-l1-diff.sh
scripts/rocs.sh
scripts/check-supply-chain.sh
scripts/check-l0-fixtures.sh
scripts/sync-l0-fixtures.sh
fixtures/l1/template-repo/README.md
fixtures/l1/template-repo/.copier-answers.yml
fixtures/l2/tpl-project-repo/AGENTS.md
fixtures/l2/tpl-project-repo/.copier-answers.yml
"

while IFS= read -r path; do
  [ -n "$path" ] || continue
  assert_file "$path"
done <<EOF
$required_files
EOF

# Required L2 template directories
required_dirs="
copier-template/copier/tpl-agent-repo
copier-template/copier/tpl-org-repo
copier-template/copier/tpl-project-repo
"

while IFS= read -r path; do
  [ -n "$path" ] || continue
  assert_dir "$path"
done <<EOF
$required_dirs
EOF

# L2 template required files (each template must have these)
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo; do
  assert_file "copier-template/copier/$tpl/copier.yml"
  assert_file "copier-template/copier/$tpl/AGENTS.md.j2"
  assert_file "copier-template/copier/$tpl/CODEOWNERS.j2"
  assert_file "copier-template/copier/$tpl/scripts/rocs.sh.j2"
  assert_file "copier-template/copier/$tpl/scripts/ci/smoke.sh"
  assert_file "copier-template/copier/$tpl/scripts/ci/full.sh"
  assert_exec "copier-template/copier/$tpl/scripts/rocs.sh.j2"
done

required_exec="
scripts/preview-l1-diff.sh
scripts/rocs.sh
scripts/check-supply-chain.sh
scripts/check-l0-fixtures.sh
scripts/sync-l0-fixtures.sh
copier-template/scripts/new-repo-from-copier.sh
copier-template/scripts/rocs.sh
copier-template/scripts/check-template-ci.sh
copier-template/scripts/install-hooks.sh
copier-template/scripts/ci/smoke.sh
copier-template/scripts/ci/full.sh
copier-template/scripts/release/check.sh
copier-template/scripts/release/publish.sh
copier-template/.githooks/pre-commit
copier-template/.githooks/pre-push
"

while IFS= read -r path; do
  [ -n "$path" ] || continue
  assert_exec "$path"
done <<EOF
$required_exec
EOF

# L0 copier.yml assertions
assert_contains "copier.yml" "_subdirectory: copier-template" "L0 copier source must target copier-template/"
assert_contains "copier.yml" "copier/tpl-agent-repo/" "L0 message must mention tpl-agent-repo template"
assert_contains "copier.yml" "copier/tpl-org-repo/" "L0 message must mention tpl-org-repo template"
assert_contains "copier.yml" "copier/tpl-project-repo/" "L0 message must mention tpl-project-repo template"
assert_contains "copier.yml" "l1_org_docs_profile" "L0 copier config must expose L1 org docs profile toggle"
assert_contains "copier.yml" "enable_community_pack" "L0 copier config must expose community pack toggle"
assert_contains "copier.yml" "enable_release_pack" "L0 copier config must expose release pack toggle"
assert_contains "copier.yml" "enable_vouch_gate" "L0 copier config must expose vouch gate toggle"
assert_contains "copier.yml" "rm -rf copier/template-repo" "L0 must remove legacy template-repo in _tasks"

# L1 answers template assertions
assert_contains "copier-template/{{ _copier_conf.answers_file }}.jinja" "l1_org_docs_profile:" "L1 answers template must persist L1 org docs profile"

# L2 template assertions (check tpl-project-repo as the primary example)
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "repo_slug:" "L2 copier config must have repo_slug"
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "enable_community_pack" "L2 copier config must expose community pack toggle"
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "enable_release_pack" "L2 copier config must expose release pack toggle"
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "enable_vouch_gate" "L2 copier config must expose vouch gate toggle"

for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo; do
  assert_contains "copier-template/copier/$tpl/AGENTS.md.j2" "Deterministic tooling policy" "L2 template $tpl AGENTS should include deterministic tooling policy"
  assert_contains "copier-template/copier/$tpl/AGENTS.md.j2" "scripts/rocs.sh" "L2 template $tpl AGENTS should reference scripts/rocs.sh"
  assert_contains "copier-template/copier/$tpl/README.md.j2" "ROCS command flow" "L2 template $tpl README should include ROCS command flow section"
  assert_contains "copier-template/copier/$tpl/scripts/ci/full.sh" "scripts/rocs.sh" "L2 template $tpl full CI should use scripts/rocs.sh when ontology is present"
done
assert_not_contains "copier-template/copier/tpl-project-repo/scripts/ci/full.sh" "uvx -n --from ./tools/rocs-cli rocs" "tpl-project-repo CI should not hardcode uvx vendored invocation"

# L1 wrapper script assertions
assert_contains "scripts/rocs.sh" "--doctor" "L0 ROCS wrapper should expose doctor mode"
assert_contains "scripts/rocs.sh" "deterministic resolution order" "L0 ROCS wrapper should document resolution order"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "tpl-agent-repo" "L1 wrapper must list tpl-agent-repo template"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "tpl-org-repo" "L1 wrapper must list tpl-org-repo template"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "tpl-project-repo" "L1 wrapper must list tpl-project-repo template"
assert_contains "copier-template/scripts/rocs.sh" "--doctor" "L1 ROCS wrapper should expose doctor mode"
assert_contains "copier-template/scripts/rocs.sh" "deterministic resolution order" "L1 ROCS wrapper should document resolution order"
assert_contains "copier-template/scripts/ci/full.sh" "scripts/rocs.sh" "L1 full CI should use scripts/rocs.sh when ontology is present"

# CODEOWNERS assertions
assert_contains "CODEOWNERS" "/copier-template/**" "CODEOWNERS must protect copier-template/"
assert_contains "AGENTS.md" "check-l0.sh" "AGENTS validation section should use consolidated L0 check"
assert_contains "AGENTS.md" "Deterministic tooling policy" "AGENTS should document deterministic tooling policy"
assert_contains "AGENTS.md" "scripts/rocs.sh" "AGENTS should reference scripts/rocs.sh"
assert_contains ".github/pull_request_template.md" "check-l0-guardrails.sh" "PR template must require guardrail checks"
assert_contains ".github/pull_request_template.md" "check-l0-generation.sh" "PR template must require generation checks"
assert_contains ".github/pull_request_template.md" "check-l0-fixtures.sh" "PR template should require fixture checks"
assert_contains ".github/pull_request_template.md" "check-supply-chain.sh" "PR template should require supply-chain checks"
assert_contains "CONTRIBUTING.md" "check-l0.sh" "L0 contributing guide should reference full L0 checks"
assert_contains "CONTRIBUTING.md" "scripts/rocs.sh --doctor" "L0 contributing guide should include deterministic ROCS wrapper usage"
assert_contains "CONTRIBUTING.md" "profile-governance-policy.md" "L0 contributing guide should link profile governance policy"
assert_contains "README.md" "Organization docs profiles" "README should document org docs profile behavior"
assert_contains "README.md" "Profile governance policy" "README should link profile governance policy"
assert_contains "README.md" "Community pack" "README should document optional community pack behavior"
assert_contains "README.md" "Release pack" "README should document optional release pack behavior"
assert_contains "README.md" "Structure baseline" "README should document baseline scaffold structure"
assert_contains "README.md" "Deterministic ROCS launcher" "README should document deterministic ROCS launcher"

for doc in copier-template/README.md.jinja copier-template/AGENTS.md; do
  assert_contains "$doc" "Recursion policy" "generated L1 docs must include recursion policy section"
  assert_contains "$doc" "L1 -> L2" "generated L1 docs must allow L1 -> L2"
  assert_contains "$doc" "L1 -> L0" "generated L1 docs must forbid L1 -> L0"
  assert_contains "$doc" "L2 -> L1" "generated L1 docs must forbid L2 -> L1"
done
assert_contains "copier-template/AGENTS.md" "Deterministic tooling policy" "generated L1 AGENTS should include deterministic tooling policy"
assert_contains "copier-template/AGENTS.md" "scripts/rocs.sh" "generated L1 AGENTS should reference scripts/rocs.sh"
assert_contains "copier-template/CONTRIBUTING.md" "scripts/rocs.sh --doctor" "generated L1 contributing guide should include deterministic ROCS wrapper usage"
assert_contains "copier-template/README.md.jinja" "Organization docs profile" "generated L1 README should describe org docs profile"
assert_contains "copier-template/README.md.jinja" "Deterministic ROCS launcher" "generated L1 README should describe deterministic ROCS launcher"

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
assert_contains "copier-template/.github/workflows/release-please.yml" "googleapis/release-please-action@v4" "L1 release-please workflow should invoke release-please action"
assert_contains "copier-template/.github/workflows/publish.yml" "softprops/action-gh-release@v2" "L1 publish workflow should upload release artifacts"

# Ensure legacy template-repo is removed from generated L1
assert_absent "copier-template/copier/template-repo"

# Ensure no nested copier invocations
if grep -nE 'copier[[:space:]]+(copy|update)' copier.yml >/dev/null 2>&1; then
  fail "nested copier invocations are not allowed in template config files"
fi

echo "ok: l0 guardrails"
