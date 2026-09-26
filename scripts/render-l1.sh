#!/usr/bin/env sh
# Render the L1 a refresh of <target> would produce, into <out-dir>, and stop.
# Read-only for <target>: no ownership planning, receipts, AK checks or writes.
# Consumers (e.g. template-propagator `report l1-refresh-preview`) diff the render
# against the target themselves.
set -eu

usage() {
	cat <<'USAGE' >&2
usage: render-l1.sh <target> <out-dir> [repo-slug]

<out-dir> must not exist yet; it receives the rendered L1 tree.
USAGE
}

[ "$#" -ge 2 ] && [ "$#" -le 3 ] || { usage; exit 2; }
target="$1"
out="$2"
repo_slug="${3:-}"
[ ! -e "$out" ] || { echo "error: output path already exists: $out" >&2; exit 2; }
out_parent="$(CDPATH='' cd -- "$(dirname -- "$out")" && pwd)" || { echo "error: output parent does not exist: $out" >&2; exit 2; }
out="$out_parent/$(basename -- "$out")"

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
# A preview must show what an apply would do, and apply refuses a dirty L0: the render
# reads the working tree, so uncommitted L0 edits would otherwise leak into it.
if [ -n "$(git -C "$repo_root" status --porcelain)" ]; then
	echo "error: L1 render requires a clean L0 worktree at an exact commit" >&2
	exit 2
fi
L1_RENDER_ONLY_OUT="$out" exec "$repo_root/scripts/lib/run-l1-template-refresh.sh" "$target" "$repo_slug" "" ""
