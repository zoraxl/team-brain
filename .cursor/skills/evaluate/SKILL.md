---
name: evaluate
description: Optional pre-PR gate, especially when the user implemented a ready-to-ship phase manually. Verifies the implementation matches the plan by mapping each acceptance criterion to code, reports gaps, and marks complete phases implemented-pending-pr. Does not write docs, clean plans, or run wiki tools — those are handled post-merge by /wiki-sync. Does not run lint/typecheck/UI checks — that is /review-pr's job. Use when the user says "/evaluate", "evaluate the implementation", "check my work against the plan", "is this implementation done", "audit my code against the plan".
---

# Evaluate

Optional pre-PR gate. Use this especially when the user implemented a `ready to ship` phase manually and wants an acceptance-criteria audit before `/review-pr`. `/implement` can already mark its own completed phases `implemented-pending-pr` after it resolves questions, writes code, and runs `/simplify`.

## When to use

Slot in the workflow:

```
/brainstorm → /planning → /implement → /evaluate → /review-pr → merge → /wiki-sync
```

Trigger phrases: "/evaluate", "evaluate the implementation", "check my work against the plan", "is this implementation done", "audit my code against the plan".

## Rules

- Treat plans as evaluation criteria, not as instructions to rewrite code.
- Findings come first. If gaps exist, stop after reporting them unless the user explicitly asks for fixes.
- Skip phase files with `status: wip` — those should either go through `/implement` directly or be reviewed/flipped to `ready to ship` first. Note them in output.
- Do not write docs, archive plans, or invoke wiki-side tools (`/wiki-sync`, `/wiki-lint`).
- Do not run lint / typecheck / UI validation — `/review-pr` owns that.
- Report missing or broken lifecycle links. When every acceptance criterion for a phase is complete, update that phase to `status: implemented-pending-pr` unless it already has a later status.

## Inputs

The user may provide:

- A plan folder, e.g. `plans/<namespace>/<feature-slug>/`.
- A feature slug.
- An implementation repo (resolve via `repos.yaml`).
- Specific files or commits to evaluate.

If no plan is named, list active feature folders under `plans/` and ask only if multiple plausible candidates exist.

## Workflow

### Step 1 — Read the plan

- List every phase file in `plans/<namespace>/<feature-slug>/`.
- For each file, check the frontmatter `status:` value:
  - `ready to ship` → include in evaluation.
  - `implemented-pending-pr` or `pr-open` → include if the user is re-checking already implemented or submitted work.
  - `wip` → skip; record in output as "skipped (still wip)".
- For each included phase, check lifecycle frontmatter and record whether `namespace`, `source_dump`, `artifact_pr`, `related_pr`, and `wiki_log` are present when expected.
- If `source_dump` is present, verify that the referenced source idea file exists.
- For each `ready to ship` phase, extract goals, scope, out-of-scope items, acceptance criteria, key design decisions, and stated implementation paths.
- If `plans/<namespace>/<feature-slug>/tests.md` exists, read its open entries — these are empirical questions that may have been answered during implementation; flag any that should now be resolved.

### Step 1.5 — Check prior phase lifecycle state

When evaluating a later phase in a plan folder, inspect earlier sibling phases before reading implementation code:

- If an earlier phase is `implemented-pending-pr`, `pr-open`, `implemented-and-synced`, or `archived`, note it as prior work and do not re-evaluate it unless the user asks.
- If an earlier phase is still `wip` or `ready to ship` but the current implementation appears to depend on it, flag the stale lifecycle state.
- If an earlier phase appears implemented from code or PR evidence but lacks status metadata, update it only when the evidence is clear; otherwise report it as a lifecycle gap for `/review-pr` or `/lifecycle-audit`.
- If an earlier phase was intentionally abandoned or superseded, route the remaining context to `inbox/backlog.md` before any cleanup happens.

`artifact_pr` is document provenance only. Do not treat it as implementation evidence, do not let it block evaluation, and report any apparent artifact-only PR stored in `related_pr` as a lifecycle link gap.

### Step 2 — Inspect the implementation

- For each acceptance criterion, locate the corresponding code, tests, migrations, or configuration in the implementation repo.
- Identify missing, partial, over-scoped, or unclear implementation.
- Cross-reference key design decisions against actual code structure to flag silent drift (implemented differently than planned, even if the criterion technically passes).

### Step 3 — Report findings

Produce a checklist mapping each acceptance criterion to one of:

- `complete` — code clearly satisfies the criterion
- `partial` — some of the criterion is met, gaps remain
- `missing` — no evidence in code
- `unclear` — evidence exists but uncertain whether it fully satisfies

Order findings by severity: `missing` > `partial` > `unclear` > `complete`. For each non-`complete` row, include the plan reference (phase + criterion) and the code locations checked.

**If anything is `partial`, `missing`, or `unclear`:** stop here. Do not proceed to Step 4. The user must fix the gaps and re-run `/evaluate`.

### Step 4 — Lifecycle and code-quality pass (only if Step 3 is fully `complete`)

When every acceptance criterion is `complete`:

1. Add or update the evaluated phase frontmatter:
   ```yaml
   status: implemented-pending-pr
   ```
   Preserve `namespace`, `source_dump`, `artifact_pr`, `related_pr`, and `wiki_log` fields. Do not overwrite later statuses such as implementation `pr-open`, `implemented-and-synced`, or `archived`. Do not update the linked source idea here unless the plan explicitly says implementation owns that transition; source idea PR/archive state is normally handled by `/review-pr` and `/wiki-sync`.
2. Optionally invoke a code-quality skill (e.g. `/simplify` if available in this environment) on the changed files to review for reuse, quality, and efficiency. Skip this if `/implement` already ran `/simplify` for the same diff.

### Step 5 — Output

Produce one of two outputs.

**If gaps were found:**

- Severity-ordered gap list (plan reference + code location for each gap).
- Any `tests.md` open entries that look resolved by the implementation (flag for migration to a Key Design Decision).
- Lifecycle link gaps, including missing `namespace`, missing or broken `source_dump`, artifact-only PRs stored in `related_pr`, missing implementation `related_pr` when a PR exists, or a missing PR body lifecycle section.
- Skipped phases (those still at `status: wip`).
- Recommendation: fix the gaps, then re-run `/evaluate`. Do not proceed to `/review-pr` yet.

**If ready for /review-pr:**

- Confirmation that all acceptance criteria across `ready to ship` phases are `complete`.
- Phase files marked `implemented-pending-pr`.
- Skipped phases (those still at `status: wip`), if any.
- Summary of any code-quality pass results (if Step 4 ran).
- Lifecycle link status. If any link is missing but does not block code correctness, report it clearly so `/review-pr` can resolve it before opening or updating the PR.
- Prior phase lifecycle notes, including stale, missing, superseded, or abandoned phase status.
- Any `tests.md` entries still `Status: open` (these are empirical and may need post-deploy follow-up).
- Recommendation: proceed to `/review-pr`.

## What this skill does NOT do

- ❌ Write docs or implementation-repo design files.
- ❌ Mark plan files complete or move them to an archive.
- ❌ Call `/wiki-sync` or `/wiki-lint`.
- ❌ Run lint, format, typecheck, or browser UI validation (those run in `/review-pr`).
- ❌ Generate a PR title or description (that is `/review-pr`'s job).

## Repository Map

Read `repos.yaml` at the repo root to resolve sibling repo paths. Do not use hardcoded local paths.
