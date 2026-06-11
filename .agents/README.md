# Agent Skills

This package includes reusable skills for maintaining an LLM-friendly cross-repo wiki and running an agent-driven development workflow on top of it. Each skill lives in `.agents/skills/<skill-name>/SKILL.md`.

Agents should use these skills when the user's request matches the skill description, or when the user names the skill directly.

## Included Skills

### Setup

| Skill | Use When |
|---|---|
| `setup-brain` | One-time (re-runnable) onboarding to this template. New-brain mode walks the customization checklist (repos.yaml, namespaces, zones, placeholders); existing-brain mode runs a report-first migration of an existing wiki into the template structure. Installs skill copies into the agent surfaces the team uses (`.claude/skills/`, `.cursor/skills/`, `.codex/skills/`, or custom) and records them in `repos.yaml` `skill_surfaces`. Lives only in the brain repo; never synced to implementation repos. |

### Idea → Planning

| Skill | Use When |
|---|---|
| `brainstorm` | Exploring a problem or idea before committing to a plan. Surfaces goals, constraints, options, and open questions. Saves to `inbox/dump/` on request. |
| `planning` | Turning an implementation intent (or a `brainstorm` output) into one or more detailed phase specs in `plans/<namespace>/<feature-slug>/`. Three-phase gate: (1) propose breakdown and pause, (2) write specs at `status: wip`, (3) optionally flip a phase to `status: ready to ship` after review when the user wants to implement manually. |

### PR Workflow

| Skill | Use When |
|---|---|
| `implement` | Implements phase plans in the target repo resolved through `repos.yaml`. Can run directly on `wip` plans by resolving open questions with the user one by one before coding, then runs `/simplify` and marks the phase `implemented-pending-pr`. |
| `simplify` | Scoped post-implementation code-quality pass that preserves behavior while improving clarity, reuse, performance, and maintainability. |
| `evaluate` | Pre-PR gate, especially for phases the user implemented manually. Reads `plans/<namespace>/<feature-slug>/`, maps each acceptance criterion to code, reports `complete` / `partial` / `missing` / `unclear`, and marks complete phases `implemented-pending-pr`. Skips phases still at `status: wip`. Does **not** run lint/typecheck/UI; does **not** touch the wiki. |
| `review-pr` | Pre-merge. Runs the repo's validation commands (lint, format, typecheck, UI as applicable). Auto-detects a linked GitHub issue. Classifies the PR as `implementation`, `artifact`, or `mixed` and stamps `related_pr`/`artifact_pr` lifecycle metadata accordingly. Writes the PR title, body, change breakdown, and total score, then applies via `gh`. No ADR drift detection — that work moved to `/wiki-sync`. Invokable from any repo. |
| `wiki-sync` | Post-merge sync. **PR mode**: creates the ADR (or flips an existing one to `accepted`), updates affected wiki pages, appends a log entry, records in `synced-prs.md` (idempotent), and archives matching lifecycle files. **Doc mode**: ingests existing implemented knowledge from a file path. |
| `create-bug-issue` | Captures a bug in the appropriate GitHub repo with the `bug` label. |
| `pr-score-log` | Lists merged PRs and the `review-pr` total score from each PR body. |
| `rebase-onto-main` | Safely rebases a feature branch onto the configured base branch and writes an audit report. |

### Wiki Retrieval & Maintenance

| Skill | Use When |
|---|---|
| `wiki-query` | Read-only. Searches wiki pages, ADRs, and `repos.yaml`. Checks `inbox/open-questions.md` and `inbox/claims.md` for unresolved items. Cites sources and distinguishes stable knowledge from uncertainty. |
| `wiki-lint` | Audits wiki health. Flags inbox-shaped pages in `wiki/`, dangling links, stale `Last reviewed` dates, missing backlinks, mixed-namespace or wrong-zone pages, `repos.yaml` feeds that don't resolve, and engineering pages missing runbook links. |
| `wiki-adr` | Creates or amends an ADR for an ad-hoc decision that didn't go through the normal `/planning → /wiki-sync` flow. In the standard flow, `/wiki-sync` creates the ADR post-merge. |
| `wiki-runbook` | Documents cross-repo operational procedures, debugging playbooks, recovery steps, or incidents into the zone-appropriate runbook pages (shared substrate goes to `wiki/platform/engineering/`). |

### Workflow Learning

| Skill | Use When |
|---|---|
| `workflow-from-chats` | Mining recent chats or pasted excerpts for durable workflow preferences. Routes each finding to the right artifact: skill update, wiki/runbook note, planning/spec guidance, inbox follow-up, or no change. |
| `lifecycle-audit` | Report-first cleanup for old brainstorms, plans, PR evidence, archives, and sync logs. Applies changes only after explicit approval. |
| `skills-sync` | Admin workflow for syncing registered skills from this repo to configured agent surfaces while preserving repo-specific customization. |

### Typical Workflow Sequence

```
/brainstorm → /planning → /implement → /evaluate → /review-pr → merge → /wiki-sync
```

Each skill owns one verb: **/implement** resolves questions and writes code from a plan, **/evaluate** verifies manually implemented work (code ↔ plan), **/review-pr** validates and packages (lint/typecheck/UI + PR title/body/score), **/wiki-sync** ingests (ADR + wiki pages + lifecycle archive).

For ongoing inbox hygiene, skim `inbox/fragments.md` periodically and `/brainstorm` promising ideas (or delete dead ones). Use `/workflow-from-chats` when repeated chat feedback should become durable workflow guidance. For periodic health, run `/wiki-lint`.

Use `/lifecycle-audit` for historical cleanup that predates the lifecycle metadata model. Use `/skills-sync` only from the skills-home repo, usually this repo.

## General Guidance

- Read only the skill needed for the task.
- Start with `CONCEPT.md`, `repos.yaml`, and `wiki/index.md` when the skill asks for them.
- Preserve source authority; wiki pages synthesize, source docs remain authoritative.
- Prefer links and concise summaries over copying source docs wholesale.
- Track uncertainty in `inbox/open-questions.md`.
- Track unsupported but important assertions in `inbox/claims.md`.
- Append meaningful maintenance entries to `wiki/logs/index.md`.
- Update `wiki/index.md` when adding a new page.
- Update `repos.yaml` when introducing a new authoritative source.

## Installing In Another Agent Environment

`.agents/skills/` is the canonical source, but agent tools do not read it directly — they discover skills from their own directories. This repo ships with `.claude/skills/`, `.cursor/skills/`, and `.codex/skills/` pre-populated as mirrors, so Claude Code, Cursor, and Codex pick the skills up immediately. Run `/setup-brain` to prune mirrors for tools the team doesn't use or to add a custom surface; it records the chosen surfaces in `repos.yaml` under `skill_surfaces` so `/skills-sync` can manage drift afterwards. You can also copy the folders manually.

If your tool uses a different directory convention, keep each skill folder intact:

```txt
wiki-query/
└── SKILL.md
```

The `name` and `description` frontmatter fields are the discovery surface. Keep them clear and generic when adapting this package for a team.
