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
need_cmd cp
need_cmd find
need_cmd git
need_cmd mkdir
need_cmd mktemp
need_cmd mv
need_cmd rm
need_cmd tail

CHECK_FIXTURES_VERBOSE="${CHECK_FIXTURES_VERBOSE:-0}"

run_step() {
  if [ "$CHECK_FIXTURES_VERBOSE" = "1" ]; then
    "$@"
    return
  fi

  log_file="$(mktemp)"
  if "$@" >"$log_file" 2>&1; then
    rm -f "$log_file"
    return
  fi

  echo "error: command failed: $*" >&2
  echo "--- last 200 lines ---" >&2
  tail -n 200 "$log_file" >&2 || true
  rm -f "$log_file"
  return 1
}

fail() {
  echo "error: $*" >&2
  exit 1
}

fixture_normalization_lib="$repo_root/scripts/lib/fixture-normalization.sh"
[ -f "$fixture_normalization_lib" ] || fail "missing required helper: $fixture_normalization_lib"
# shellcheck source=/dev/null
. "$fixture_normalization_lib"

expected_l1="$repo_root/fixtures/l1/template-repo"
expected_l2_project="$repo_root/fixtures/l2/tpl-project-repo"
expected_l2_individual="$repo_root/fixtures/l2/tpl-individual-repo"

[ -d "$expected_l1" ] || fail "missing fixture directory: $expected_l1"
[ -d "$expected_l2_project" ] || fail "missing fixture directory: $expected_l2_project"
[ -d "$expected_l2_individual" ] || fail "missing fixture directory: $expected_l2_individual"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

actual_l1="$tmp_root/l1-template-repo"
actual_l2_project="$tmp_root/l2-tpl-project-repo"
actual_l2_individual="$tmp_root/l2-tpl-individual-repo"

run_step "$repo_root/scripts/new-l1-from-copier.sh" "$actual_l1" \
  -d repo_slug=fixture-template-repo \
  -d maintainer_handle=@template-owner \
  -d l1_org_docs_profile=rich \
  -d enable_community_pack=false \
  -d enable_release_pack=false \
  -d enable_vouch_gate=false \
  --defaults --overwrite

(
  cd "$actual_l1"
  run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$actual_l2_project" \
    -d repo_slug=fixture-product-repo \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite
  run_step ./scripts/new-repo-from-copier.sh tpl-individual-repo "$actual_l2_individual" \
    -d repo_slug=fixture-individual-repo \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite
)

prepare_compare_tree() {
  src="$1"
  dst="$2"
  rm -rf "$dst"
  mkdir -p "$dst"
  cp -R "$src/." "$dst/"
  normalize_fixture_tree_volatiles "$dst"
}

compare_tree() {
  expected="$1"
  actual="$2"
  label="$3"

  set +e
  git diff --no-index --quiet -- "$expected" "$actual"
  status=$?
  set -e

  if [ "$status" -eq 0 ]; then
    return
  fi
  if [ "$status" -eq 1 ]; then
    echo "error: fixture drift detected for $label" >&2
    git --no-pager diff --no-index -- "$expected" "$actual" >&2 || true
    echo "hint: run 'bash ./scripts/sync-l0-fixtures.sh' and commit fixture updates" >&2
    exit 1
  fi

  fail "diff command failed while checking $label"
}

compare_expected_l1="$tmp_root/compare/expected-l1"
compare_actual_l1="$tmp_root/compare/actual-l1"
compare_expected_l2_project="$tmp_root/compare/expected-l2-project"
compare_actual_l2_project="$tmp_root/compare/actual-l2-project"
compare_expected_l2_individual="$tmp_root/compare/expected-l2-individual"
compare_actual_l2_individual="$tmp_root/compare/actual-l2-individual"

prepare_compare_tree "$expected_l1" "$compare_expected_l1"
prepare_compare_tree "$actual_l1" "$compare_actual_l1"
prepare_compare_tree "$expected_l2_project" "$compare_expected_l2_project"
prepare_compare_tree "$actual_l2_project" "$compare_actual_l2_project"
prepare_compare_tree "$expected_l2_individual" "$compare_expected_l2_individual"
prepare_compare_tree "$actual_l2_individual" "$compare_actual_l2_individual"

compare_tree "$compare_expected_l1" "$compare_actual_l1" "L1 fixture"
compare_tree "$compare_expected_l2_project" "$compare_actual_l2_project" "L2 project fixture"
compare_tree "$compare_expected_l2_individual" "$compare_actual_l2_individual" "L2 individual fixture"

echo "ok: l0 fixtures"
