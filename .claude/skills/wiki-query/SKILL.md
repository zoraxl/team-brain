---
name: wiki-query
description: Use when retrieving knowledge from the team wiki, including product concept, architecture, infrastructure, repo changes, decisions, runbooks, incidents, open questions, and source-backed claims. Answers should cite relevant wiki/source pages and distinguish stable knowledge from uncertainty.
---

# Wiki Query

## Wiki Zones

Per the wiki-zone model in `CONCEPT.md`, route wiki knowledge through namespace zones:

- `wiki/<namespace>/` — product/domain knowledge for one namespace: its concept, vocabulary, architecture, and app/API behavior. One zone per product, customer, domain, or workstream namespace the team defines.
- `wiki/platform/` — shared implementation substrate: infrastructure, deploys, dependencies, environments, and cross-namespace implementation details.
- `wiki/general/` — team/brain workflow operating knowledge: lifecycle semantics, conventions, and process principles.

**Boundary rule:** route by implementation sharing, not by topic. If changing the knowledge would force edits in more than one namespace's code, use `platform`; if it only touches one namespace's code, use that namespace's zone even when the concept sounds shared.

**Fixed-path exceptions:** `wiki/decisions/index.md`, `wiki/logs/`, and `wiki/index.md` stay at the wiki root. ADR files live under `wiki/decisions/<zone>/` while retaining global ADR numbers and `Namespace:` fields (a product namespace, `platform`, or `general`).

If the wiki predates zones, tolerate a half-migrated layout: read/update existing legacy root pages when a `repos.yaml` feed still points there, but classify the intended zone and call out any future move needed. Do not move wiki pages as part of this skill unless the user explicitly asks for a migration.

Use this skill to answer questions from the wiki.

## Workflow

1. Read `CONCEPT.md`, `repos.yaml`, and `wiki/index.md`.
2. Infer the relevant namespace zone from the user's wording, repo names, and source paths. If ambiguous, ask which product/namespace they mean, or whether they mean shared platform substrate or general workflow knowledge.
3. Search the matching wiki zone first, the matching decision zone under `wiki/decisions/<zone>/`, plus fixed root exceptions (`wiki/decisions/index.md`, `wiki/logs/`, `wiki/index.md`) and `wiki/platform/` only when shared implementation substrate is relevant.
4. Read relevant pages, ADRs, and `repos.yaml` source entries. If the wiki is mid-migration to zones, also check legacy root pages when the intended zone page does not exist yet.
5. If the question is operational or engineering-related, include the zone-appropriate runbook/infrastructure pages, using `wiki/platform/` for shared runtime operations.
6. If the question is unresolved or speculative, check `inbox/open-questions.md` and `inbox/claims.md`.
7. Answer with links to relevant files and name the zone boundary when it affects the answer.

## Answer Rules

- Distinguish:
  - stable source-backed knowledge
  - wiki synthesis
  - source-needed claims
  - open questions
- Do not invent missing details.
- Mention when the wiki does not contain enough evidence.
- Prefer concise answers with file references.
- Do not answer a namespace-specific question from another namespace's pages unless the user asks for a comparison or the page is explicitly shared `platform` knowledge.

## Useful Searches

- `rg -n "topic" wiki/ inbox/ CONCEPT.md repos.yaml`
- `rg -n "source-needed|Status: open|Open" inbox/claims.md inbox/open-questions.md`
