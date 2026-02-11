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

need_cmd cp
need_cmd mkdir
need_cmd mktemp
need_cmd rm

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

l1_render="$tmp_root/l1-template-repo"
l2_render="$tmp_root/l2-template-repo"

"$repo_root/scripts/new-l1-from-copier.sh" template-repo "$l1_render" \
  -d repo_slug=fixture-template-repo \
  -d maintainer_handle=@template-owner \
  -d l1_org_docs_profile=rich \
  -d l2_org_docs_default=compact \
  -d enable_community_pack=false \
  -d enable_release_pack=false \
  -d enable_vouch_gate=false \
  --defaults --overwrite >/dev/null

(
  cd "$l1_render"
  ./scripts/new-repo-from-copier.sh template-repo "$l2_render" \
    -d repo_slug=fixture-product-repo \
    -d owner_handle=@repo-owner \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite >/dev/null
)

fixtures_root="$repo_root/fixtures"
fixture_l1="$fixtures_root/l1/template-repo"
fixture_l2="$fixtures_root/l2/template-repo"

rm -rf "$fixture_l1" "$fixture_l2"
mkdir -p "$fixture_l1" "$fixture_l2"

cp -R "$l1_render/." "$fixture_l1/"
cp -R "$l2_render/." "$fixture_l2/"

echo "ok: fixtures synchronized"
echo "  - $fixture_l1"
echo "  - $fixture_l2"
