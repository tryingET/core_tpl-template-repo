#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: missing dependency: $1" >&2
    exit 2
  }
}

need_cmd awk
need_cmd git
need_cmd grep
need_cmd mktemp

fail() {
  echo "error: $*" >&2
  exit 1
}

assert_file() {
  path="$1"
  [ -f "$path" ] || fail "missing file: $path"
}

assert_not_file() {
  path="$1"
  [ ! -f "$path" ] || fail "unexpected file present: $path"
}

assert_exec() {
  path="$1"
  [ -x "$path" ] || fail "missing executable bit: $path"
}

assert_contains() {
  path="$1"
  needle="$2"
  label="$3"
  grep -qF -- "$needle" "$path" || fail "$label (missing '$needle' in $path)"
}

value_from_answers() {
  answers_file="$1"
  key="$2"

  awk -F':' -v key="$key" '
    $1 ~ "^" key "$" {
      v=$2
      gsub(/^[ \t]+|[ \t]+$/, "", v)
      gsub(/"/, "", v)
      gsub(/\047/, "", v)
      print tolower(v)
      exit
    }
  ' "$answers_file"
}

bool_from_answers() {
  value_from_answers "$1" "$2"
}

required_files="
README.md
AGENTS.md
CONTRIBUTING.md
.gitattributes
.copier-answers.yml
contracts/layer-contract.yml
scripts/new-repo-from-copier.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.github/VOUCHED.td
.github/workflows/template-check.yml
.github/workflows/ci.yml
.github/workflows/vouch-check-pr.yml
.github/workflows/vouch-manage.yml
.githooks/pre-commit
.githooks/pre-push
docs/.gitkeep
docs/org/operating_model.md
examples/.gitkeep
external/.gitkeep
ontology/.gitkeep
policy/.gitkeep
src/.gitkeep
tests/.gitkeep
copier/template-repo/copier.yml
copier/template-repo/README.md.j2
copier/template-repo/CODEOWNERS.j2
copier/template-repo/.gitattributes
copier/template-repo/.github/VOUCHED.td.j2
copier/template-repo/.github/workflows/vouch-check-pr.yml.j2
copier/template-repo/.github/workflows/vouch-manage.yml.j2
copier/template-repo/.github/pull_request_template.md.j2
copier/template-repo/.github/ISSUE_TEMPLATE/config.yml.j2
copier/template-repo/.github/ISSUE_TEMPLATE/bug-report.yml.j2
copier/template-repo/.github/ISSUE_TEMPLATE/feature-request.yml.j2
copier/template-repo/CODE_OF_CONDUCT.md.j2
copier/template-repo/SUPPORT.md.j2
copier/template-repo/.release-please-config.json
copier/template-repo/.release-please-manifest.json
copier/template-repo/CHANGELOG.md
copier/template-repo/SECURITY.md
copier/template-repo/contracts/layer-contract.yml.j2
copier/template-repo/contracts/provenance-seal.yml.j2
copier/template-repo/docs/.gitkeep
copier/template-repo/docs/_core/.gitkeep
copier/template-repo/docs/system4d/.gitkeep
copier/template-repo/docs/decisions/.gitkeep
copier/template-repo/docs/dev/.gitkeep
copier/template-repo/docs/person/.gitkeep
copier/template-repo/docs/learnings/.gitkeep
copier/template-repo/docs/registers/.gitkeep
copier/template-repo/docs/org/operating_model.md.j2
copier/template-repo/docs/org/project-docs-intake.questions.json
copier/template-repo/docs/org/purpose.md.j2
copier/template-repo/docs/org/mission.md.j2
copier/template-repo/docs/org/vision.md.j2
copier/template-repo/docs/org/strategic_objectives.md.j2
copier/template-repo/docs/org/values_ethics.md.j2
copier/template-repo/docs/org/governance.md.j2
copier/template-repo/docs/org/glossary.md.j2
copier/template-repo/docs/org_context/operating_model.md.j2
copier/template-repo/docs/org_context/project-docs-intake.questions.json
copier/template-repo/docs/project/foundation.md.j2
copier/template-repo/docs/project/governance_overlay.md.j2
copier/template-repo/docs/project/vision.md.j2
copier/template-repo/docs/project/strategic_goals.md.j2
copier/template-repo/docs/project/tactical_goals.md.j2
copier/template-repo/docs/project/incentives.md.j2
copier/template-repo/docs/project/resources.md.j2
copier/template-repo/docs/project/skills.md.j2
copier/template-repo/governance/consent.md.j2
copier/template-repo/prompts/activities/.gitkeep
copier/template-repo/ontology/manifest.yaml.j2
copier/template-repo/ontology/src/.gitkeep
copier/template-repo/.github/workflows/release-please.yml
copier/template-repo/.github/workflows/release-check.yml
copier/template-repo/.github/workflows/publish.yml
copier/template-repo/scripts/release/check.sh
copier/template-repo/scripts/release/publish.sh
"

for path in $required_files; do
  assert_file "$path"
done

for path in copier/*; do
  [ -d "$path" ] || continue
  name="$(basename "$path")"
  [ "$name" = "template-repo" ] || fail "legacy or unsupported L2 template tree detected under copier/: $name"
done

required_exec="
scripts/new-repo-from-copier.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.githooks/pre-commit
.githooks/pre-push
copier/template-repo/scripts/release/check.sh
copier/template-repo/scripts/release/publish.sh
"

for path in $required_exec; do
  assert_exec "$path"
done

for doc in README.md AGENTS.md; do
  assert_contains "$doc" "Recursion policy" "L1 docs must contain recursion policy section"
  assert_contains "$doc" "L1 -> L2" "L1 docs must allow L1 -> L2"
  assert_contains "$doc" "L1 -> L0" "L1 docs must forbid L1 -> L0"
  assert_contains "$doc" "L2 -> L1" "L1 docs must forbid L2 -> L1"
done
assert_contains "CONTRIBUTING.md" "check-template-ci.sh" "L1 contributing guide should reference template checks"
assert_contains "README.md" "Organization docs profile" "L1 README should describe organization docs profile"
assert_contains "README.md" "Governance layering" "L1 README should describe governance layering"
assert_contains "README.md" "Community profile" "L1 README should describe community profile toggle"
assert_contains "README.md" "Release profile" "L1 README should describe release profile toggle"
assert_contains "README.md" "Baseline structure" "L1 README should describe baseline directory structure"
assert_contains "README.md" ".gitattributes" "L1 README should mention git baseline files"

contract="contracts/layer-contract.yml"
assert_contains "$contract" "layer: L1" "L1 contract layer mismatch"
assert_contains "$contract" "L0 -> L1" "L1 contract must include L0 -> L1"
assert_contains "$contract" "L1 -> L2" "L1 contract must include L1 -> L2"
assert_contains "$contract" "L1 -> L0" "L1 contract must include forbidden reverse edge"
assert_contains "$contract" "L2 -> L1" "L1 contract must include forbidden reverse edge"
assert_contains "$contract" "nested_copier_tasks_allowed: false" "L1 contract must forbid nested copier tasks"
assert_contains ".copier-answers.yml" "l1_org_docs_profile:" "L1 answers file should persist L1 org docs profile"
assert_contains ".copier-answers.yml" "l2_org_docs_default:" "L1 answers file should persist L2 org docs default"
assert_contains "copier/template-repo/copier.yml" "repo_archetype" "nested L2 copier config must expose archetype selector"
assert_contains "copier/template-repo/.copier-answers.yml.j2" "repo_archetype:" "nested L2 answers template should persist archetype"
assert_contains "copier/template-repo/copier.yml" "org_docs_profile" "nested L2 copier config must expose org docs profile toggle"
assert_contains "copier/template-repo/copier.yml" "org_docs_canonical_ref" "nested L2 copier config must expose canonical org docs reference"
assert_contains "copier/template-repo/.copier-answers.yml.j2" "org_docs_profile:" "nested L2 answers template should persist org docs profile"
assert_contains "copier/template-repo/.copier-answers.yml.j2" "org_docs_canonical_ref:" "nested L2 answers template should persist canonical org docs reference"
assert_contains "copier/template-repo/copier.yml" "core_owner_handle" "nested L2 copier config must expose ownership handles"
assert_contains "copier/template-repo/copier.yml" "kernel_ontology_ref" "nested L2 copier config must expose ontology refs"
assert_contains "copier/template-repo/copier.yml" "template_source_sha" "nested L2 copier config must expose template source sha"
assert_contains "copier/template-repo/.copier-answers.yml.j2" "core_owner_handle:" "nested L2 answers template should persist ownership handles"
assert_contains "copier/template-repo/.copier-answers.yml.j2" "kernel_ontology_ref:" "nested L2 answers template should persist ontology refs"
assert_contains "copier/template-repo/.copier-answers.yml.j2" "template_source_sha:" "nested L2 answers template should persist template source sha"
assert_contains "scripts/new-repo-from-copier.sh" "template_source_sha" "L1 wrapper should inject template source sha"
assert_contains "copier/template-repo/contracts/layer-contract.yml.j2" "archetype: {{ repo_archetype }}" "nested L2 contract template must declare archetype"
assert_contains "copier/template-repo/contracts/layer-contract.yml.j2" "governance_model:" "nested L2 contract template must declare governance model"
assert_contains "copier/template-repo/contracts/provenance-seal.yml.j2" "schema: ai-society.template-provenance.v1" "nested L2 provenance template must declare schema"
assert_contains "copier/template-repo/contracts/provenance-seal.yml.j2" "source_sha:" "nested L2 provenance template must include source sha"
assert_contains "copier/template-repo/contracts/provenance-seal.yml.j2" "content_hash_sha256" "nested L2 provenance template must include render hash"
assert_contains "copier/template-repo/copier.yml" "enable_community_pack" "nested L2 copier config must expose community pack toggle"
assert_contains "copier/template-repo/copier.yml" "enable_release_pack" "nested L2 copier config must expose release pack toggle"
assert_contains "copier/template-repo/copier.yml" "enable_vouch_gate" "nested L2 copier config must expose vouch gate toggle"

workflow=".github/workflows/template-check.yml"
assert_contains "$workflow" "pull_request:" "template-check workflow must run on pull requests"
assert_contains "$workflow" "push:" "template-check workflow must run on pushes"
assert_contains "$workflow" "./scripts/check-template-ci.sh" "template-check workflow must run template checks"

assert_contains ".githooks/pre-commit" "scripts/ci/smoke.sh" "pre-commit must run smoke lane"
assert_contains ".githooks/pre-push" "scripts/ci/full.sh" "pre-push must run full lane"

vouch_enabled="$(bool_from_answers .copier-answers.yml enable_vouch_gate || true)"
if [ "$vouch_enabled" = "true" ]; then
  assert_contains ".github/workflows/vouch-check-pr.yml" "pull_request_target" "vouch-check-pr must be active when enable_vouch_gate=true"
  assert_contains ".github/workflows/vouch-check-pr.yml" "mitchellh/vouch/action/check-pr@5713ce1baedf75e2f830afa3dac813a9c48bff12" "vouch-check-pr action must be SHA pinned"
  assert_contains ".github/workflows/vouch-check-pr.yml" "require-vouch: \"true\"" "vouch-check-pr must enforce vouched contributors"
  assert_contains ".github/workflows/vouch-manage.yml" "issue_comment" "vouch-manage must be active when enable_vouch_gate=true"
  assert_contains ".github/workflows/vouch-manage.yml" "mitchellh/vouch/action/manage-by-issue@5713ce1baedf75e2f830afa3dac813a9c48bff12" "vouch-manage action must be SHA pinned"
else
  assert_contains ".github/workflows/vouch-check-pr.yml" "workflow_dispatch:" "vouch-check-pr should be inactive when enable_vouch_gate=false"
  assert_contains ".github/workflows/vouch-check-pr.yml" "vouch gate disabled" "vouch-check-pr disabled workflow should explain status"
  assert_contains ".github/workflows/vouch-manage.yml" "workflow_dispatch:" "vouch-manage should be inactive when enable_vouch_gate=false"
  assert_contains ".github/workflows/vouch-manage.yml" "vouch manage workflow disabled" "vouch-manage disabled workflow should explain status"
fi

community_enabled="$(bool_from_answers .copier-answers.yml enable_community_pack || true)"
if [ "$community_enabled" = "true" ]; then
  assert_file "CODE_OF_CONDUCT.md"
  assert_file "SUPPORT.md"
  assert_file ".github/pull_request_template.md"
  assert_file ".github/ISSUE_TEMPLATE/config.yml"
  assert_file ".github/ISSUE_TEMPLATE/bug-report.yml"
  assert_file ".github/ISSUE_TEMPLATE/feature-request.yml"
  assert_contains ".github/ISSUE_TEMPLATE/config.yml" "blank_issues_enabled: false" "community issue-template config should disable blank issues"
else
  assert_not_file "CODE_OF_CONDUCT.md"
  assert_not_file "SUPPORT.md"
  assert_not_file ".github/pull_request_template.md"
  assert_not_file ".github/ISSUE_TEMPLATE/config.yml"
  assert_not_file ".github/ISSUE_TEMPLATE/bug-report.yml"
  assert_not_file ".github/ISSUE_TEMPLATE/feature-request.yml"
fi

release_enabled="$(bool_from_answers .copier-answers.yml enable_release_pack || true)"
if [ "$release_enabled" = "true" ]; then
  assert_file ".release-please-config.json"
  assert_file ".release-please-manifest.json"
  assert_file "CHANGELOG.md"
  assert_file "SECURITY.md"
  assert_file ".github/workflows/release-please.yml"
  assert_file ".github/workflows/release-check.yml"
  assert_file ".github/workflows/publish.yml"
  assert_exec "scripts/release/check.sh"
  assert_exec "scripts/release/publish.sh"
  assert_contains ".github/workflows/release-please.yml" "googleapis/release-please-action@v4" "release-please workflow should use release-please action"
  assert_contains ".github/workflows/publish.yml" "softprops/action-gh-release@v2" "publish workflow should upload release artifacts"
else
  assert_not_file ".release-please-config.json"
  assert_not_file ".release-please-manifest.json"
  assert_not_file "CHANGELOG.md"
  assert_not_file "SECURITY.md"
  assert_not_file ".github/workflows/release-please.yml"
  assert_not_file ".github/workflows/release-check.yml"
  assert_not_file ".github/workflows/publish.yml"
  assert_not_file "scripts/release/check.sh"
  assert_not_file "scripts/release/publish.sh"
fi

l1_org_docs_profile="$(value_from_answers .copier-answers.yml l1_org_docs_profile || true)"
[ -n "$l1_org_docs_profile" ] || l1_org_docs_profile="rich"

if [ "$l1_org_docs_profile" = "rich" ]; then
  assert_file "docs/org/purpose.md"
  assert_file "docs/org/mission.md"
  assert_file "docs/org/vision.md"
  assert_file "docs/org/strategic_objectives.md"
  assert_file "docs/org/values_ethics.md"
  assert_file "docs/org/governance.md"
  assert_file "docs/org/glossary.md"
else
  assert_not_file "docs/org/purpose.md"
  assert_not_file "docs/org/mission.md"
  assert_not_file "docs/org/vision.md"
  assert_not_file "docs/org/strategic_objectives.md"
  assert_not_file "docs/org/values_ethics.md"
  assert_not_file "docs/org/governance.md"
  assert_not_file "docs/org/glossary.md"
fi

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

l2_dir="$tmp_root/l2-sample"
./scripts/new-repo-from-copier.sh template-repo "$l2_dir" \
  -d repo_slug=l2-sample \
  --defaults --overwrite >/dev/null

l2_required_files="
README.md
AGENTS.md
CONTRIBUTING.md
CODEOWNERS
.gitattributes
.copier-answers.yml
contracts/layer-contract.yml
contracts/provenance-seal.yml
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.github/VOUCHED.td
.githooks/pre-commit
.githooks/pre-push
.github/workflows/ci.yml
.github/workflows/vouch-check-pr.yml
.github/workflows/vouch-manage.yml
docs/.gitkeep
docs/_core/.gitkeep
docs/system4d/.gitkeep
docs/decisions/.gitkeep
docs/dev/.gitkeep
docs/org/operating_model.md
docs/org/project-docs-intake.questions.json
docs/org_context/operating_model.md
docs/org_context/project-docs-intake.questions.json
docs/project/foundation.md
docs/project/governance_overlay.md
docs/project/vision.md
docs/project/strategic_goals.md
docs/project/tactical_goals.md
docs/project/incentives.md
docs/project/resources.md
docs/project/skills.md
examples/.gitkeep
external/.gitkeep
ontology/.gitkeep
ontology/src/.gitkeep
ontology/manifest.yaml
policy/.gitkeep
src/.gitkeep
tests/.gitkeep
"

for path in $l2_required_files; do
  [ -f "$l2_dir/$path" ] || fail "generated L2 missing file: $path"
done

l2_required_exec="
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.githooks/pre-commit
.githooks/pre-push
"

for path in $l2_required_exec; do
  [ -x "$l2_dir/$path" ] || fail "generated L2 file not executable: $path"
done

assert_contains "$l2_dir/README.md" "Recursion policy" "generated L2 README must include recursion section"
assert_contains "$l2_dir/README.md" "L2 -> L1" "generated L2 README must forbid L2 -> L1"
assert_contains "$l2_dir/README.md" "Organization docs profile" "generated L2 README should describe org docs profile"
assert_contains "$l2_dir/README.md" "Governance layering" "generated L2 README should describe governance layering"
assert_contains "$l2_dir/README.md" "Release pack" "generated L2 README should describe release profile toggle"
assert_contains "$l2_dir/README.md" "Baseline structure" "generated L2 README should describe baseline directory structure"
assert_contains "$l2_dir/CONTRIBUTING.md" ".copier-answers.yml" "generated L2 contributing guide should mention answers-file reproducibility"
assert_contains "$l2_dir/contracts/layer-contract.yml" "layer: L2" "generated L2 contract layer mismatch"
assert_contains "$l2_dir/contracts/layer-contract.yml" "L2 -> L1" "generated L2 contract must forbid reverse edge"
assert_contains "$l2_dir/contracts/layer-contract.yml" "archetype: project" "generated L2 contract archetype mismatch"
assert_contains "$l2_dir/contracts/layer-contract.yml" "governance_model: org-baseline-plus-project-overlay" "generated L2 contract must declare governance layering model"
assert_contains "$l2_dir/contracts/provenance-seal.yml" "schema: ai-society.template-provenance.v1" "generated L2 provenance seal must declare schema"
assert_contains "$l2_dir/contracts/provenance-seal.yml" "archetype: \"project\"" "generated L2 provenance seal must capture archetype"
assert_contains "$l2_dir/contracts/provenance-seal.yml" "content_hash_sha256:" "generated L2 provenance seal must capture render hash"
if grep -q "__RENDER_HASH__" "$l2_dir/contracts/provenance-seal.yml"; then
  fail "generated L2 provenance seal must not retain hash placeholder"
fi
assert_contains "$l2_dir/docs/project/governance_overlay.md" "Approved deviations register" "generated L2 governance overlay must include deviation register"
assert_not_file "$l2_dir/docs/person/.gitkeep"
assert_not_file "$l2_dir/docs/learnings/.gitkeep"
assert_not_file "$l2_dir/docs/registers/.gitkeep"
assert_not_file "$l2_dir/prompts/activities/.gitkeep"
assert_not_file "$l2_dir/governance/consent.md"

assert_contains "$l2_dir/.copier-answers.yml" "template_source_sha:" "generated L2 answers file should persist template source sha"
l2_repo_archetype="$(value_from_answers "$l2_dir/.copier-answers.yml" repo_archetype || true)"
[ -n "$l2_repo_archetype" ] || l2_repo_archetype="project"
[ "$l2_repo_archetype" = "project" ] || fail "default generated L2 archetype should be project"

l2_org_docs_profile="$(value_from_answers "$l2_dir/.copier-answers.yml" org_docs_profile || true)"
[ -n "$l2_org_docs_profile" ] || l2_org_docs_profile="compact"
if [ "$l2_org_docs_profile" = "rich" ]; then
  assert_file "$l2_dir/docs/org/purpose.md"
  assert_file "$l2_dir/docs/org/mission.md"
  assert_file "$l2_dir/docs/org/vision.md"
  assert_file "$l2_dir/docs/org/strategic_objectives.md"
  assert_file "$l2_dir/docs/org/values_ethics.md"
  assert_file "$l2_dir/docs/org/governance.md"
  assert_file "$l2_dir/docs/org/glossary.md"
else
  assert_not_file "$l2_dir/docs/org/purpose.md"
  assert_not_file "$l2_dir/docs/org/mission.md"
  assert_not_file "$l2_dir/docs/org/vision.md"
  assert_not_file "$l2_dir/docs/org/strategic_objectives.md"
  assert_not_file "$l2_dir/docs/org/values_ethics.md"
  assert_not_file "$l2_dir/docs/org/governance.md"
  assert_not_file "$l2_dir/docs/org/glossary.md"
fi

l2_vouch_enabled="$(bool_from_answers "$l2_dir/.copier-answers.yml" enable_vouch_gate || true)"
if [ "$l2_vouch_enabled" = "true" ]; then
  assert_contains "$l2_dir/.github/workflows/vouch-check-pr.yml" "pull_request_target" "generated L2 vouch-check-pr must be active when enable_vouch_gate=true"
  assert_contains "$l2_dir/.github/workflows/vouch-check-pr.yml" "mitchellh/vouch/action/check-pr@5713ce1baedf75e2f830afa3dac813a9c48bff12" "generated L2 vouch-check-pr action must be SHA pinned"
  assert_contains "$l2_dir/.github/workflows/vouch-manage.yml" "issue_comment" "generated L2 vouch-manage must be active when enable_vouch_gate=true"
else
  assert_contains "$l2_dir/.github/workflows/vouch-check-pr.yml" "workflow_dispatch:" "generated L2 vouch-check-pr should be inactive when enable_vouch_gate=false"
  assert_contains "$l2_dir/.github/workflows/vouch-manage.yml" "workflow_dispatch:" "generated L2 vouch-manage should be inactive when enable_vouch_gate=false"
fi

l2_community_enabled="$(bool_from_answers "$l2_dir/.copier-answers.yml" enable_community_pack || true)"
if [ "$l2_community_enabled" = "true" ]; then
  assert_file "$l2_dir/CODE_OF_CONDUCT.md"
  assert_file "$l2_dir/SUPPORT.md"
  assert_file "$l2_dir/.github/pull_request_template.md"
  assert_file "$l2_dir/.github/ISSUE_TEMPLATE/config.yml"
  assert_file "$l2_dir/.github/ISSUE_TEMPLATE/bug-report.yml"
  assert_file "$l2_dir/.github/ISSUE_TEMPLATE/feature-request.yml"
  assert_contains "$l2_dir/.github/ISSUE_TEMPLATE/config.yml" "blank_issues_enabled: false" "generated L2 community issue-template config should disable blank issues"
else
  assert_not_file "$l2_dir/CODE_OF_CONDUCT.md"
  assert_not_file "$l2_dir/SUPPORT.md"
  assert_not_file "$l2_dir/.github/pull_request_template.md"
  assert_not_file "$l2_dir/.github/ISSUE_TEMPLATE/config.yml"
  assert_not_file "$l2_dir/.github/ISSUE_TEMPLATE/bug-report.yml"
  assert_not_file "$l2_dir/.github/ISSUE_TEMPLATE/feature-request.yml"
fi

l2_release_enabled="$(bool_from_answers "$l2_dir/.copier-answers.yml" enable_release_pack || true)"
if [ "$l2_release_enabled" = "true" ]; then
  assert_file "$l2_dir/.release-please-config.json"
  assert_file "$l2_dir/.release-please-manifest.json"
  assert_file "$l2_dir/CHANGELOG.md"
  assert_file "$l2_dir/SECURITY.md"
  assert_file "$l2_dir/.github/workflows/release-please.yml"
  assert_file "$l2_dir/.github/workflows/release-check.yml"
  assert_file "$l2_dir/.github/workflows/publish.yml"
  assert_exec "$l2_dir/scripts/release/check.sh"
  assert_exec "$l2_dir/scripts/release/publish.sh"
  assert_contains "$l2_dir/.github/workflows/release-please.yml" "googleapis/release-please-action@v4" "generated L2 release-please workflow should use release-please action"
  assert_contains "$l2_dir/.github/workflows/publish.yml" "softprops/action-gh-release@v2" "generated L2 publish workflow should upload release artifacts"
else
  assert_not_file "$l2_dir/.release-please-config.json"
  assert_not_file "$l2_dir/.release-please-manifest.json"
  assert_not_file "$l2_dir/CHANGELOG.md"
  assert_not_file "$l2_dir/SECURITY.md"
  assert_not_file "$l2_dir/.github/workflows/release-please.yml"
  assert_not_file "$l2_dir/.github/workflows/release-check.yml"
  assert_not_file "$l2_dir/.github/workflows/publish.yml"
  assert_not_file "$l2_dir/scripts/release/check.sh"
  assert_not_file "$l2_dir/scripts/release/publish.sh"
fi

for archetype in agent org owned; do
  variant_dir="$tmp_root/l2-$archetype"
  ./scripts/new-repo-from-copier.sh template-repo "$variant_dir" \
    -d repo_slug="l2-$archetype" \
    -d repo_archetype="$archetype" \
    --defaults --overwrite >/dev/null

  assert_file "$variant_dir/.copier-answers.yml"
  assert_contains "$variant_dir/contracts/layer-contract.yml" "archetype: $archetype" "generated L2 contract archetype mismatch"
  assert_contains "$variant_dir/contracts/provenance-seal.yml" "archetype: \"$archetype\"" "generated L2 provenance seal archetype mismatch"
  if grep -q "__RENDER_HASH__" "$variant_dir/contracts/provenance-seal.yml"; then
    fail "generated L2 provenance seal must not retain hash placeholder"
  fi

  case "$archetype" in
    agent)
      assert_contains "$variant_dir/contracts/layer-contract.yml" "governance_model: agent-local-governance" "agent archetype must set agent governance model"
      assert_file "$variant_dir/docs/person/.gitkeep"
      assert_file "$variant_dir/docs/system4d/.gitkeep"
      assert_file "$variant_dir/docs/learnings/.gitkeep"
      assert_file "$variant_dir/prompts/activities/.gitkeep"
      assert_not_file "$variant_dir/docs/project/foundation.md"
      assert_not_file "$variant_dir/docs/org/operating_model.md"
      assert_not_file "$variant_dir/src/.gitkeep"
      assert_not_file "$variant_dir/ontology/.gitkeep"
      assert_not_file "$variant_dir/governance/consent.md"
      ;;
    org)
      assert_contains "$variant_dir/contracts/layer-contract.yml" "governance_model: org-governance-primary" "org archetype must set org governance model"
      assert_file "$variant_dir/docs/org/operating_model.md"
      assert_file "$variant_dir/docs/system4d/.gitkeep"
      assert_file "$variant_dir/docs/registers/.gitkeep"
      assert_file "$variant_dir/docs/decisions/.gitkeep"
      assert_file "$variant_dir/governance/consent.md"
      assert_not_file "$variant_dir/docs/project/foundation.md"
      assert_not_file "$variant_dir/docs/person/.gitkeep"
      assert_not_file "$variant_dir/prompts/activities/.gitkeep"
      assert_not_file "$variant_dir/src/.gitkeep"
      assert_not_file "$variant_dir/ontology/.gitkeep"
      ;;
    owned)
      assert_contains "$variant_dir/contracts/layer-contract.yml" "governance_model: org-baseline-plus-project-overlay" "owned archetype must set overlay governance model"
      assert_file "$variant_dir/docs/project/foundation.md"
      assert_file "$variant_dir/docs/project/governance_overlay.md"
      assert_file "$variant_dir/docs/org_context/operating_model.md"
      assert_file "$variant_dir/src/.gitkeep"
      assert_file "$variant_dir/tests/.gitkeep"
      assert_file "$variant_dir/ontology/manifest.yaml"
      assert_not_file "$variant_dir/prompts/activities/.gitkeep"
      assert_not_file "$variant_dir/docs/person/.gitkeep"
      assert_not_file "$variant_dir/docs/registers/.gitkeep"
      assert_not_file "$variant_dir/governance/consent.md"
      ;;
  esac

  (
    cd "$variant_dir"
    ./scripts/ci/smoke.sh >/dev/null
  )
done

(
  cd "$l2_dir"
  git init -b main >/dev/null
  git config user.name "l1-template ci" >/dev/null
  git config user.email "ci@l1-template.local" >/dev/null
  git add .
  git commit -m "initial L2 render" >/dev/null
  ./scripts/install-hooks.sh >/dev/null
  hooks_path="$(git config --get core.hooksPath || true)"
  [ "$hooks_path" = ".githooks" ] || fail "generated L2 expected core.hooksPath=.githooks"
  ./scripts/ci/smoke.sh >/dev/null
)

./scripts/new-repo-from-copier.sh template-repo "$l2_dir" \
  -d repo_slug=l2-sample \
  --defaults --overwrite >/dev/null

(
  cd "$l2_dir"
  if [ -n "$(git status --porcelain)" ]; then
    echo "error: non-idempotent L1 -> L2 generation" >&2
    git status --short >&2
    exit 1
  fi
)

echo "ok: template ci"
