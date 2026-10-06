#!/bin/sh
# Optional observation only; default commands and all unittest arguments are retained.
set -eu
root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
cohort="$1"
runtime="$2"
shift 2
case "$cohort" in
    ''|*[!a-zA-Z0-9_.-]*|.|..) echo 'error: invalid profile cohort' >&2; exit 2 ;;
esac
profile="${L0_PROFILE_DIR:-}"
if [ -n "$profile" ]; then
    export PYTHONDONTWRITEBYTECODE=1
    L0_PROFILE_PARENT="${L0_PROFILE_COHORT:-}"
    L0_PROFILE_COHORT="$cohort"
    export L0_PROFILE_PARENT L0_PROFILE_COHORT
    set -- "$root/tests/ci_profile.py" --cohort "$cohort" --out "$profile/$cohort-$$.json" -- "$@"
else
    set -- -m unittest "$@"
fi
case "$runtime" in
    pinned) exec uvx --from "copier==${COPIER_VERSION:-9.11.1}" python -B "$@" ;;
    pinned-9.11.1) exec uvx --from copier==9.11.1 python -B "$@" ;;
    *) exec "$runtime" "$@" ;;
esac
