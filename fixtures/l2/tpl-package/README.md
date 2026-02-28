# fixture-core



- **Type**: library
- **Language**: python
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
uv run pytest packages/fixture-core/tests/

# Node
npm test --workspace=packages/fixture-core
```

## Notes

- NO `.git` directory — managed by monorepo
- NO `.github` workflows — CI from monorepo root
- NO release config — released from monorepo root

## ROCS command flow

ROCS commands should be run from the monorepo root:

```bash
# From monorepo root
./scripts/rocs.sh --doctor
./scripts/rocs.sh validate --repo .
```
