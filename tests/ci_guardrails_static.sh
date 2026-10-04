#!/usr/bin/env sh
set -eu
if [ "$#" -ne 0 ]; then
	printf '%s\n' "error: ci_guardrails_static.sh accepts no arguments" >&2
	exit 2
fi
repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"
export PYTHONDONTWRITEBYTECODE=1
. "$repo_root/tests/ci_guardrails_helpers.sh"
. "$repo_root/tests/ci_guardrails_context.sh"
. "$repo_root/tests/ci_guardrails_root.sh"
. "$repo_root/tests/ci_guardrails_l2.sh"
. "$repo_root/tests/ci_guardrails_tail.sh"
