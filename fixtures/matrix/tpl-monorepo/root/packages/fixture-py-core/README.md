# fixture-py-core



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

## Deferred work + task scope

Package/app slices inherit deferred-work and explicit task-scope authority from the parent monorepo root.
Do not create standalone AK state inside this member.

When a package/app slice needs explicit task scope, author/export it from the monorepo root:

```bash
# from monorepo root
./scripts/ak.sh task scope show <AK-ID>
mkdir -p governance/task-scopes && ./scripts/ak.sh task scope export <AK-ID> > governance/task-scopes/AK-<AK-ID>.snapshot.json
```

## Development

```bash
# Run tests (from monorepo root)
# Python
uv run pytest packages/fixture-py-core/tests/

# Node
npm test --workspace=packages/fixture-py-core
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
