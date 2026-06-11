---
name: implement
description: Implement one or more phase plans in the target implementation repo. Can be used directly on wip plans: checks open questions, asks the user to resolve or route them one by one, locks the plan, implements the scoped work, runs /simplify, and marks the phase implemented-pending-pr. Use when the user says "/implement", "implement this plan", "build this phase", "start phase implementation", or asks to turn a phase plan into code.
---

# Implement

Implement a written phase plan in the target repo while preserving the plan lifecycle. This skill can be used directly on a `wip` plan: it resolves open questions with the user before writing code, then runs a focused code-quality pass with `/simplify` when available and marks the phase `implemented-pending-pr`.

## Workflow Slot

```text
/brainstorm -> /planning -> /implement -> /evaluate -> /review-pr -> merge -> /wiki-sync
```

## Inputs

The user may provide:

- A plan file, e.g. `plans/<namespace>/<feature-slug>/<phase-slug>.md`.
- A plan folder, e.g. `plans/<namespace>/<feature-slug>/`.
- A phase number or feature slug.
- A target implementation repo, if the plan does not make it clear.

If no plan is named, list plausible active plan folders under `plans/` and ask only when multiple candidates could match.

## Rules

- Read `repos.yaml` at the brain repo root to resolve implementation repo paths. Do not hardcode local paths.
- Treat plan files as the source of implementation scope. Do not expand scope unless the user explicitly asks.
- Preserve unrelated user changes in every repo.
- Do not implement code until every open question in the target phase is resolved in-place, routed to tests, or routed to backlog.
- Mark phases `implemented-pending-pr` after implementation and `/simplify` complete. `/evaluate` may also set this status when the user implemented the phase themselves.
- Do not create PRs, write PR summaries, archive plan files, or run wiki-sync tools.

## Step 1 - Resolve the Plan

1. Locate the requested phase file(s).
2. Read each phase file and record:
   - Frontmatter status.
   - Namespace, source dump, artifact PR, related PR, and wiki log fields.
   - Objective, scope, implementation steps, acceptance criteria, file paths, migrations, tests, and open questions.
3. If implementing a later phase, inspect earlier sibling phase statuses and note dependencies that are not implemented yet.

## Step 2 - Resolve Questions and Lock the Phase

Handle each phase by status:

- `ready to ship` - treat the phase as already locked and proceed to implementation.
- `wip` - enter an interactive question-resolution loop before implementation:
  - Read the `## Open Questions` section and present each question one by one.
  - For each question, ask the user to choose one bucket: resolve now, empirical test, or backlog.
  - Route empirical questions to `plans/<namespace>/<feature-slug>/tests.md`.
  - Route deferred questions to `inbox/backlog.md`.
  - Resolve in-place questions by updating the relevant plan sections, usually Key Design Decisions or Implementation.
  - Only after every open question is resolved or routed, remove the empty Open Questions section and change `status: wip` to `status: ready to ship`.
  - After this flip, treat the phase as locked implementation scope. Route new ideas to `inbox/backlog.md` or a follow-up phase.
- `implemented-pending-pr`, `implemented-and-synced`, or `archived` - do not reimplement unless the user explicitly asks for a revision.
- `pr-open` - verify the status before skipping:
  - If `related_pr` is present and points to an implementation or workflow-deliverable PR, treat the phase as already submitted and do not reimplement unless the user explicitly asks for a revision.
  - If `related_pr` is missing, equals `artifact_pr`, or the PR appears to be artifact-only, report a lifecycle metadata error instead of skipping. Ask the user whether to restore the phase to `wip`, restore it to `ready to ship`, or treat it as a revision of already-submitted work.

`artifact_pr` is document provenance only. Its presence must not block implementation of a `wip` or `ready to ship` phase.
An artifact-only PR is not implementation evidence. Do not treat `status: pr-open` as authoritative when the only supporting PR evidence is `artifact_pr`.

When locking a plan, keep edits limited to lifecycle status, question routing, and any directly required in-place answers.

## Step 3 - Implement

1. Move to the target implementation repo resolved from `repos.yaml`.
2. Read applicable engineering principles from `wiki/<namespace>/principles/<repo>/engineering.md` when present, then read local repo instructions (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, or path-specific guidance) before editing.
3. Implement the smallest code change that satisfies the phase plan.
4. Add or update tests when the plan calls for them or when risk warrants coverage.
5. Run the most relevant lightweight checks for the touched area when practical.

## Step 4 - Post-Implementation Simplify

After code changes are complete, invoke `/simplify` on the changed files or implementation diff if that skill is available.

Apply clear `/simplify` fixes that preserve behavior. If `/simplify` surfaces valid findings that are broader than this phase, report them as deferred; do not widen the implementation.

## Step 5 - Mark Implemented Pending PR

After implementation and `/simplify` are complete, add or update the implemented phase frontmatter:

```yaml
status: implemented-pending-pr
```

Preserve `namespace`, `source_dump`, `artifact_pr`, `related_pr`, and `wiki_log` fields. Do not stamp `related_pr`; `/review-pr` owns that after an implementation or workflow-deliverable PR exists.

## Step 6 - Output

Finish with:

- What was implemented and where.
- Any open questions resolved or routed.
- Any phase files moved from `wip` to `ready to ship` and then to `implemented-pending-pr`.
- `/simplify` result and checks run.
- Any known gaps, deferred cleanup, or tests not run.
- A clear handoff: tell the user they can proceed to `/review-pr`, or run `/evaluate` first if they want a separate acceptance-criteria audit.

Use this exact final handoff sentence when implementation appears complete:

> Implementation is complete and the phase is `implemented-pending-pr`; you can proceed to `/review-pr` or run `/evaluate` first for a separate acceptance-criteria audit.
