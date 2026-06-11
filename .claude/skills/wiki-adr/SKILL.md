---
name: wiki-adr
description: Use when a product, architecture, infrastructure, dependency, repo-boundary, or operations choice becomes a durable decision that should be recorded as an ADR — outside of the normal /planning flow. For decisions that emerge ad-hoc (e.g., a choice made during implementation or review that wasn't planned ahead). If the decision came from /planning, the ADR was already created — use this skill only to amend status or consequences post-merge.
---

# Wiki ADR

## Wiki Zones

Per the wiki-zone model in `CONCEPT.md`, route wiki knowledge through namespace zones:

- `wiki/<namespace>/` — product/domain knowledge for one namespace: its concept, vocabulary, architecture, and app/API behavior. One zone per product, customer, domain, or workstream namespace the team defines.
- `wiki/platform/` — shared implementation substrate: infrastructure, deploys, dependencies, environments, and cross-namespace implementation details.
- `wiki/general/` — team/brain workflow operating knowledge: lifecycle semantics, conventions, and process principles.

**Boundary rule:** route by implementation sharing, not by topic. If changing the knowledge would force edits in more than one namespace's code, use `platform`; if it only touches one namespace's code, use that namespace's zone even when the concept sounds shared.

**Fixed-path exceptions:** `wiki/decisions/index.md`, `wiki/logs/`, and `wiki/index.md` stay at the wiki root. ADR files live under `wiki/decisions/<zone>/` while retaining global ADR numbers and `Namespace:` fields (a product namespace, `platform`, or `general`).

If the wiki predates zones, tolerate a half-migrated layout: read/update existing legacy root pages when a `repos.yaml` feed still points there, but classify the intended zone and call out any future move needed. Do not move wiki pages as part of this skill unless the user explicitly asks for a migration.

Use this skill to create or update architecture decision records for decisions captured **outside of `/planning`** — i.e., choices that emerged during implementation, review, or incident response.

If a decision was made during a `/planning` session, the ADR was already written as part of that flow. Use this skill only to:
- Amend the Decision or Consequences sections after implementation reveals nuance
- Update the Status after a PR merges (preferred path: `/wiki-sync`)
- Create an ADR for a durable decision that bypassed `/planning`

## Workflow

1. Read `repos.yaml`, `CONCEPT.md`, and `wiki/decisions/index.md`.
2. Determine whether the decision is durable enough for an ADR and classify its `Namespace:` (a product namespace, `platform`, or `general`) using the wiki-zone boundary rule. If still unresolved, add it to `inbox/open-questions.md` instead. If it is a claim needing source backing, add it to `inbox/claims.md` instead.
3. Pick the ADR number = max existing in `wiki/decisions/*/adr-*.md` + 1, across all decision zone folders.
4. Create `wiki/decisions/<zone>/adr-NNN-<slug>.md`:

```markdown
# ADR NNN: <Title>

Status: <proposed | accepted | superseded>
Date: YYYY-MM-DD
Namespace: <product namespace | platform | general>

## Context

<Why this decision is being made>

## Decision

<What was decided>

## Alternatives Considered

<What else was considered and why it was rejected>

## Consequences

<Expected outcomes and trade-offs>

## Sources

<Relevant docs, PRs, or issues>

## Related

- [Decision index](../index.md)
```

5. Update `wiki/decisions/index.md` — add the new ADR under its zone group.
6. Link back from affected wiki pages.
7. Append a short entry to `wiki/logs/index.md`.

## Rules

- ADRs are for decisions, not vague ideas. If the decision is still unresolved, use `inbox/open-questions.md`.
- If a claim lacks support, use `inbox/claims.md`.
- Keep ADRs concise and source-linked.
- ADRs live in `wiki/decisions/<zone>/`; choose the zone with the implementation-sharing boundary rule and always add or preserve `Namespace:`.
- Do not create a duplicate ADR for a decision already captured by `/planning`.
