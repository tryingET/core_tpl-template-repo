#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF' >&2
usage: preview-l1-diff.sh <target-l1-repo-path> [repo-slug]

Renders a fresh L1 repo from this L0 into a temp directory and shows
non-destructive diff against the target L1 repository.
EOF
}

target_repo="${1:-}"
repo_slug="${2:-}"

if [ -z "$target_repo" ]; then
  usage
  exit 2
fi

if [ ! -d "$target_repo" ]; then
  echo "error: target repo path does not exist: $target_repo" >&2
  exit 2
fi

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: missing dependency: $1" >&2
    exit 2
  }
}

need_cmd basename
need_cmd git
need_cmd mktemp

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

if [ -z "$repo_slug" ]; then
  repo_slug="$(basename "$target_repo")"
fi

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

render_dir="$tmp_root/l1-render"

"$repo_root/scripts/new-l1-from-copier.sh" template-repo "$render_dir" \
  -d repo_slug="$repo_slug" \
  --defaults --overwrite >/dev/null

echo "==> rendered: $render_dir"
echo "==> target:   $target_repo"

if git -C "$target_repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ -n "$(git -C "$target_repo" status --porcelain)" ]; then
    echo "warning: target repo has uncommitted changes; diff may include local edits" >&2
  fi
fi

set +e
git --no-pager diff --no-index -- "$render_dir" "$target_repo"
status=$?
set -e

# git diff --no-index exits 1 when differences are found.
if [ "$status" -gt 1 ]; then
  echo "error: diff command failed" >&2
  exit "$status"
fi

if [ "$status" -eq 0 ]; then
  echo "ok: no diff between rendered L1 and target"
else
  echo "info: differences detected (expected during adoption)"
fi
