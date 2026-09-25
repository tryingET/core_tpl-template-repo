#!/usr/bin/env sh
# Point this repository's git hooks at .githooks (staged-file UBS pre-commit).
set -eu
repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)"
chmod +x "$repo_root/.githooks/pre-commit" 2>/dev/null || true
toplevel="$(git -C "$repo_root" rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$toplevel" ] && [ "$(CDPATH='' cd -- "$toplevel" && pwd -P)" = "$repo_root" ]; then
	git -C "$repo_root" config core.hooksPath .githooks
	echo "Configured git hooks path: .githooks"
else
	echo "warning: $repo_root is not the root of its own git repository; hook path not configured" >&2
fi
