#!/usr/bin/env sh
# Run a company-owned local/ extension hook, if the company provides one.
#
# usage: scripts/lib/run-local-hook.sh <local/relative/path> [args...]
#
# local/ matches no template_owned or agent_owned glob in
# contracts/template-ownership.yml, so an L1 template refresh never writes or
# deletes anything under it. The template entry scripts (CI lanes, git hooks,
# install-hooks.sh) call their local/ counterpart through this helper; see
# docs/dev/l1-local-extensions.md.
#
# - absent hook: no-op (exit 0)
# - present but not executable: error (exit 1), so a lost mode bit never
#   silently drops a company gate
# - present and executable: runs from the repo root with the given args; its
#   exit status is returned unchanged
set -eu

[ "$#" -ge 1 ] || {
	echo "usage: scripts/lib/run-local-hook.sh <local/path> [args...]" >&2
	exit 2
}
hook="$1"
shift
case "$hook" in
local/*) ;;
*)
	echo "error: local hook path must live under local/: $hook" >&2
	exit 2
	;;
esac

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$repo_root"

if [ ! -e "$hook" ] && [ ! -L "$hook" ]; then
	exit 0
fi
if [ ! -f "$hook" ] || [ ! -x "$hook" ]; then
	echo "error: company hook $hook exists but is not an executable file (chmod +x $hook, or remove it)" >&2
	exit 1
fi
exec "./$hook" "$@"
