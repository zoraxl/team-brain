---
name: wiki-lint
description: Use for periodic maintenance audits of the team wiki. Finds stale pages, orphan pages, missing backlinks, unsourced claims, contradictions, old open questions, and engineering pages that need review after infrastructure, dependency, or repo-structure changes.
---

# Wiki Lint

## Wiki Zones

Per the wiki-zone model in `CONCEPT.md`, route wiki knowledge through namespace zones:

- `wiki/<namespace>/` — product/domain knowledge for one namespace: its concept, vocabulary, architecture, and app/API behavior. One zone per product, customer, domain, or workstream namespace the team defines.
- `wiki/platform/` — shared implementation substrate: infrastructure, deploys, dependencies, environments, and cross-namespace implementation details.
- `wiki/general/` — team/brain workflow operating knowledge: lifecycle semantics, conventions, and process principles.

**Boundary rule:** route by implementation sharing, not by topic. If changing the knowledge would force edits in more than one namespace's code, use `platform`; if it only touches one namespace's code, use that namespace's zone even when the concept sounds shared.

**Fixed-path exceptions:** `wiki/decisions/index.md`, `wiki/logs/`, and `wiki/index.md` stay at the wiki root. ADR files live under `wiki/decisions/<zone>/` while retaining global ADR numbers and `Namespace:` fields (a product namespace, `platform`, or `general`).

If the wiki predates zones, tolerate a half-migrated layout: read/update existing legacy root pages when a `repos.yaml` feed still points there, but classify the intended zone and call out any future move needed. Do not move wiki pages as part of this skill unless the user explicitly asks for a migration.

Use this skill to audit wiki health.

## Workflow

1. Read `CONCEPT.md`, `repos.yaml`, and `wiki/index.md`.
2. Inspect the wiki structure.
3. Check for:
   - pages missing from `wiki/index.md`
   - links to missing files
   - any of `fragments.md`, `open-questions.md`, `claims.md`, `threads.md` existing directly under `wiki/` (violation: these belong in `inbox/`)
   - any `wiki/log.md` (singular) reference — should be `wiki/logs/index.md`
   - stale `Last reviewed` dates
   - engineering pages missing runbook or incident links
   - contradictions across product/system/engineering pages
   - mixed-namespace pages that combine implementation claims from different namespaces outside an intentional comparison or `platform` shared-substrate page
   - namespace-specific pages placed outside their intended zone once a zone page exists, excluding fixed root paths (`wiki/decisions/index.md`, `wiki/logs/`, `wiki/index.md`)
   - `repos[].sources[].feeds` targets in `repos.yaml` that don't exist as wiki pages
   - `repos[].sources[].path` entries that don't exist in the sibling repo on disk (flag, don't fail)
4. Use the implementation-sharing boundary rule when classifying mixed-namespace or wrong-zone pages; topic overlap alone is not a lint failure.
5. Report findings first, ordered by severity.
6. Make small obvious fixes when requested or clearly implied.

## Useful Commands

- `find . -name "*.md" | sort`
- `rg -n "source-needed|Status: open|TODO|TBD|Last reviewed" .`
- `rg -n "\\]\\([^)]*\\)" .`

## Output

Use code-review style:

- findings with file references
- open questions
- suggested fixes
- optional summary
