#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$repo_root"

fail() {
  echo "error: $*" >&2
  exit 1
}

assert_file() {
  path="$1"
  [ -f "$path" ] || fail "missing required release file: $path"
}

assert_contains() {
  path="$1"
  needle="$2"
  grep -qF -- "$needle" "$path" || fail "missing '$needle' in $path"
}

assert_file .release-please-config.json
assert_file .release-please-manifest.json
assert_file CHANGELOG.md
assert_file SECURITY.md

assert_contains .release-please-config.json '"release-type": "simple"'
assert_contains .release-please-config.json '"include-v-in-tag": true'
assert_contains .release-please-manifest.json '".": "0.1.0"'
assert_contains CHANGELOG.md '## [0.1.0]'

echo "ok: release baseline check"
