#!/bin/sh
set -eu

script_dir="$(cd "$(dirname "$0")" && pwd)"
"$script_dir/smoke.sh"
