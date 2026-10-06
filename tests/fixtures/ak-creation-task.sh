#!/bin/sh
# Synthetic task visibility for golden agent births only; never live AK authority.
set -eu
if [ "$#" -ne 3 ] || [ "$1" != task ] || [ "$2" != show ] || [ "$3" != 5105 ]; then
    echo "error: unsupported synthetic AK invocation" >&2
    exit 97
fi
printf 'synthetic creation task 5105\n'
