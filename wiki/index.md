# Wiki Index

Status: template
Last reviewed: YYYY-MM-DD

## Start Here

- [Concept](../CONCEPT.md)
- [Repos manifest](../repos.yaml)
- [Agent skills](../.agents/README.md)
- [Maintenance log](logs/index.md)
- [Synced PR ledger](logs/synced-prs.md)

The wiki contains only **decided and implemented** knowledge. Pre-implementation material — fragments, open questions, claims, backlog items, threads, brainstorm dumps — lives in [`inbox/`](../inbox/). Active phase plans live in `plans/<namespace>/<feature-slug>/`; completed lifecycle material is archived under `archive/<namespace>/`.

## Wiki Zones

Wiki knowledge is organized into namespace zones (see [CONCEPT.md](../CONCEPT.md) for the boundary rule):

- `wiki/<namespace>/` — one zone per product, customer, domain, or workstream namespace. Created as the team adopts namespaces. This template ships with [`wiki/product/`](product/) as an example zone — rename it to your first product namespace or delete it.
- [`wiki/platform/`](platform/) — shared implementation substrate across namespaces: architecture, infrastructure, deploys, dependencies, runbooks, incidents.
- `wiki/general/` — team/brain workflow operating knowledge: lifecycle semantics, conventions, process principles. Created lazily.
- [`wiki/decisions/`](decisions/) — ADRs, grouped under `wiki/decisions/<zone>/` with global numbering.
- [`wiki/logs/`](logs/) — maintenance and sync logs (fixed root path).

## Product (example zone — rename to your first namespace)

- [Vision](product/vision.md)
- [Glossary](product/glossary.md)

## Platform

- [Architecture](platform/architecture.md)
- [Repo map](platform/repo-map.md)
- [Data flow](platform/data-flow.md)
- [Infrastructure](platform/engineering/infrastructure.md)
- [Environments](platform/engineering/environments.md)
- [Deploys](platform/engineering/deploys.md)
- [Repo changes](platform/engineering/repo-changes.md)
- [Dependencies](platform/engineering/dependencies.md)
- [Runbooks](platform/engineering/runbooks.md)
- [Incidents](platform/engineering/incidents.md)

## Decisions

- [Decision index](decisions/index.md)
- [ADR template](decisions/adr-template.md)
