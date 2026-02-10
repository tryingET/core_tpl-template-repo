# Security Policy

## Supported versions

Security fixes target the latest release and `main` branch.

## Reporting a vulnerability

Use private reporting channels.

1. Preferred: GitHub Security tab -> **Report a vulnerability**.
2. If private reporting is unavailable, open a minimal issue titled
   `Security contact request` without exploit details and request a private channel.
3. Include impact, affected versions, and reproduction steps.
4. Avoid public disclosure until maintainers confirm a fix/release plan.

## Release baseline

- Release flow uses release-please PRs before tags/releases.
- Release checks validate release configuration and changelog baseline.
- Publish flow builds a tagged source archive and uploads it to the release.
- Workflow permissions default to read and elevate per job only.
