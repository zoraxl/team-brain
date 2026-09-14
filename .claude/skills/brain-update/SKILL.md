---
name: brain-update
description: >-
  Discover sibling git repos from repos.yaml, the current workspace, and the
  local filesystem, then sync each local default branch with origin. On a
  feature branch, update local main first and only rebase after the user
  confirms. Use when the user says "brain-update", "/brain-update",
  "sync all repos", "pull main everywhere", or "update local mains from origin".
---

# Brain Update

Brain-only workflow. Lives only in the skills-home brain repo (the repo marked `skills_home: true` in `repos.yaml`):

- `.agents/skills/brain-update/SKILL.md`
- `.codex/skills/brain-update/SKILL.md`
- `.claude/skills/brain-update/SKILL.md`
- `.cursor/skills/brain-update/SKILL.md`

Do not install into implementation repos. Do not open PRs. Do not push.

## What this does

1. Pull every repo listed in `repos.yaml` (and extra workspace/sibling checkouts that belong to the same GitHub orgs). If the repo is on its default branch, pull or rebase that branch onto origin.
2. If it is on a feature branch, still update local main from origin, but ask the user if they want to rebase after everything is done.
3. If they want to rebase, rebase the feature branch onto the newly synced local main.

## Guardrails

- Never `git merge` main. Never `git rebase -i`. Never force-push.
- Never skip hooks. Never update git config.
- Never stash, commit, or switch the user's current branch away from where they started.
- Never force-update local main if it has commits that origin/main does not have.
- Dirty worktree on the default branch: skip that repo's pull; still sync other repos.
- Dirty worktree on a feature branch: still update local main (ref only). Do not rebase until the tree is clean.

## Workflow

### Phase 1 — Sync every local main

From the brain repo, run the helper (needs network):

```bash
python3 .agents/skills/brain-update/scripts/sync_mains.py \
  --workspace <each Cursor workspace root>
```

Pass every workspace folder as `--workspace`. The script reads `repos.yaml` and also includes extra workspace git roots whose origin org matches a real `github:` org in that catalog. Placeholder orgs such as `<org>` are ignored.

If the script is missing, do the same steps by hand from the commands in `scripts/sync_mains.py` — do not skip repos because the helper failed to import.

The script:

1. Resolves repos from `repos.yaml` `local_path`, workspace roots, and sibling directories named like catalog entries.
2. Skips missing paths. Reports them under **Not found**.
3. `git fetch origin` in each found repo.
4. **On the default branch** (`main` or whatever `origin/HEAD` is): `git pull --rebase origin <default>` when the tree is clean.
5. **On a feature branch** (or detached HEAD): fast-forward local `<default>` with `git fetch origin <default>:<default>` without checking out main.
6. Stays on the branch the user already had checked out.

### Phase 2 — Report, then ask about rebase

Show the script report. Then stop.

If any found repo is on a non-default branch and local main synced (or was already current):

- List those repos with branch name, dirty/clean, and how many commits they are behind/ahead of local main.
- Ask **after all main syncs finish**, not per repo during the fetch loop.
- Use AskQuestion when available. Options:
  - Rebase all clean feature branches onto local main
  - Rebase none
  - Let me pick (follow up with the repo list)

Do not rebase until the user answers. If they say none, stop after the report.

Skip the question when every found repo is already on its default branch.

### Phase 3 — Rebase confirmed feature branches

For each repo the user selected, in that repo, on the existing feature branch:

1. If the worktree is dirty, skip and say so. Do not stash.
2. Confirm local main exists and was synced this run (or was already equal to origin).
3. Rebase onto **local** main, not a merge:

   ```bash
   git rebase main
   ```

   Use the actual default branch name if it is not `main`.
4. If conflicts occur, follow `.agents/skills/rebase-onto-main/SKILL.md` Phase 3 in that repo (or that repo's `rebase-onto-main` copy). Auto-resolve obvious conflicts; ask on ambiguous ones. Offer `git rebase --abort` if they want to stop.
5. After a successful rebase, show `git log --oneline main..HEAD`. Remind them that rewriting a pushed branch needs an explicit `git push --force-with-lease` — do not push.

Do repos one at a time so conflicts stay isolated.

## Output

```markdown
## Brain Update

### Main sync
- `<repo>` (`<branch>`): <fast-forwarded | already current | pulled with rebase | skipped: dirty | failed: …>

### Not found
- `<repo>`: looked in `<paths>`

### Rebase
- asked: yes/no
- `<repo>` (`<branch>`): <rebased onto local main | skipped | conflict — aborted | not requested>
```

## Common invocations

- `/brain-update`
- `/brain-update` with extra `--workspace` paths already in the session
- User says "pull main in all repos" or "sync local mains"
