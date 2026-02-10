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

required_files="
README.md
AGENTS.md
contracts/layer-contract.yml
scripts/new-repo-from-copier.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.github/workflows/template-check.yml
.github/workflows/ci.yml
.githooks/pre-commit
.githooks/pre-push
copier/template-repo/copier.yml
"

for path in $required_files; do
  assert_file "$path"
done

required_exec="
scripts/new-repo-from-copier.sh
scripts/check-template-ci.sh
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.githooks/pre-commit
.githooks/pre-push
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

contract="contracts/layer-contract.yml"
assert_contains "$contract" "layer: L1" "L1 contract layer mismatch"
assert_contains "$contract" "L0 -> L1" "L1 contract must include L0 -> L1"
assert_contains "$contract" "L1 -> L2" "L1 contract must include L1 -> L2"
assert_contains "$contract" "L1 -> L0" "L1 contract must include forbidden reverse edge"
assert_contains "$contract" "L2 -> L1" "L1 contract must include forbidden reverse edge"
assert_contains "$contract" "nested_copier_tasks_allowed: false" "L1 contract must forbid nested copier tasks"

workflow=".github/workflows/template-check.yml"
assert_contains "$workflow" "pull_request:" "template-check workflow must run on pull requests"
assert_contains "$workflow" "push:" "template-check workflow must run on pushes"
assert_contains "$workflow" "./scripts/check-template-ci.sh" "template-check workflow must run template checks"

assert_contains ".githooks/pre-commit" "scripts/ci/smoke.sh" "pre-commit must run smoke lane"
assert_contains ".githooks/pre-push" "scripts/ci/full.sh" "pre-push must run full lane"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

l2_dir="$tmp_root/l2-sample"
./scripts/new-repo-from-copier.sh template-repo "$l2_dir" \
  -d repo_slug=l2-sample \
  --defaults --overwrite >/dev/null

l2_required_files="
README.md
AGENTS.md
contracts/layer-contract.yml
scripts/install-hooks.sh
scripts/ci/smoke.sh
scripts/ci/full.sh
.githooks/pre-commit
.githooks/pre-push
.github/workflows/ci.yml
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
assert_contains "$l2_dir/contracts/layer-contract.yml" "layer: L2" "generated L2 contract layer mismatch"
assert_contains "$l2_dir/contracts/layer-contract.yml" "L2 -> L1" "generated L2 contract must forbid reverse edge"

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
