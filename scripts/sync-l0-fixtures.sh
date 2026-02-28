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
need_cmd mkdir
need_cmd mktemp
need_cmd mv
need_cmd rm
need_cmd tail

SYNC_VERBOSE="${SYNC_VERBOSE:-0}"

run_step() {
  if [ "$SYNC_VERBOSE" = "1" ]; then
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

fixture_normalization_lib="$repo_root/scripts/lib/fixture-normalization.sh"
[ -f "$fixture_normalization_lib" ] || {
  echo "error: missing required helper: $fixture_normalization_lib" >&2
  exit 1
}
# shellcheck source=/dev/null
. "$fixture_normalization_lib"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

l1_render="$tmp_root/l1-template-repo"
l2_render_project="$tmp_root/l2-tpl-project-repo"
l2_render_monorepo="$tmp_root/l2-tpl-monorepo"
l2_render_package="$tmp_root/l2-tpl-package"

run_step "$repo_root/scripts/new-l1-from-copier.sh" "$l1_render" \
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
  cd "$l1_render"
  run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$l2_render_project" \
    -d repo_slug=fixture-product-repo \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-monorepo "$l2_render_monorepo" \
    -d repo_slug=fixture-monorepo \
    -d language=python \
    -d package_manager=uv \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

  run_step ./scripts/new-repo-from-copier.sh tpl-package "$l2_render_package" \
    -d package_name=fixture-core \
    -d package_type=library \
    -d language=python \
    --defaults --overwrite
)

fixtures_root="$repo_root/fixtures"
fixture_l1="$fixtures_root/l1/template-repo"
fixture_l2_project="$fixtures_root/l2/tpl-project-repo"
fixture_l2_monorepo="$fixtures_root/l2/tpl-monorepo"
fixture_l2_package="$fixtures_root/l2/tpl-package"

rm -rf "$fixture_l1" "$fixture_l2_project" "$fixture_l2_monorepo" "$fixture_l2_package"
mkdir -p "$fixture_l1" "$fixture_l2_project" "$fixture_l2_monorepo" "$fixture_l2_package"

cp -R "$l1_render/." "$fixture_l1/"
cp -R "$l2_render_project/." "$fixture_l2_project/"
cp -R "$l2_render_monorepo/." "$fixture_l2_monorepo/"
cp -R "$l2_render_package/." "$fixture_l2_package/"

normalize_fixture_tree_volatiles "$fixture_l1"
normalize_fixture_tree_volatiles "$fixture_l2_project"
normalize_fixture_tree_volatiles "$fixture_l2_monorepo"
normalize_fixture_tree_volatiles "$fixture_l2_package"

echo "ok: fixtures synchronized"
echo "  - $fixture_l1"
echo "  - $fixture_l2_project"
echo "  - $fixture_l2_monorepo"
echo "  - $fixture_l2_package"
