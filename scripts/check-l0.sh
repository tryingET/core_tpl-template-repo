#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

"$repo_root/scripts/check-l0-guardrails.sh"
"$repo_root/scripts/check-supply-chain.sh"
"$repo_root/scripts/check-l0-generation.sh"
"$repo_root/scripts/check-l0-fixtures.sh"
