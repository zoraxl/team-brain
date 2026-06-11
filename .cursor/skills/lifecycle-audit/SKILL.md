---
name: lifecycle-audit
description: Audit historical idea, plan, PR, archive, and wiki-sync lifecycle state. Classifies old brainstorms, plans, synced PRs, and merged PR history by confidence, reports proposed moves/archive actions first, and applies changes only after explicit approval. Use when cleaning old inbox dumps, backfilling lifecycle metadata, finding implemented ideas, or preparing namespace-aware migration.
---

# Lifecycle Audit

Audit historical workflow files before moving or archiving them. This skill is for messy pre-lifecycle history, not normal single-PR `/wiki-sync`.

## When to Use

Use when the user asks to:

- audit historical ideas or plans
- classify old brainstorm dumps
- identify which ideas were implemented
- backfill lifecycle metadata
- clean old `inbox/dump/` files
- prepare namespace-aware migration into `general` or another team-defined namespace

Do not use for normal post-merge wiki ingestion; use `/wiki-sync` for that.

## Rules

- Report first. Do not move, archive, or edit files during the first pass.
- Require explicit second approval before applying any proposed action.
- Never archive `probably-implemented` or `unknown` files without explicit approval.
- Never overwrite an existing destination path.
- Normalize stored paths to forward slashes.
- Treat similarity as evidence, not proof.
- Do not use legacy inference to weaken normal `/wiki-sync` verification. Backfill missing metadata first, then let `/wiki-sync` consume the confirmed chain.
- Never archive a source idea or plan folder unless the whole linked idea/plan chain is complete, synced, superseded, or explicitly approved for legacy cleanup.
- Treat `artifact_pr` as provenance only. It must not be used as implementation evidence and must not advance a source idea or phase to `pr-open`.
- Default artifact-PR migration audits to active `inbox/` and `plans/` files. Inspect or report archived metadata inconsistencies only when the user explicitly requests archive scope.

## Read Scope

Read in passes to preserve context:

1. `repos.yaml`, `CONCEPT.md`, and `wiki/logs/synced-prs.md`.
2. File lists and headings for `inbox/**/*.md`, `plans/**/*.md`, and `wiki/logs/*.md`. Include `archive/**/*.md` only when the user asks for archive or historical consistency scope.
3. Full file contents only for candidates that need classification.
4. Merged GitHub PR evidence with `gh pr list --state merged` and `gh pr view` only for target repos that matter to the audit.

## Classification Labels

- `confirmed-implemented-synced` - linked or strongly evidenced merged PR appears in `wiki/logs/synced-prs.md`.
- `confirmed-implemented-not-synced` - merged PR exists but is not recorded in `wiki/logs/synced-prs.md`.
- `probably-implemented` - title/content strongly matches merged work but lacks explicit links.
- `planned-active` - linked plan exists and is not archived/synced.
- `superseded` - file points to a replacement idea, plan, or wiki page.
- `unknown` - insufficient evidence.
- `artifact-pr-misuse` - `status: pr-open` or `related_pr` points at a PR that only lands brainstorms, plans, strategy docs, source material, or planning cleanup.
- `implementation-pr-valid` - `related_pr` points at a PR that actually submits the linked implementation or brain-native workflow change.
- `no-implementation-resolved` - a source idea produced a durable strategy/doc output and no implementation plan is expected.
- `ambiguous-needs-confirmation` - PR body, changed files, lifecycle metadata, or source links conflict; do not migrate without user confirmation.

## Legacy Backfill Confidence

For old idea/plan chains that predate lifecycle metadata, classify the cleanup path separately from implementation status:

- `proven-chain` - source idea, plan files, PR body/diff, and synced ledger all agree. Safe to propose metadata backfill and `/wiki-sync` cleanup.
- `likely-needs-confirmation` - paths, titles, or PR diffs strongly suggest a chain, but one or more lifecycle links are missing. Ask the user to confirm before writing metadata.
- `unsafe-to-clean` - source idea appears multi-use, phases are incomplete, PR evidence is missing, or links conflict. Do not backfill or archive; report what evidence is missing.

## Artifact PR Migration Rules

Use these rules for active lifecycle files that predate the `artifact_pr` contract:

- Source idea with an artifact-only PR and linked plan: propose `status: planned`, `artifact_pr: <PR URL>`, and clear `related_pr` unless a separate implementation PR exists.
- Plan phase with an artifact-only PR: preserve or restore the active work-state status (`wip` or `ready to ship` when evidence supports it), set `artifact_pr: <PR URL>`, and clear `related_pr`.
- Strategy-only or durable-doc brainstorm with no implementation expected: propose `status: resolved`, `artifact_pr: <PR URL>` when known, and `related_strategy:` or `related_doc:` pointing at the durable output.
- Genuine implementation PR: keep `status: pr-open` and `related_pr`.

PR evidence checks:

- Treat PR body language such as "planning docs", "brainstorm", "strategy doc", "source material", "artifact only", or "no implementation changes yet" as artifact-only evidence.
- Treat linked implementation repo PRs, code changes, or brain-native skill/workflow/wiki changes as implementation evidence only when they match the plan scope.
- Treat PR evidence as supporting evidence, not proof. Conflicts become `ambiguous-needs-confirmation`.
- Allow batch approval for `no-implementation-resolved` migrations only when durable-doc links are proven. Ambiguous durable-doc migrations require per-file approval.

## Report Format

Produce a concise report grouped by classification:

```markdown
# Lifecycle Audit: <scope>

## Summary
- Files scanned:
- PRs checked:
- Safe archive candidates:
- Needs review:

## Proposed actions
- `<path>` — <classification>, confidence: <high|medium|low>. Evidence: <short evidence>. Proposed action: <move/archive/update/run wiki-sync/leave>.

## Needs approval
List the exact actions that require user approval before applying.
```

## Apply Mode

Only after the user explicitly approves one or more proposed actions:

1. Move active idea files to namespace folders when the team uses them, e.g. `inbox/<namespace>-ideas/`, or leave them in `inbox/dump/` if the repo has not adopted namespace intake folders.
2. Move active plans to `plans/<namespace>/<feature-slug>/`.
3. Archive implemented synced files to:
   - `archive/<namespace>/ideas/YYYY-MM/`
   - `archive/<namespace>/plans/YYYY-MM/`
4. Add or update metadata:
   ```yaml
   namespace:
   status:
   source_dump:
   related_plan:
   related_pr:
   artifact_pr:
   related_doc:
   related_strategy:
   wiki_log:
   archived_from:
   archived_at:
   ```
5. For confirmed legacy backfill before `/wiki-sync`, write enough metadata for the normal verification path:
   - Source idea: `namespace`, `status`, `related_plan`, `artifact_pr`, `related_pr`, `related_doc`, `related_strategy`, `wiki_log` when known.
   - Plan phases: `namespace`, `status`, `source_dump`, `artifact_pr`, `related_pr`, `wiki_log` when known.
   - Preserve `archive_after`, `archived_from`, and `archived_at` if already present.
   - Use `status: planned` for active source ideas with linked plans, `status: resolved` for no-implementation source ideas with proven durable-doc outputs, `status: implemented-pending-pr` for implemented phases without a PR stamp, `status: pr-open` only when `related_pr` is a real implementation or workflow-deliverable PR URL, and `status: implemented-and-synced` only when the implementation PR is already in `wiki/logs/synced-prs.md`.
6. Update active links that point to moved files.
7. Report every file changed.

## Handoff to Wiki Sync

After applying approved backfill:

- If the chain is `proven-chain` and the PR is merged but not synced, recommend `/wiki-sync <repo>#<pr>`.
- If the chain is already synced and every linked phase is complete, recommend `/wiki-sync` only when archive cleanup still needs to run and the metadata now verifies.
- If any phase is incomplete, keep the source idea and plan folder active; do not ask `/wiki-sync` to archive the chain yet.
- If the user approved cleanup of abandoned or superseded phases, ensure that context is preserved in `inbox/backlog.md` or the relevant file metadata before any archive move.

## Output

End with one of:

- "Report only — no files changed."
- "Applied approved lifecycle actions: <count> files changed."
