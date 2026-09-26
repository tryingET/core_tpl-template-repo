# L1 company extensions (`local/`)

The L1 root scripts (`scripts/**`, `.githooks/**`, ...) are **template-owned**: an L1
template refresh replaces them with the L0 render. Company-specific gates, hooks and
settings therefore live in `local/`, which matches no pattern in
`contracts/template-ownership.yml`. Paths outside both ownership lists are target-only:
a refresh never writes, replaces or deletes them.

Each template entry point hands off to its optional company counterpart through
`scripts/lib/run-local-hook.sh`:

| Template entry point | Company hook | When it runs |
| --- | --- | --- |
| `scripts/ci/smoke.sh` | `local/ci/smoke.sh` | after the template smoke checks |
| `scripts/ci/full.sh` | `local/ci/full.sh` | after smoke, task-scope checks and the ROCS gate; gets the `full.sh` args (`--deep`) |
| `scripts/check-template-ci.sh` | `local/ci/check-template-ci.sh` | first, before the template checks |
| `.githooks/pre-commit` | `local/githooks/pre-commit` | after `scripts/ci/smoke.sh` |
| `.githooks/pre-push` | `local/githooks/pre-push` | after `scripts/ci/full.sh`; gets git's pre-push args and ref lines on stdin |
| `scripts/install-hooks.sh` | `local/install-hooks.sh` | after the template sets `core.hooksPath` |

Rules:

- A missing hook is a no-op. A hook that exists but is not an executable file is an
  error, so a lost mode bit never silently drops a company gate.
- Hooks run from the repo root; a non-zero exit fails the calling gate.
- Keep company tests and helpers wherever the company likes (for example `local/` or
  target-only files such as `tests/test_<name>.py`), and call them from the hook.

## ROCS settings (`local/rocs.env`)

`scripts/rocs.sh` runs the workspace rocs-cli core checkout pinned by the launcher
(`~/ai-society/core/rocs-cli`, or `ROCS_CORE_PROJECT`), the same model as the L2
templates. When `local/rocs.env` exists, the launcher sources it (POSIX `sh`, with
`set -a`, so plain assignments are exported) before anything else, with the launcher
arguments visible as `"$@"` and the repo root in `$repo`; `exit` in it aborts the
launcher. Typical content:

```sh
# Route ROCS outputs out of ontology/ (rocs-cli writes an ownership marker there).
ROCS_OUTPUT_ROOT=governance/ontology-dist
ROCS_AUTHORITY_AGGREGATE=1
: "${ROCS_CI_PROFILE:=main-strict}"
```

`scripts/ci/full.sh` runs `cleanup -> validate -> build` whenever
`ontology/manifest.yaml` exists, so outputs follow `ROCS_OUTPUT_ROOT` wherever it is set.
If `ontology/` is a declared gitlink that is not materialized, `full.sh` fails with
`ontology is not materialized`.
