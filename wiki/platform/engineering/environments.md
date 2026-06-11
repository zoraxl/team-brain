# Environments

Status: template
Last reviewed: YYYY-MM-DD

Track environment names, ownership, configuration contracts, and known gaps.

## Environments

| Environment | Purpose | Owner | Notes |
|---|---|---|---|
| local | Developer machines | TBD | Replace with project-specific setup notes. |
| staging | Pre-production validation | TBD | Replace or remove. |
| production | Live system | TBD | Replace or remove. |

## Configuration Contracts

- Add required cross-repo environment variables or secrets by name only when safe.
- Do not commit secret values.

## Open Questions

- Which repo owns each environment contract?
