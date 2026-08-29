#!/bin/sh
set -eu

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "error: not a git repository" >&2
  exit 2
}
exec python3 "$repo_root/scripts/lib/propagate_template.py" --repo-root "$repo_root" "$@"
