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
copier.yml
.github/pull_request_template.md
docs/release-compatibility-policy.md
docs/l1-adoption-playbook.md
copier-template/README.md.jinja
copier-template/AGENTS.md
copier-template/contracts/layer-contract.yml
copier-template/scripts/new-repo-from-copier.sh
copier-template/scripts/check-template-ci.sh
copier-template/scripts/install-hooks.sh
copier-template/scripts/ci/smoke.sh
copier-template/scripts/ci/full.sh
copier-template/.github/workflows/template-check.yml
copier-template/.githooks/pre-commit
copier-template/.githooks/pre-push
copier-template/copier/template-repo/copier.yml
copier-template/copier/template-repo/README.md.jinja
copier-template/copier/template-repo/AGENTS.md
copier-template/copier/template-repo/contracts/layer-contract.yml
copier-template/copier/template-repo/scripts/install-hooks.sh
copier-template/copier/template-repo/scripts/ci/smoke.sh
copier-template/copier/template-repo/scripts/ci/full.sh
copier-template/copier/template-repo/.githooks/pre-commit
copier-template/copier/template-repo/.githooks/pre-push
scripts/preview-l1-diff.sh
"

for path in $required_files; do
  assert_file "$path"
done

required_exec="
scripts/preview-l1-diff.sh
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

for path in $required_exec; do
  assert_exec "$path"
done

assert_contains "copier.yml" "_subdirectory: copier-template" "L0 copier source must target copier-template/"
assert_contains "copier.yml" "- template-repo" "L0 must expose the template-repo profile"
assert_contains "CODEOWNERS" "/copier-template/**" "CODEOWNERS must protect copier-template/"
assert_contains ".github/pull_request_template.md" "check-l0-guardrails.sh" "PR template must require guardrail checks"
assert_contains ".github/pull_request_template.md" "check-l0-generation.sh" "PR template must require generation checks"

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

if grep -nE 'copier[[:space:]]+(copy|update)' copier.yml copier-template/copier/template-repo/copier.yml >/dev/null 2>&1; then
  fail "nested copier invocations are not allowed in template config files"
fi

echo "ok: l0 guardrails"
