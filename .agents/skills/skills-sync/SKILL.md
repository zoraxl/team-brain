---
name: skills-sync
description: Admin workflow for auditing and syncing registered agent skills from team-brain across configured repos and agent surfaces. Use when asked to sync skills, install missing registered skills, add a skill to the managed registry, compare skill copies, or update shared/generalizable skill sections while preserving repo-specific customization. This skill should live in the skills-home repo.
allowed-tools: ["Bash"]
---

# Skills Sync

Admin workflow for keeping registered skills consistent across sibling repos without erasing repo-specific customization, then opening one reviewable PR per repo that changed when requested.

This skill should live in the repo marked `skills_home: true` in `repos.yaml`. Do not install `skills-sync` into implementation repos unless the team intentionally makes that repo a skills home.

## Actions

Default action: `sync`.

- `/skills-sync` or `/skill-sync` - run the default sync action for all registered skills.
- `/skills-sync <skill>` - run sync for one registered skill.
- `/skills-sync sync <optional skill>` - explicit form of the default sync action.
- `/skills-sync add <skill>` - add a skill to the registered skills list, then optionally sync it when the source exists.

If the first argument is not a known action, treat it as a skill name for the default `sync` action.

## Registered Skills

Managed skills:

- `review-pr`
- `pr-score-log`
- `rebase-onto-main`
- `create-bug-issue`
- `simplify`
- `lifecycle-audit`

When the user names a skill, sync only that skill. When no skill is named, evaluate all registered skills.

The authoritative admin source is `.agents/skills/<skill>/SKILL.md` in the skills-home repo unless the user explicitly names another source. Mirror updates back to other local surfaces in this repo only if those surfaces exist.

### Add Action

Use `add` when the user wants a new skill to be managed by `skills-sync`.

1. Normalize the requested skill name to kebab-case.
2. Confirm an authoritative source exists at `.agents/skills/<skill>/SKILL.md`, unless the user provides another source path.
3. Add the skill name to the `Registered Skills` list in this file.
4. Mirror the updated `skills-sync` file to other local surfaces if present.
5. If the source exists, run the normal sync workflow for that skill.
6. If the source does not exist, stop after registration only if the user explicitly asked to register a future skill; otherwise ask for the source path.

Do not add `skills-sync` itself to the registered list; it is an admin skill and should stay local to the skills-home repo.

## Repo Targets

Read `repos.yaml` from the skills-home repo and consider sibling repos with local paths that exist on disk.

Default target surfaces per repo:

- `.agents/skills/<skill>/SKILL.md`
- `.codex/skills/<skill>/SKILL.md`
- `.claude/skills/<skill>/SKILL.md`
- `.cursor/skills/<skill>/SKILL.md`

If a repo already uses only a subset of surfaces, preserve that pattern unless the user asks to install every surface. For a missing skill in a repo, create the standard four-surface set unless `repos.yaml` declares a different `skill_surfaces` list.

Every target skill description should identify its repo first when copied outside the skills-home repo. Ensure the frontmatter `description` starts with `(<repo-name>)` in repo-specific copies. Keep the skills-home copy generic.

## Preserve Customization

Treat these as repo-specific sections or values. Do not overwrite them during sync unless the user explicitly asks:

- `## Repository Scope`
- local check commands and CI commands
- base branch names
- repo-specific paths, Makefiles, package managers, Terraform commands, test commands
- checklist items naming those commands
- repo-specific categories
- wording that names the current repo or explains how this repo invokes the skill

Treat these as generalizable sections that should stay aligned across copies:

- frontmatter identity and trigger intent
- workflow structure and step ordering
- GitHub CLI update/create mechanics
- PR title rules
- PR description template shape
- description section guidelines
- scoring guide and output rules
- common mistakes that are not repo-specific
- read-only behavior and user-facing output expectations

If a section mixes shared and repo-specific content, patch only the shared lines.

## Workflow

1. Read `repos.yaml` and confirm you are operating from the skills-home repo.
2. Build the target matrix: registered skill x repo x available or desired surfaces.
3. For each skill, read the authoritative source and all target copies.
4. Classify each difference as one of:
   - `missing` - skill copy does not exist.
   - `generalizable drift` - shared section differs from the source.
   - `repo customization` - target differs for valid repo-specific reasons.
   - `conflict` - unclear whether a difference is shared or repo-specific.
5. Install missing copies by creating `skills/<skill>/SKILL.md` under the target surfaces and copying the authoritative source, then add or preserve a `## Repository Scope` section for that repo when the skill supports repo-specific behavior.
6. Patch generalizable drift only. Preserve repo customization.
7. For conflicts, stop and ask the user before editing that hunk.
8. Mirror any changed skills-home `.agents` admin source to other local surfaces if present.
9. If the user asked for PRs, create one dedicated branch/commit/PR per repo that changed.
10. Report what changed, what was intentionally left untouched, and the PR URL for each updated repo.

## PR Creation

Create PRs only for repos that this skill actually changed and only when the user asked this skill to open PRs.

For each updated repo:

1. Read `git status --short` and separate skill-sync changes from unrelated user work.
2. Create a branch named `skills-sync/<short-skill-or-date>` unless already on a suitable branch created for this sync.
3. Stage only files changed by this sync. Do not stage unrelated local changes.
4. Commit with a concise message such as `chore: sync agent skills`.
5. Push the branch with upstream tracking.
6. Open a PR with a clear title and body.

PR body template:

```markdown
## Summary
- Sync registered agent skills for this repo.
- Preserve repo-specific skill customization.

## Validation
- Confirmed updated skill files are present.
- Checked `git status --short` for unrelated local changes.
```

If a repo has unrelated local changes, mention them only if they remain unstaged and could affect review context. If a repo cannot create a PR because of authentication, branch conflicts, missing remote, or ambiguous dirty state, stop for that repo and report it under **Needs Review** without forcing through.

## Output

Provide a concise report:

```markdown
## Skills Sync Report

### Installed
- `<repo>`: `<surface>/skills/<skill>/SKILL.md`

### Updated
- `<repo>`: synced shared sections for `<skill>`

### Preserved
- `<repo>`: kept repo-specific `<section or command>`

### Needs Review
- `<repo>`: `<conflict summary>`

### Pull Requests
- `<repo>`: `<PR URL>`
```

## Guardrails

- Never delete a skill copy unless the user explicitly asks.
- Never overwrite repo-specific commands just because they differ from the source.
- Do not install this `skills-sync` skill outside the skills-home repo unless requested.
- Respect dirty worktrees. Read `git status --short` before editing a repo and mention unrelated existing changes in the final report.
- Never include unrelated local changes in a skills-sync commit or PR.
- Do not force-push, amend published commits, or bypass hooks unless the user explicitly requests it.
- Prefer small patches over wholesale replacement when a target skill already exists.
