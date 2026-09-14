---
name: evaluate
description: Optional pre-PR gate, especially when the user implemented a ready-to-ship phase manually. Verifies the implementation matches the plan by mapping each acceptance criterion to code, applies obvious gap fixes then re-evaluates, reports remaining gaps plus a fix report, and marks complete phases implemented-pending-pr. Does not write docs, clean plans, or run wiki tools — those are handled post-merge by /wiki-sync. Does not run lint/typecheck/UI checks — that is /review-pr's job. Use when the user says "/evaluate", "evaluate the implementation", "check my work against the plan", "is this implementation done", "audit my code against the plan".
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
- Findings come first. After mapping gaps, apply **obvious** fixes only, then re-run Steps 2–3. Leave non-obvious gaps for the user.
- Skip phase files with `status: wip` — those should either go through `/implement` directly or be reviewed/flipped to `ready to ship` first. Note them in output.
- Do not write docs, archive plans, or invoke wiki-side tools (`/wiki-sync`, `/wiki-lint`).
- Do not run lint / typecheck / UI validation — `/review-pr` owns that.
- Report missing or broken lifecycle links. When every acceptance criterion for a phase is complete, update that phase to `status: implemented-pending-pr` unless it already has a later status.
- Always include a **Fix report** in the final output when any auto-fix pass ran (or when gaps were classified and none were obvious).

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

**If everything is `complete`:** proceed to Step 4.

**If anything is `partial`, `missing`, or `unclear`:** proceed to Step 3.5 (obvious-fix loop) instead of stopping.

### Step 3.5 — Obvious-fix loop (when gaps exist)

Classify each non-`complete` finding as **obvious** or **not obvious**.

A gap is **obvious** only when all of the following hold:

- The acceptance criterion and plan paths make the intended change unambiguous.
- The fix is local and mechanical (missing registration/wiring, omitted constant/enum/case already specified in the plan, incomplete mirror of an adjacent existing pattern, wrong field/status name called out by the plan, missing test assertion that copies an existing suite pattern).
- No product, UX, schema-shape, or architectural judgment is required.
- The change stays inside the phase scope and does not invent behavior beyond the criterion.

A gap is **not obvious** when any of these apply: large missing feature surface, multiple valid designs, `unclear` evidence, intentional out-of-scope items, prior-phase dependencies still incomplete, or anything that should go through `/implement` / user confirmation.

Then:

1. Append each classification to the running **Fix report** (fixed / skipped-as-not-obvious / deferred).
2. Apply all **obvious** fixes in the implementation repo(s). Keep edits minimal and criterion-scoped. Do not commit unless the user asked.
3. If at least one obvious fix was applied, re-run **Steps 2–3** on the same phases (one automatic re-evaluation pass).
4. Cap the loop at **one** auto-fix + re-evaluate cycle per `/evaluate` invocation. A second pass of newly discovered obvious gaps is allowed only if the first re-evaluate introduced them as direct fallout of the first fixes; never exceed **two** fix cycles total.
5. After the loop ends:
   - If any `partial` / `missing` / `unclear` remain → stop. Do **not** proceed to Step 4. Output the gap list + Fix report (Step 6 “gaps remain” form).
   - If all criteria are now `complete` → proceed to Step 4.

Do not auto-fix lifecycle frontmatter gaps, wiki links, or `tests.md` open empirical questions — report those only.

### Step 4 — Code-quality pass (only if Step 3 is fully `complete`)

When every acceptance criterion is `complete`, invoke `/simplify` on the changed files to review for reuse, quality, and efficiency unless `/implement` already ran `/simplify` for the same diff. `/simplify` may surface fixable issues — apply or report them per its own rules. Skip this if `/simplify` is not available in this environment.

If this `/evaluate` run applied obvious fixes in Step 3.5, include those files in the `/simplify` scope.

After `/simplify` completes, collect any findings that were **skipped** (valid but out of scope for this PR — e.g. wider refactors, shared utility extractions, type improvements). Write these to `inbox/backlog.md`, appending if the file already exists. **Do not create `plans/<namespace>/<feature-slug>/backlog.md`.**

```markdown
## YYYY-MM-DD — <short title> (from /simplify on <phase-slug>)

- Files: `<file1>`, `<file2>`
- Issue: <what the finding is>
- Suggested fix: <what to do>
- Why deferred: <reason it wasn't fixed in this PR>
```

If there are no skipped findings, do not append.

### Step 5 — Update lifecycle status

For every evaluated phase whose acceptance criteria are all `complete`, update its frontmatter to:

```yaml
status: implemented-pending-pr
```

Do not overwrite later statuses such as implementation `pr-open`, `implemented-and-synced`, or `archived`. Preserve `namespace`, `source_dump`, `artifact_pr`, `related_pr`, and `wiki_log` fields. Do not update the linked source idea here unless the plan explicitly says implementation owns that transition; source idea PR/archive state is normally handled by `/review-pr` and `/wiki-sync`.

### Step 6 — Output

Every final `/evaluate` response must include a **Fix report** section whenever Step 3.5 ran (including when zero obvious fixes were applied).

**Fix report format:**

```markdown
## Fix report
- Cycles: <n> auto-fix + re-evaluate
- Applied:
  - <phase + criterion>: <what changed> (`<files>`)
- Skipped (not obvious):
  - <phase + criterion>: <why left for the user>
- Re-evaluate result: <all complete | gaps remain>
```

If Step 3.5 never ran (no gaps on first pass), omit the Fix report or note `Fix report: none (no gaps)`.

**If gaps remain after the obvious-fix loop:**

- Severity-ordered gap list (plan reference + code location for each gap).
- **Fix report** (what was auto-fixed vs left alone).
- Any `tests.md` open entries that look resolved by the implementation (flag for migration to a Key Design Decision).
- Lifecycle link gaps, including missing `namespace`, missing or broken `source_dump`, artifact-only PRs stored in `related_pr`, missing implementation `related_pr` when a PR exists, or a missing PR body lifecycle section.
- Skipped phases (those still at `status: wip`).
- Recommendation: fix the remaining gaps (or confirm intent for skipped ones), then re-run `/evaluate`. Do not proceed to `/review-pr` yet.

**If ready for /review-pr:**

- Confirmation that all acceptance criteria across `ready to ship` phases are `complete`.
- **Fix report** when any auto-fix pass ran.
- Status updates written, including any phases moved to `implemented-pending-pr`.
- Skipped phases (those still at `status: wip`), if any.
- Summary of `/simplify` results, including a pointer to `inbox/backlog.md` if any skipped items were recorded.
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
- ❌ Auto-implement large or ambiguous missing work (that remains `/implement` or a manual follow-up).

## Repository Map

Read `repos.yaml` at the repo root to resolve sibling repo paths. Do not use hardcoded local paths.
