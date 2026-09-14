---
name: review-pr
description: Run pre-PR validation (lint/format/typecheck/UI), detect linked issues, generate the PR package (title, description, change breakdown, score), and apply it to GitHub. Lifecycle-stamp-only PRs may be merged after an explicit user confirmation; never auto-merge other PR types. Works with a PR number or the current branch's committed changes vs its base. Invokable from any repo. Use when the user says "/review-pr", "review my pr", "write a pr", "summarize a pr", "score my pr", "prepare a pr for submission".
version: 3.1.0
allowed-tools: ["Bash"]
triggers:
  - "review.{0,10}(my.{0,5})?(pr|pull.?request|changes|diff)"
  - "score.{0,10}(my.{0,5})?(pr|pull.?request|changes|diff)"
  - "rate.{0,10}(my.{0,5})?(pr|pull.?request|changes|diff)"
  - "analyse.{0,10}(my.{0,5})?(pr|pull.?request|changes|diff)"
  - "analyze.{0,10}(my.{0,5})?(pr|pull.?request|changes|diff)"
  - "grade.{0,10}(my.{0,5})?(pr|pull.?request|changes|diff)"
---

# Review PR

Validate, package, and apply a PR. Owns lint / format / typecheck / UI checks. Does **not** detect ADR drift — ADRs are created or updated post-merge by `/wiki-sync`. Does **not** check code against the plan — that is `/evaluate`'s responsibility (run before this skill).

Workflow position:

```
/brainstorm → /planning → /implement → /evaluate → /review-pr → merge → /wiki-sync
```

Invokable from any repo. The skill resolves repo paths via `repos.yaml` at the wiki repo root when needed.

---

## Step 1 — Determine the diff source

**Option A — PR number/URL provided:**

```bash
gh pr view <number> --json title,body,baseRefName,headRefName,files,labels,state,closingIssuesReferences
gh pr diff <number>
```

**Option B — No PR number (use current branch):**

```bash
BASE=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's|refs/remotes/origin/||')
git branch --show-current
git log --oneline origin/$BASE..HEAD
git diff origin/$BASE...HEAD
```

Read every file in the diff before continuing.

### Lifecycle-stamp-only detection

Before continuing to validation and the scored PR package, classify whether this PR is **lifecycle-stamp-only**.

A PR is lifecycle-stamp-only when **all** of the following hold:

1. Every changed file is a lifecycle-bearing markdown path (`plans/…`, `inbox/…`, `archive/…`, or other plan/source/strategy docs with lifecycle frontmatter).
2. Every substantive diff hunk only updates lifecycle frontmatter fields such as `status`, `related_pr`, `artifact_pr`, `wiki_log`, `archive_after`, `archived_from`, `archived_at` — not plan body, brainstorm content, skill code, product code, or other deliverables.
3. Optionally reinforced by commit subjects like `Stamp lifecycle metadata for PR #…`.

If the PR mixes stamp fields with any deliverable content (implementation, artifact body, skill/workflow changes), it is **not** stamp-only — continue with the normal Steps 2–6 template.

**When lifecycle-stamp-only:**

- Skip Step 2 validation (no lint/format/typecheck/UI gate).
- Skip Step 3 linked-issue prompting (do not ask about closing issues; carry an existing `Closes #N` only if already present).
- Skip the scored Step 5 **PR Description Template** (no PR Details / Testing / Change Breakdown / Total Score).
- Resolve the Lifecycle links from Step 3.5 only as needed to fill the stamp template, then jump to **Step 5b — Lifecycle stamp PR package**, then apply via Step 6.
- After Step 6 apply, run **Step 6.4**: alarm the user and merge only after an explicit `yes`. Never auto-merge any other PR type.
- Do not invent Feature/Fix/Test categories or effort scores for stamp-only PRs.
- If this stamp-only run is only refreshing metadata already pointed at an existing implementation/artifact PR URL, keep that URL in the body; do not treat the stamp PR as a new deliverable.

---

## Step 2 — Run validation

Validation runs against the **current working tree** before the PR is created or updated. If validation fails, stop — fix and re-run.

**Skip Step 2** when the user only wants a read-only summary of an existing PR (Option A, no apply step), **or** when the PR is lifecycle-stamp-only (see Step 1). Note in the output that local validation was not run.

### Choosing commands

Run the implementation repo's standard validation. Always check the repo's `CLAUDE.md`, `AGENTS.md`, or `README.md` first for the canonical validation commands.

| Repo type | Default commands |
|-----------|------------------|
| TypeScript / Node monorepo | `pnpm lint`, `pnpm format`, `pnpm typecheck` (or `turbo typecheck`) |
| Python service | Run the local `Makefile` targets (`make lint`, `make typecheck`, `make test`) |
| Docker / Compose service | Repo-root validation per the local README; typically a compose config check |
| Wiki / markdown-only (this repo) | No automated validation; skip Step 2 |

The table is a fallback, not the source of truth.

### UI changes

For UI changes, start the dev server and verify the feature in a browser. Test the golden path and key edge cases. Watch for regressions in nearby features. Type checking and tests verify code correctness, not feature correctness — if you can't test the UI, say so explicitly in the PR description rather than claiming success.

### On failure

If any check fails:

- **Stop.** Do not proceed to Step 3.
- Summarize the failure for the user (which command, which file/line, what error).
- Recommend running `/evaluate` if the failure looks like a planning gap, or fixing directly otherwise.
- Re-run `/review-pr` after the user fixes.

---

## Step 3 — Detect linked issue

**Skip Step 3** when the PR is lifecycle-stamp-only, except to preserve an existing closing reference already in the PR body.

Auto-detect first. Look for an issue number reference in this order:

1. **Head branch name** — patterns like `fix-123-...`, `issue-123-...`, `123-foo-bar`.
2. **Commit messages** on the branch — search for `#NNN` references.
3. **Existing PR body** — look for `Closes #NNN`, `Fixes #NNN`, `Resolves #NNN`.

If a closing reference is found, carry it through into the new PR body unchanged.

If nothing is detected:

```bash
gh issue list --state open --limit 10 --json number,title,labels
```

Show the list and ask:

> **Does this PR resolve any of these issues?** Reply with the issue number, a comma-separated list of numbers, or `none`.

For each chosen number, add `Closes #N` to the Summary block of the PR description. If `none`, skip — no closing reference is added.

GitHub auto-closes the linked issue when the PR merges; do not comment on or label the issue from this skill.

---

## Step 3.5 — Detect lifecycle plan

For implementation or workflow work that came from `/planning`, resolve the lifecycle links before generating the PR package:

1. Find the plan path from the branch, commits, changed files, or user-provided context. Expected shapes: `plans/<namespace>/<feature>/<phase>.md` for a single phase or `plans/<namespace>/<feature>/` for a full linked plan folder.
2. If a folder is named, list its phase files and determine whether the PR intentionally submits the full folder or only specific phases. Use the diff, `/evaluate` output, user-provided context, and plan frontmatter. If phase scope is ambiguous, ask before stamping.
3. Read the plan frontmatter and resolve `source_dump`.
4. Resolve the source idea from plan `source_dump` first, then a source idea whose `related_plan` points to the plan path/folder, then user confirmation.
5. If no plan path is found, ask the user for the plan path or `none`.
6. If no source idea exists, record `Source idea: none`; do not invent one.
7. Classify the PR lifecycle type before stamping:
   - `implementation` — the PR submits the actual code, workflow, wiki behavior, skill behavior, or repo metadata deliverable described by the plan.
   - `artifact` — the PR only lands brainstorms, plans, strategy docs, source material, or planning cleanup. It does not implement the linked deliverable.
   - `mixed` — the PR both implements a deliverable and lands source artifacts.

   Use the diff, PR title/body, changed paths, `/evaluate` output, and user context. Brain-native workflow changes in the brain repo can be implementation PRs when the plan is about workflow/skill/wiki behavior. A PR that only commits brainstorms, plan specs, lifecycle metadata, or other source artifacts is `artifact` even when those files reference implementation work. If there is no clear implemented deliverable in the diff, default to `artifact`; if the lifecycle type is still ambiguous, ask the user to choose `artifact`, `implementation`, or `mixed` before stamping.

Carry these values into the PR body so `/wiki-sync` can follow the merged PR back to its source material:

```markdown
## Lifecycle

- Plan: `{plan_path_or_none}`
- Source idea: `{source_idea_path_or_none}`
- Lifecycle scope: `{single phase | full linked plan folder | none}`
- Implementation scope: `{phase/file/folder implemented | none}`
- Artifact scope: `{brainstorm/plan/strategy/source artifacts submitted | none}`
- Lifecycle metadata: `{stamped | not stamped - <reason>}`
```

Lifecycle status contract:

- `ready to ship` means a plan phase was reviewed and can be implemented.
- `implemented-pending-pr` means implementation/evaluation found the phase complete before PR submission.
- `pr-open` is written by `/review-pr` only for implementation or workflow-deliverable PRs after the PR URL can be stamped into `related_pr`.
- `artifact_pr` is written for PRs that only land brainstorms, plans, strategy docs, source artifacts, or planning cleanup; it must not advance source ideas or plan phases to `pr-open`.
- Never set `status: pr-open` merely because the plan or source file itself is included in the PR. Plans/source files included without an implemented deliverable keep their existing work-state status and receive only `artifact_pr`.
- Source ideas should move to PR state only when an implementation PR covers the full linked idea/plan chain; partial phase PRs and artifact PRs keep the source idea active.
- Preserve existing `related_plan` and `source_dump` links. Do not rewrite them opportunistically during PR prep.
- `/review-pr` does not archive source or plan files. `/wiki-sync` owns post-merge archive.

After the PR URL exists, update lifecycle frontmatter before finalizing the PR body:

- For an `implementation` or `mixed` PR, set each implemented/submitted plan phase:
  ```yaml
  status: pr-open
  related_pr: <PR URL>
  ```
- For an `artifact` PR, do not change the work-state `status`; set `artifact_pr: <PR URL>` on submitted source/plan files instead.
- For a `mixed` PR, stamp `related_pr` only on the implemented lifecycle scope and stamp `artifact_pr` on artifact-only source/plan files.
- For a source idea, set `status: pr-open` and `related_pr: <PR URL>` only when an implementation PR submits the full linked idea/plan chain. If this is a partial phase PR or artifact-only PR, leave the source idea active and note that in `Lifecycle metadata`.
- If an artifact-only PR would otherwise be the only evidence behind an existing `status: pr-open`, treat that as a lifecycle metadata error: do not reinforce it. Correct the file back to `wip` or `ready to ship` when the prior intended status is clear from the plan/review context; otherwise stop and ask the user which active status to restore.
- Preserve `related_plan`, `source_dump`, `artifact_pr`, `related_pr`, `wiki_log`, and archive fields that already exist unless the lifecycle classification says to update one of the PR fields.
- Do not stamp sibling phases merely because they share a folder.

If there are no lifecycle files to update, set `Lifecycle metadata: not stamped - <reason>` in the PR body. Do not archive or update wiki pages from this skill; `/wiki-sync` owns that after merge.

---

## Step 4 — Analyze the diff

Read every file in the diff. Understand:

- **What** changed (new features, refactors, bug fixes, wiki updates, etc.)
- **Why** it changed (motivation, gap being addressed)
- **How** it was done (structure, key patterns, cross-links)

Group changes into logical items for the change breakdown table in Step 5.

---

## Step 5 — Generate the PR package

If the PR is lifecycle-stamp-only (Step 1), **do not use** the scored PR Description Template below — use **Step 5b** instead.

Produce exactly **two copy-pasteable blocks**:

1. **PR Title** — single-line code block.
2. **PR Description** — fenced code block with the full PR body.

### PR Title Rules

- Maximum 72 characters.
- Imperative mood ("Add …", "Fix …", "Update …", "Clarify …").
- Specific — mention the feature, area, or component.
- No trailing period.
- No generic titles like "Update docs" or "Fix stuff".
- Lifecycle-stamp-only titles should follow Step 5b (e.g. `Stamp lifecycle metadata for <phase/feature>`).

### PR Description Template

Use this template only for normal implementation, artifact, or mixed PRs — **not** for lifecycle-stamp-only PRs.

```
## PR Details

### Summary

**Summary:** <!-- 1-2 sentences high level -->
{summary}

{closes_reference_if_any}

**Motivation:** <!-- Why is this change needed? -->
{motivation}

**Approach:** <!-- How was it implemented? Key decisions and trade-offs. -->
{approach}

**Impact:** <!-- Effect on users, decisions, or cross-repo understanding -->
{impact}

{lifecycle_block_if_any}

**Changes:** <!-- Bullet list of key changes -->
{changes_as_bullet_list}

## Testing

{testing_description}

### Test Evidence

{validation_output_summary_from_step_2}

**Checklist:**

- [ ] Self-review completed
- [ ] Validation commands pass (lint, format, typecheck, UI as applicable)
- [ ] Linked issue verified (or none required)

---

### Change Breakdown

| # | Category | Description | Files Changed | Score |
|---|----------|-------------|---------------|-------|
| 1 | category | what changed and why | list of files | n/10 |

**Verdict:** {one-sentence scope assessment}

**Total Score: {sum}/{max}**

**Summary:**
1. **What** — {2-3 sentences on what this PR does}
2. **Why** — {motivation}
3. **How** — {key implementation details worth noting}
```

If `/evaluate` ran in the same session and produced an acceptance-criteria checklist, paste a condensed version of it into the **Test Evidence** block above the validation output.

### Change Breakdown Categories

#### For implementation repos

| Category | Signals |
|----------|---------|
| **Feature** | New user-visible or system-visible capability |
| **Fix** | Bug fix or regression repair |
| **Refactor** | Internal restructure without behavior change |
| **Test** | New or updated tests |
| **Config / Infra** | Build, deploy, environment, dependency changes |
| **Docs** | Documentation, comments, README |

#### For wiki repos

| Category | Signals |
|----------|---------|
| **New concept / decision** | New ADR, product idea in stable form, CONCEPT.md change |
| **Cross-links & structure** | wiki/index.md updates, hub pages, navigation between pages |
| **Source alignment** | repos.yaml changes; tracing claims; authority map |
| **Lint / maintenance** | Stale metadata, index coverage, small consistency fixes, log append |
| **Housekeeping** | Typos, formatting-only, trivial link fixes |

### Effort Scoring Guide

| Score | Meaning |
|-------|---------|
| 1–2 | Trivial / housekeeping — no meaningful change |
| 3–4 | Small clarification or local fix |
| 5–6 | Meaningful addition or restructure |
| 7–8 | Significant new durable knowledge or feature |
| 9–10 | Foundational — binding decision, full architecture change |

`max` = number of categories × 10. List categories in descending order of score.

### Step 5b — Lifecycle stamp PR package

For lifecycle-stamp-only PRs, produce exactly **two** copy-pasteable blocks using this lighter template. Do **not** include Change Breakdown, effort scores, Testing, or Test Evidence.

**PR Title** (≤72 chars, imperative):

```
Stamp lifecycle metadata for {phase_or_feature}
```

**PR Description:**

```
## Lifecycle stamp

**Summary:** Stamp lifecycle frontmatter only — no implementation or artifact deliverable in this PR.

{closes_reference_only_if_already_present}

## Lifecycle

- Plan: `{plan_path_or_none}`
- Source idea: `{source_idea_path_or_none}`
- Lifecycle scope: `{single phase | full linked plan folder | none}`
- Implementation scope: `none (stamp only)`
- Artifact scope: `none (stamp only)`
- Lifecycle metadata: `{stamped | not stamped - <reason>}`

**Fields updated:**

- `{path}`: `{field}={value}` …
```

Keep the body short. List each stamped file and the fields changed. If the stamp points at an existing deliverable PR, mention that URL in the fields list (`related_pr` / `artifact_pr`) rather than rewriting this PR as the deliverable.

---

## Step 6 — Apply to GitHub and stamp lifecycle metadata

Immediately apply the PR package. Do **not** ask for confirmation to create or update the PR. Lifecycle stamping is part of applying the PR, not a separate optional cleanup. Merge is different: only lifecycle-stamp-only PRs may be merged by this skill, and only after Step 6.4's explicit confirmation.

For lifecycle-stamp-only PRs, apply the Step 5b body. If the branch already contains the stamp commit and frontmatter is complete, create/update the PR and set `Lifecycle metadata: stamped` without inventing a second stamp commit. Do not replace an existing deliverable PR body with the stamp template when this run is only appending a stamp commit onto that deliverable PR — keep the scored/full body and only refresh the `## Lifecycle` section.

### Step 6.1 — Create or update the PR

**If a PR already exists (PR number is known):**

```bash
BODY_FILE=$(mktemp)
trap 'rm -f "$BODY_FILE"' EXIT
cat > "$BODY_FILE" <<'PRBODY'
<description>
PRBODY
gh api repos/{owner}/{repo}/pulls/<number> --method PATCH \
  --field title="<title>" \
  --field body=@"$BODY_FILE" \
  --jq '.html_url'
```

**If no PR exists yet (working from current branch):**

```bash
git push -u origin HEAD
BODY_FILE=$(mktemp)
trap 'rm -f "$BODY_FILE"' EXIT
cat > "$BODY_FILE" <<'PRBODY'
<description>
PRBODY
gh pr create --title "<title>" --body-file "$BODY_FILE"
```

After applying, check for auto-appended footers (e.g., "Made with Cursor"). If present, re-apply with the clean body.

### Step 6.4 — Lifecycle-stamp-only merge (confirmation required)

This step exists **only** for PRs classified as lifecycle-stamp-only in Step 1. Implementation, artifact, mixed, and any PR with deliverable content must never be merged by `/review-pr`, even if the user asks in the same turn.

Skip this step when the user only wanted a read-only summary (Option A, no apply).

**Hard stop.** After Step 6.1, do not merge yet. Show this alarm and wait for an explicit yes/no:

```
ALARM — this will merge to the base branch.

This PR is classified as lifecycle-stamp-only (frontmatter metadata only).
`/review-pr` can merge stamp-only PRs after you confirm.
Implementation, artifact, mixed, and any PR with deliverable content are never auto-merged by this skill.

PR: {url}
Base: `{baseRefName}`
Files:
- `{path}`: {fields}

This lands on `{base}` immediately, or via GitHub auto-merge if required checks are still running. It cannot be undone from this skill.

Merge this stamp-only PR now? Reply `yes` to merge, or `no` to leave it open.
```

Confirmation rules:

- Stop and wait. Do not merge in the same turn as the first `/review-pr` invocation, even if the user said "merge it" up front. They must see the alarm and the file list first.
- Treat only a clear `yes`, `merge`, or `merge it` in the reply to this alarm as consent. `ok`, `looks good`, `continue`, `ship it`, `lgtm`, and silence are **no**.
- If the user replies `no`, leave the PR open and report the URL. Do not ask again in this run.
- If classification was borderline, do not offer merge. Leave the PR open and say why.
- If the user replies `yes`, re-verify stamp-only classification against the final pushed diff before merging. If the diff is no longer stamp-only, refuse to merge and say so.

Merge commands after an explicit `yes` (never `--admin`, never bypass required checks):

```bash
# If the PR is mergeable now:
gh pr merge <number> --squash --delete-branch

# If required checks are still running:
gh pr merge <number> --auto --squash --delete-branch
```

If merge or auto-merge fails, report the PR URL and the blocking reason. Do not retry with admin override.

After a successful merge or auto-merge enablement, report the URL and the merged / auto-merge state. Do not run `/wiki-sync` from this step. A stamp-only PR is not the deliverable; wiki-sync the implementation or artifact PR it points at, if any.

---

## Common Mistakes

- **Skipping validation** — Step 2 is a hard gate for normal PRs. Do not generate the scored PR package if validation fails. Lifecycle-stamp-only PRs intentionally skip Step 2.
- **Scoring a lifecycle stamp** — stamp-only PRs must use Step 5b, not the scored Change Breakdown / Total Score package.
- **Merging a non-stamp PR** — `/review-pr` never merges implementation, artifact, mixed, or unclassified PRs.
- **Merging a stamp PR without an explicit yes** — the Step 6.4 alarm is a hard stop. Do not treat apply-step "do not ask" as merge consent.
- **Classifying mixed diffs as stamp-only to unlock merge** — if any hunk is not a lifecycle frontmatter field, it is not stamp-only and must not be merged by this skill.
- **Scoring by length** — a long reformat that doesn't change behavior stays 1–2.
- **Merging unrelated edits** — keep change breakdown categories distinct.
- **Including uncommitted changes** — only committed work is in scope.
- **Forgetting the three-dot diff** — use `origin/<base>...HEAD` for branch comparisons.
- **Inventing implementation detail** — flag uncertainty instead of speculating.
- **Re-running ADR drift checks** — that work moved to `/wiki-sync` post-merge. If you find yourself reading `wiki/decisions/` from this skill, stop.
