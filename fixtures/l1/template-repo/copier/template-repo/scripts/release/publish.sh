#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$repo_root"

fail() {
  echo "error: $*" >&2
  exit 1
}

tag_name="${TAG_NAME:-}"
[ -n "$tag_name" ] || fail "TAG_NAME is required"

case "$tag_name" in
  v*) ;;
  *) fail "release tag must start with 'v'" ;;
esac

mkdir -p dist
archive_path="dist/source-${tag_name}.tar.gz"

git rev-parse --verify "$tag_name" >/dev/null 2>&1 || fail "tag not found: $tag_name"
git archive --format=tar.gz --output "$archive_path" "$tag_name"

echo "ok: built release artifact $archive_path"
