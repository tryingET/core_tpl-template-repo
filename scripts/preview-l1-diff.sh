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
need_cmd cp
need_cmd git
need_cmd mkdir
need_cmd mktemp
need_cmd rm

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

read_answer_value() {
  file="$1"
  key="$2"

  [ -f "$file" ] || return 1

  awk -v key="$key" '
    $0 ~ "^[[:space:]]*" key "[[:space:]]*:" {
      v = $0
      sub("^[[:space:]]*" key "[[:space:]]*:[[:space:]]*", "", v)
      gsub(/^[ \t]+|[ \t]+$/, "", v)
      sub(/[[:space:]]+#.*$/, "", v)
      if (v ~ /^".*"$/) {
        v = substr(v, 2, length(v) - 2)
      } else if (v ~ /^\047.*\047$/) {
        v = substr(v, 2, length(v) - 2)
      }
      print v
      exit
    }
  ' "$file"
}

answers_file="$target_repo/.copier-answers.yml"

if [ -z "$repo_slug" ] && [ -f "$answers_file" ]; then
  repo_slug_from_answers="$(read_answer_value "$answers_file" repo_slug || true)"
  if [ -n "$repo_slug_from_answers" ]; then
    repo_slug="$repo_slug_from_answers"
  fi
fi

if [ -z "$repo_slug" ]; then
  repo_slug="$(basename "$target_repo")"
fi

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

render_dir="$tmp_root/l1-render"

set -- --defaults --overwrite

if [ -f "$answers_file" ]; then
  for key in company_slug company_name maintainer_handle l1_org_docs_profile enable_vouch_gate enable_community_pack enable_release_pack; do
    value="$(read_answer_value "$answers_file" "$key" || true)"
    if [ -n "$value" ]; then
      set -- "$@" -d "$key=$value"
    fi
  done
fi

set -- "$@" -d "repo_slug=$repo_slug"

"$repo_root/scripts/new-l1-from-copier.sh" "$render_dir" "$@" >/dev/null

echo "==> rendered: $render_dir"
echo "==> target:   $target_repo"

if git -C "$target_repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ -n "$(git -C "$target_repo" status --porcelain)" ]; then
    echo "warning: target repo has uncommitted changes; diff may include local edits" >&2
  fi
fi

compare_render_dir="$tmp_root/l1-render-compare"
compare_target_dir="$tmp_root/l1-target-compare"
mkdir -p "$compare_render_dir" "$compare_target_dir"
cp -R "$render_dir/." "$compare_render_dir/"
cp -R "$target_repo/." "$compare_target_dir/"
rm -rf "$compare_render_dir/.git" "$compare_target_dir/.git"

set +e
git --no-pager diff --no-index -- "$compare_render_dir" "$compare_target_dir"
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
