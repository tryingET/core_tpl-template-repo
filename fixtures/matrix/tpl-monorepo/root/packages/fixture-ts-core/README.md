# fixture-ts-core



- **Type**: library
- **Language**: typescript
- **Company**: Holding Company

## Structure

```
src/              # Source code
tests/            # Test files
docs/             # Package docs
```

## Usage

This package is managed by the parent monorepo. See monorepo root for:

- Workspace configuration
- CI/CD pipelines
- Release process

## Development

```bash
# Run tests (from monorepo root)
# Python
uv run pytest packages/fixture-ts-core/tests/

# Node
npm test --workspace=packages/fixture-ts-core
```

## Notes

- NO `.git` directory — managed by monorepo
- NO `.github` workflows — CI from monorepo root
- NO release config — released from monorepo root
- Stack contract surface:
  - `policy/stack-lane.json` when an upstream `tech-stack-core` lane exists
  - `docs/tech-stack.local.md` for package-local overrides

## ROCS command flow

ROCS commands should be run from the monorepo root:

```bash
# From monorepo root
./scripts/rocs.sh --doctor
./scripts/rocs.sh validate --repo .
```
