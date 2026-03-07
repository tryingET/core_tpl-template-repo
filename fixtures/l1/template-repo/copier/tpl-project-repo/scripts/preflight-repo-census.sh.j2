#!/usr/bin/env bash
set -euo pipefail

# Deterministic repo census fallback for environments without ~/.pi/agent/scripts/preflight-repo-census.sh
# Usage: ./scripts/preflight-repo-census.sh [scope]

SCOPE="${1:-.}"

if [ ! -d "$SCOPE" ]; then
  echo "error: scope not found: $SCOPE" >&2
  exit 1
fi

mapfile -t REPOS < <(find "$SCOPE" -mindepth 1 -maxdepth 5 -type d -name .git -printf '%h\n' | sort)

repo_count="$(printf '%s\n' "${REPOS[@]-}" | sed '/^$/d' | wc -l | tr -d ' ')"
if [ "${repo_count:-0}" -eq 0 ] && [ -d "$SCOPE/.git" ]; then
  REPOS=("$SCOPE")
  repo_count=1
fi

echo "scope: $SCOPE"
echo "repos: ${repo_count:-0}"
echo
printf '%-45s %-28s %-8s\n' "REPO" "BRANCH" "DIRTY"
printf '%-45s %-28s %-8s\n' "----" "------" "-----"

for repo in "${REPOS[@]}"; do
  if ! git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
    printf '%-45s %-28s %-8s\n' "$repo" "(not-git)" "n/a"
    continue
  fi

  branch="$(git -C "$repo" branch --show-current 2>/dev/null || true)"
  [ -n "$branch" ] || branch="(detached)"

  dirty_count="$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  dirty="clean"
  if [ "${dirty_count:-0}" -gt 0 ]; then
    dirty="dirty:$dirty_count"
  fi

  printf '%-45s %-28s %-8s\n' "$repo" "$branch" "$dirty"
done
