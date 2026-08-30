#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF' >&2
usage: preview-l1-diff.sh <target> [repo-slug] [--bootstrap-map] [--evidence-ref REF]

Renders a fresh L1 repo and emits a non-destructive ownership-aware plan.
This entry point cannot apply changes.
EOF
}

target="${1:-}"
[ -n "$target" ] || { usage; exit 2; }
shift
repo_slug=""
case "${1:-}" in
"" | --*) ;;
*) repo_slug="$1"; shift ;;
esac

bootstrap=""
evidence_ref=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --bootstrap-map) bootstrap="--bootstrap-map"; shift ;;
    --evidence-ref)
      [ "$#" -ge 2 ] || { usage; exit 2; }
      evidence_ref="$2"; shift 2
      ;;
    *) usage; exit 2 ;;
  esac
done
if [ -n "$evidence_ref" ] && [ -z "$bootstrap" ]; then
  echo "error: --evidence-ref is valid only with --bootstrap-map" >&2
  exit 2
fi

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
exec "$repo_root/scripts/lib/run-l1-template-refresh.sh" \
  "$target" "$repo_slug" "$bootstrap" "" "$evidence_ref"
