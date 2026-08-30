#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF' >&2
usage:
  propagate-l1-template.sh <target> [repo-slug] --bootstrap-map --evidence-ref REF --apply
  propagate-l1-template.sh <target> [repo-slug] --plan-sha256 SHA --wave-id ID --apply
  propagate-l1-template.sh <target> [repo-slug] --finalize-task AK-ID --plan-artifact PATH --apply

Explicit mutation entry point. Apply writes state=applied_pending_receipt; after
that target commit passes validation and receives target-repo AK evidence, the
finalize form verifies the external receipt before establishing ownership.
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
apply=""
evidence_ref=""
plan_sha256=""
wave_id=""
finalize_task=""
plan_artifact=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --bootstrap-map) bootstrap="--bootstrap-map"; shift ;;
    --apply) apply=1; shift ;;
    --evidence-ref|--plan-sha256|--wave-id|--finalize-task|--plan-artifact)
      [ "$#" -ge 2 ] || { usage; exit 2; }
      case "$1" in
        --evidence-ref) evidence_ref="$2" ;;
        --plan-sha256) plan_sha256="$2" ;;
        --wave-id) wave_id="$2" ;;
        --finalize-task) finalize_task="$2" ;;
        --plan-artifact) plan_artifact="$2" ;;
      esac
      shift 2
      ;;
    *) usage; exit 2 ;;
  esac
done
[ "$apply" = "1" ] || { echo "error: mutation requires explicit --apply" >&2; exit 2; }

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
if [ -n "$(git -C "$repo_root" status --porcelain)" ]; then
  echo "error: L1 mutation requires a clean L0 worktree at an exact commit" >&2
  exit 2
fi
source_l0_commit="$(git -C "$repo_root" rev-parse HEAD)"

python_exec=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'pass' >/dev/null 2>&1; then
    python_exec="$candidate"
    break
  fi
done
[ -n "$python_exec" ] || { echo "error: missing functional python3 or python" >&2; exit 2; }
engine="$repo_root/scripts/lib/l1_template_ownership.py"

if [ -n "$finalize_task" ]; then
  [ -z "$bootstrap$evidence_ref$plan_sha256$wave_id" ] || { usage; exit 2; }
  [ -n "$plan_artifact" ] || { usage; exit 2; }
  exec "$python_exec" "$engine" --repo-root "$target" \
    --finalize-task "$finalize_task" --plan-artifact "$plan_artifact"
fi
[ -z "$plan_artifact" ] || { usage; exit 2; }

if [ "$bootstrap" = "--bootstrap-map" ]; then
  [ -n "$evidence_ref" ] || { echo "error: bootstrap requires --evidence-ref" >&2; exit 2; }
  [ -z "$plan_sha256$wave_id" ] || { usage; exit 2; }
else
  [ -z "$evidence_ref" ] || { usage; exit 2; }
  [ -n "$plan_sha256" ] && [ -n "$wave_id" ] || {
    echo "error: apply requires --plan-sha256 and --wave-id" >&2
    exit 2
  }
fi

exec "$repo_root/scripts/lib/run-l1-template-refresh.sh" \
  "$target" "$repo_slug" "$bootstrap" --apply "$evidence_ref" \
  "$plan_sha256" "$wave_id" "$source_l0_commit"
