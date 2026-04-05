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
expected_l2_agent="$repo_root/fixtures/l2/tpl-agent-repo"
expected_l2_org="$repo_root/fixtures/l2/tpl-org-repo"
expected_l2_project="$repo_root/fixtures/l2/tpl-project-repo"
expected_l2_monorepo="$repo_root/fixtures/l2/tpl-monorepo"
expected_l2_package="$repo_root/fixtures/l2/tpl-package"
expected_matrix_project_python="$repo_root/fixtures/matrix/tpl-project-repo/python"
expected_matrix_project_rust="$repo_root/fixtures/matrix/tpl-project-repo/rust"
expected_matrix_project_elixir="$repo_root/fixtures/matrix/tpl-project-repo/elixir"
expected_matrix_monorepo_root="$repo_root/fixtures/matrix/tpl-monorepo/root"

[ -d "$expected_l1" ] || fail "missing fixture directory: $expected_l1"
[ -d "$expected_l2_agent" ] || fail "missing fixture directory: $expected_l2_agent"
[ -d "$expected_l2_org" ] || fail "missing fixture directory: $expected_l2_org"
[ -d "$expected_l2_project" ] || fail "missing fixture directory: $expected_l2_project"
[ -d "$expected_l2_monorepo" ] || fail "missing fixture directory: $expected_l2_monorepo"
[ -d "$expected_l2_package" ] || fail "missing fixture directory: $expected_l2_package"
[ -d "$expected_matrix_project_python" ] || fail "missing fixture directory: $expected_matrix_project_python"
[ -d "$expected_matrix_project_rust" ] || fail "missing fixture directory: $expected_matrix_project_rust"
[ -d "$expected_matrix_project_elixir" ] || fail "missing fixture directory: $expected_matrix_project_elixir"
[ -d "$expected_matrix_monorepo_root" ] || fail "missing fixture directory: $expected_matrix_monorepo_root"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

actual_l1="$tmp_root/l1-template-repo"
actual_l2_agent="$tmp_root/l2-tpl-agent-repo"
actual_l2_org="$tmp_root/l2-tpl-org-repo"
actual_l2_project="$tmp_root/l2-tpl-project-repo"
actual_l2_monorepo="$tmp_root/l2-tpl-monorepo"
actual_l2_package="$tmp_root/l2-tpl-package"
actual_matrix_project_python="$tmp_root/matrix-tpl-project-repo-python"
actual_matrix_project_rust="$tmp_root/matrix-tpl-project-repo-rust"
actual_matrix_project_elixir="$tmp_root/matrix-tpl-project-repo-elixir"
actual_matrix_monorepo_root="$tmp_root/matrix-tpl-monorepo-root"

run_step "$repo_root/scripts/new-l1-from-copier.sh" "$actual_l1" \
  -d repo_slug=fixture-template-repo \
  -d company_slug=holdingco \
  -d company_name="Holding Company" \
  -d maintainer_handle=@template-owner \
  -d l1_org_docs_profile=rich \
  -d enable_community_pack=false \
  -d enable_release_pack=false \
  -d enable_vouch_gate=false \
  --defaults --overwrite

(
  cd "$actual_l1"

  run_step ./scripts/new-repo-from-copier.sh tpl-agent-repo "$actual_l2_agent" \
    -d repo_slug=fixture-agent \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-org-repo "$actual_l2_org" \
    -d repo_slug=fixture-org \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$actual_l2_project" \
    -d repo_slug=fixture-product-repo \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-monorepo "$actual_l2_monorepo" \
    -d repo_slug=fixture-monorepo \
    -d package_manager=uv \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-package "$actual_l2_package" \
    -d package_name=fixture-core \
    -d package_type=library \
    -d language=python \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$actual_matrix_project_python" \
    -d repo_slug=fixture-project-python \
    -d language=python \
    -d enable_software_pack=true \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$actual_matrix_project_rust" \
    -d repo_slug=fixture-project-rust \
    -d language=rust \
    -d enable_software_pack=true \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$actual_matrix_project_elixir" \
    -d repo_slug=fixture-project-elixir \
    -d language=elixir \
    -d enable_software_pack=true \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-monorepo "$actual_matrix_monorepo_root" \
    -d repo_slug=fixture-monorepo-matrix \
    -d package_manager=uv \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-package "$actual_matrix_monorepo_root/packages/fixture-py-core" \
    -d package_name=fixture-py-core \
    -d package_type=library \
    -d language=python \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-package "$actual_matrix_monorepo_root/packages/fixture-ts-core" \
    -d package_name=fixture-ts-core \
    -d package_type=library \
    -d language=typescript \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-package "$actual_matrix_monorepo_root/packages/fixture-rust-core" \
    -d package_name=fixture-rust-core \
    -d package_type=library \
    -d language=rust \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-package "$actual_matrix_monorepo_root/packages/fixture-elixir-core" \
    -d package_name=fixture-elixir-core \
    -d package_type=library \
    -d language=elixir \
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
compare_expected_l2_agent="$tmp_root/compare/expected-l2-agent"
compare_actual_l2_agent="$tmp_root/compare/actual-l2-agent"
compare_expected_l2_org="$tmp_root/compare/expected-l2-org"
compare_actual_l2_org="$tmp_root/compare/actual-l2-org"
compare_expected_l2_project="$tmp_root/compare/expected-l2-project"
compare_actual_l2_project="$tmp_root/compare/actual-l2-project"
compare_expected_l2_monorepo="$tmp_root/compare/expected-l2-monorepo"
compare_actual_l2_monorepo="$tmp_root/compare/actual-l2-monorepo"
compare_expected_l2_package="$tmp_root/compare/expected-l2-package"
compare_actual_l2_package="$tmp_root/compare/actual-l2-package"
compare_expected_matrix_project_python="$tmp_root/compare/expected-matrix-project-python"
compare_actual_matrix_project_python="$tmp_root/compare/actual-matrix-project-python"
compare_expected_matrix_project_rust="$tmp_root/compare/expected-matrix-project-rust"
compare_actual_matrix_project_rust="$tmp_root/compare/actual-matrix-project-rust"
compare_expected_matrix_project_elixir="$tmp_root/compare/expected-matrix-project-elixir"
compare_actual_matrix_project_elixir="$tmp_root/compare/actual-matrix-project-elixir"
compare_expected_matrix_monorepo_root="$tmp_root/compare/expected-matrix-monorepo-root"
compare_actual_matrix_monorepo_root="$tmp_root/compare/actual-matrix-monorepo-root"

prepare_compare_tree "$expected_l1" "$compare_expected_l1"
prepare_compare_tree "$actual_l1" "$compare_actual_l1"
prepare_compare_tree "$expected_l2_agent" "$compare_expected_l2_agent"
prepare_compare_tree "$actual_l2_agent" "$compare_actual_l2_agent"
prepare_compare_tree "$expected_l2_org" "$compare_expected_l2_org"
prepare_compare_tree "$actual_l2_org" "$compare_actual_l2_org"
prepare_compare_tree "$expected_l2_project" "$compare_expected_l2_project"
prepare_compare_tree "$actual_l2_project" "$compare_actual_l2_project"
prepare_compare_tree "$expected_l2_monorepo" "$compare_expected_l2_monorepo"
prepare_compare_tree "$actual_l2_monorepo" "$compare_actual_l2_monorepo"
prepare_compare_tree "$expected_l2_package" "$compare_expected_l2_package"
prepare_compare_tree "$actual_l2_package" "$compare_actual_l2_package"
prepare_compare_tree "$expected_matrix_project_python" "$compare_expected_matrix_project_python"
prepare_compare_tree "$actual_matrix_project_python" "$compare_actual_matrix_project_python"
prepare_compare_tree "$expected_matrix_project_rust" "$compare_expected_matrix_project_rust"
prepare_compare_tree "$actual_matrix_project_rust" "$compare_actual_matrix_project_rust"
prepare_compare_tree "$expected_matrix_project_elixir" "$compare_expected_matrix_project_elixir"
prepare_compare_tree "$actual_matrix_project_elixir" "$compare_actual_matrix_project_elixir"
prepare_compare_tree "$expected_matrix_monorepo_root" "$compare_expected_matrix_monorepo_root"
prepare_compare_tree "$actual_matrix_monorepo_root" "$compare_actual_matrix_monorepo_root"

compare_tree "$compare_expected_l1" "$compare_actual_l1" "L1 fixture"
compare_tree "$compare_expected_l2_agent" "$compare_actual_l2_agent" "L2 agent fixture"
compare_tree "$compare_expected_l2_org" "$compare_actual_l2_org" "L2 org fixture"
compare_tree "$compare_expected_l2_project" "$compare_actual_l2_project" "L2 project fixture"
compare_tree "$compare_expected_l2_monorepo" "$compare_actual_l2_monorepo" "L2 monorepo fixture"
compare_tree "$compare_expected_l2_package" "$compare_actual_l2_package" "L2 package fixture"
compare_tree "$compare_expected_matrix_project_python" "$compare_actual_matrix_project_python" "project-language matrix python"
compare_tree "$compare_expected_matrix_project_rust" "$compare_actual_matrix_project_rust" "project-language matrix rust"
compare_tree "$compare_expected_matrix_project_elixir" "$compare_actual_matrix_project_elixir" "project-language matrix elixir"
compare_tree "$compare_expected_matrix_monorepo_root" "$compare_actual_matrix_monorepo_root" "monorepo-language matrix root"

echo "ok: l0 fixtures"
