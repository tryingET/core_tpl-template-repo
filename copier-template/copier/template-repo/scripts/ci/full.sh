#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"

case "${1:-}" in
  ""|--deep) ;;
  *)
    echo "usage: full.sh [--deep]" >&2
    exit 2
    ;;
esac

"$repo_root/scripts/ci/smoke.sh"

echo "ok: ci full"
