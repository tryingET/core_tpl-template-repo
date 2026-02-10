#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"

deep=0
case "${1:-}" in
  "") ;;
  --deep) deep=1 ;;
  *)
    echo "usage: full.sh [--deep]" >&2
    exit 2
    ;;
esac

"$repo_root/scripts/ci/smoke.sh"

if [ "$deep" -eq 1 ]; then
  "$repo_root/scripts/check-template-ci.sh"
fi

echo "ok: ci full"
