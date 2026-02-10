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

fail() {
  echo "error: $*" >&2
  exit 1
}

expected_l1="$repo_root/fixtures/l1/template-repo"
expected_l2="$repo_root/fixtures/l2/template-repo"

[ -d "$expected_l1" ] || fail "missing fixture directory: $expected_l1"
[ -d "$expected_l2" ] || fail "missing fixture directory: $expected_l2"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

actual_l1="$tmp_root/l1-template-repo"
actual_l2="$tmp_root/l2-template-repo"

"$repo_root/scripts/new-l1-from-copier.sh" template-repo "$actual_l1" \
  -d repo_slug=fixture-template-repo \
  -d maintainer_handle=@template-owner \
  -d enable_community_pack=false \
  -d enable_release_pack=false \
  -d enable_vouch_gate=false \
  --defaults --overwrite >/dev/null

(
  cd "$actual_l1"
  ./scripts/new-repo-from-copier.sh template-repo "$actual_l2" \
    -d repo_slug=fixture-product-repo \
    -d owner_handle=@repo-owner \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite >/dev/null
)

sanitize_answers_tree() {
  tree="$1"

  find "$tree" -type f -name '.copier-answers.yml' | while IFS= read -r answers_file; do
    sanitized_file="${answers_file}.sanitized"
    awk '
      !/^_commit:/ &&
      !/^_src_path:/
    ' "$answers_file" > "$sanitized_file"
    mv "$sanitized_file" "$answers_file"
  done
}

prepare_compare_tree() {
  src="$1"
  dst="$2"
  rm -rf "$dst"
  mkdir -p "$dst"
  cp -R "$src/." "$dst/"
  sanitize_answers_tree "$dst"
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
compare_expected_l2="$tmp_root/compare/expected-l2"
compare_actual_l2="$tmp_root/compare/actual-l2"

prepare_compare_tree "$expected_l1" "$compare_expected_l1"
prepare_compare_tree "$actual_l1" "$compare_actual_l1"
prepare_compare_tree "$expected_l2" "$compare_expected_l2"
prepare_compare_tree "$actual_l2" "$compare_actual_l2"

compare_tree "$compare_expected_l1" "$compare_actual_l1" "L1 fixture"
compare_tree "$compare_expected_l2" "$compare_actual_l2" "L2 fixture"

echo "ok: l0 fixtures"
