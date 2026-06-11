# Deploys

Status: template
Last reviewed: YYYY-MM-DD

Document deployment ownership, sequencing, and verification that spans repos.

## Deployment Surfaces

| Surface | Owner | Deploy Mechanism | Notes |
|---|---|---|---|
| app or service | TBD | TBD | Replace with team-specific details. |

## Checklist Template

```md
- [ ] Confirm source branch or release tag
- [ ] Review related wiki pages and ADRs
- [ ] Check migrations or data changes
- [ ] Deploy owning surfaces in the required order
- [ ] Verify health checks, logs, and core workflows
- [ ] Update incidents or runbooks if anything changed
```

## Related

- [Infrastructure](infrastructure.md)
- [Runbooks](runbooks.md)
- [Incidents](incidents.md)
