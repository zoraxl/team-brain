---
name: wiki-runbook
description: Use when documenting operational procedures, debugging playbooks, recovery steps, deployment checks, incidents, on-call procedures, or cross-repo infrastructure workflows in the team wiki.
---

# Wiki Runbook

## Wiki Zones

Per the wiki-zone model in `CONCEPT.md`, route wiki knowledge through namespace zones:

- `wiki/<namespace>/` — product/domain knowledge for one namespace: its concept, vocabulary, architecture, and app/API behavior. One zone per product, customer, domain, or workstream namespace the team defines.
- `wiki/platform/` — shared implementation substrate: infrastructure, deploys, dependencies, environments, and cross-namespace implementation details.
- `wiki/general/` — team/brain workflow operating knowledge: lifecycle semantics, conventions, and process principles.

**Boundary rule:** route by implementation sharing, not by topic. If changing the knowledge would force edits in more than one namespace's code, use `platform`; if it only touches one namespace's code, use that namespace's zone even when the concept sounds shared.

**Fixed-path exceptions:** `wiki/decisions/index.md`, `wiki/logs/`, and `wiki/index.md` stay at the wiki root. ADR files live under `wiki/decisions/<zone>/` while retaining global ADR numbers and `Namespace:` fields (a product namespace, `platform`, or `general`).

If the wiki predates zones, tolerate a half-migrated layout: read/update existing legacy root pages when a `repos.yaml` feed still points there, but classify the intended zone and call out any future move needed. Do not move wiki pages as part of this skill unless the user explicitly asks for a migration.

Use this skill to turn operational knowledge into repeatable procedures.

## Workflow

1. Read `CONCEPT.md`, `repos.yaml`, `wiki/index.md`, and the zone-appropriate runbook/infrastructure pages. For shared runtime operations, use `wiki/platform/engineering/runbooks.md` and `wiki/platform/engineering/infrastructure.md`.
2. Gather source material or implementation details.
3. Resolve the destination zone with the boundary rule: namespace-specific operations go to that namespace's zone, shared runtime/infrastructure operations go to `wiki/platform/`, and brain workflow operations go to `wiki/general/`.
4. Add or update a runbook with:
   - when to use it
   - symptoms
   - likely causes
   - checks
   - recovery steps
   - verification
   - prevention
   - related pages
5. If the runbook comes from a failure, update the zone-appropriate incidents page; if the wiki is mid-migration to zones, tolerate a legacy `wiki/engineering/incidents.md`.
6. If the procedure depends on unknown environment details, add an open question to `inbox/open-questions.md`.
7. Append `wiki/logs/index.md`.

## Rules

- Do not invent commands or environment names.
- Mark environment-specific unknowns explicitly.
- Link architecture, data-flow, deploy, dependency, and incident pages when relevant.
- Prefer cross-repo runbooks here; purely repo-local procedures can stay with their owning repo.
- Prefer `platform` only when the operational procedure depends on shared implementation substrate, not merely because two namespaces have similar concepts.
