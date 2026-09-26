#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
vectors="$root/contracts/canonicalization-v1-vectors.json"
python "$root/scripts/canonicalization/reference.py" "$vectors" > "${TMPDIR:-/tmp}/gate-a-python.json"
node --experimental-strip-types "$root/scripts/canonicalization/reference.ts" "$vectors" > "${TMPDIR:-/tmp}/gate-a-typescript.json"
python - "${TMPDIR:-/tmp}/gate-a-python.json" "${TMPDIR:-/tmp}/gate-a-typescript.json" <<'PY_COMPARE'
import json,sys
p=json.load(open(sys.argv[1])); t=json.load(open(sys.argv[2]))
assert all(r['ok'] for r in p['results']), 'Python vector failure'
assert all(r['ok'] for r in t['results']), 'TypeScript vector failure'
pa={r['id']:r['actual'] for r in p['results']}; ta={r['id']:r['actual'] for r in t['results']}
assert pa == ta, 'cross-language outputs differ'
print(json.dumps({'status':'pass','vectors':len(pa),'implementations':['python','typescript']},sort_keys=True))
PY_COMPARE
