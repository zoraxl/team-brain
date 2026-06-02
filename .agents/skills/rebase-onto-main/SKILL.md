---
name: rebase-onto-main
description: Rebase the current feature branch onto the configured base branch without merging. Resolves each conflict with AI judgment, auto-resolving obvious cases and asking the user for ambiguous ones. Writes a structured report to the audit folder. Use when the user asks to rebase, /rebase, update branch from main, update branch from base, or sync with main.
---

# Rebase Onto Main

Safely rebase the current branch onto the repository's default remote base branch, with conflict-by-conflict judgment and a final audit report.

## Safety Rules

- Never run `git merge main` or `git pull origin main`.
- Never force-push without explicit user confirmation.
- Never rewrite already-pushed history unless the user confirms.
- Keep the working tree clean before starting.
- If rebase fails or the user wants to stop, offer `git rebase --abort`.

## Workflow

### Phase 1 - Pre-flight checks

1. Confirm a clean tree:

   ```sh
   git status --porcelain
   ```

   If output is non-empty, stop and ask the user to stash or commit first.

2. Capture branch context:

   ```sh
   git branch --show-current
   git symbolic-ref refs/remotes/origin/HEAD
   ```

   Resolve the base branch from `origin/HEAD` unless the user names a different base. If the current branch is the base branch, stop and ask for the feature branch.

3. Sync the base and inspect divergence:

   ```sh
   BASE=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's|refs/remotes/origin/||')
   git fetch origin "$BASE"
   git log --oneline "origin/$BASE..HEAD"
   git log --oneline "HEAD..origin/$BASE"
   ```

4. Summarize what is unique on the branch versus the base, then confirm proceeding.

### Phase 2 - Start rebase

Run:

```sh
git rebase "origin/$BASE"
```

If no conflicts occur, continue to Phase 4. If conflicts occur, continue to Phase 3.

### Phase 3 - Conflict resolution loop

Repeat until rebase completes.

1. List current conflicts:

   ```sh
   git diff --name-only --diff-filter=U
   ```

2. For each conflicted file:
   - Read conflict markers and understand overlapping edits.
   - Collect context:

     ```sh
     git log --oneline -5 -- <file>
     git diff "origin/$BASE...HEAD" -- <file>
     ```

3. Classify each conflict:
   - **Obvious** (auto-resolve): formatting-only differences, non-overlapping intent with accidental context overlap, or one side deleting a block the other side did not semantically change.
   - **Ambiguous** (ask user): both sides changed the same logic in different ways, rename/move plus behavior edits on both sides, or any case with product/behavior trade-offs.

4. Resolve and continue:

   ```sh
   git add <resolved-files>
   git rebase --continue
   ```

5. If a conflict is ambiguous, present:
   - branch intent
   - base intent
   - proposed merged option, if available
   - direct question asking which resolution to choose

### Phase 4 - Post-rebase verification

After rebase succeeds:

```sh
git log --oneline "origin/$BASE..HEAD"
git diff "origin/$BASE...HEAD" --stat
```

Then run the repo-appropriate verification command from local repo docs or `## Repository Scope` if present. If none applies, skip with a note.

Report success/fail/skipped status and remind the user that pushing rewritten history requires explicit confirmation (`git push --force-with-lease`), but do not push automatically.

### Phase 5 - Write audit report

Write a report to:

- `audit/rebase-<branch>-<YYYY-MM-DD>.md`

Use this template:

```markdown
# Rebase Report: <branch> onto <base>
**Date:** YYYY-MM-DD
**Branch:** `<branch>`
**Base:** `origin/<base>` at <short-sha>
**Operator:** AI agent + user review

## Summary
- Commits on branch: N
- Commits on base since divergence: M
- Conflicts encountered: K (N auto-resolved, M user-resolved)
- Build status after rebase: pass/fail/skipped

## Conflict Resolutions

### Conflict 1: `<file>`
**Type:** auto / user-resolved
**Branch intent:** <what the branch was doing>
**Base intent:** <what the base changed>
**Resolution:** <what was chosen and why>

## Post-Rebase Commit History
(output of `git log --oneline origin/<base>..HEAD`)

## Notes
- Any warnings, follow-ups, or observations
```

## Completion Checklist

- [ ] Rebase used (`git rebase origin/<base>`) and no merge from the base branch performed
- [ ] Every conflict resolved with explicit judgment
- [ ] Ambiguous conflicts approved by user
- [ ] Post-rebase verification completed or explicitly skipped
- [ ] Audit report written to `audit/`

## Repository Scope

Replace this section in repo-specific copies with repo-specific verification commands. If none applies, skip and note it in the audit report.
