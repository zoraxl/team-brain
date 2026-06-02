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
  - `wip` → skip; record in output as "skipped (still wip)".
- For each `ready to ship` phase, extract goals, scope, out-of-scope items, acceptance criteria, key design decisions, and stated implementation paths.
- If `plans/<namespace>/<feature-slug>/tests.md` exists, read its open entries — these are empirical questions that may have been answered during implementation; flag any that should now be resolved.

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
   Preserve `namespace`, `source_dump`, `related_pr`, and `wiki_log` fields.
2. Optionally invoke a code-quality skill (e.g. `/simplify` if available in this environment) on the changed files to review for reuse, quality, and efficiency. Skip this if `/implement` already ran `/simplify` for the same diff.

### Step 5 — Output

Produce one of two outputs.

**If gaps were found:**

- Severity-ordered gap list (plan reference + code location for each gap).
- Any `tests.md` open entries that look resolved by the implementation (flag for migration to a Key Design Decision).
- Skipped phases (those still at `status: wip`).
- Recommendation: fix the gaps, then re-run `/evaluate`. Do not proceed to `/review-pr` yet.

**If ready for /review-pr:**

- Confirmation that all acceptance criteria across `ready to ship` phases are `complete`.
- Phase files marked `implemented-pending-pr`.
- Skipped phases (those still at `status: wip`), if any.
- Summary of any code-quality pass results (if Step 4 ran).
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
