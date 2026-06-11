# Team-Brain

A reusable, LLM-friendly internal wiki **and agent-driven workflow** for teams that need a durable cross-repo knowledge store.

This repository is the synthesis layer. Repo-local docs remain authoritative for implementation details; this wiki explains how the product concept, systems, engineering operations, decisions, and unresolved questions fit together — and the included agent skills run a full development loop on top of it.

**Rule: [`wiki/`](wiki/) contains only decided and implemented knowledge. Pre-implementation material lives in [`inbox/`](inbox/).**

Start here:

- [CONCEPT.md](CONCEPT.md) — wiki model, principles, and maintenance rules
- [repos.yaml](repos.yaml) — machine-readable source of truth for all team repos, ownership, and source→wiki mappings
- [wiki/index.md](wiki/index.md) — wiki table of contents
- [wiki/logs/](wiki/logs/) — latest wiki maintenance logs
- [inbox/](inbox/) — fragments, open questions, claims, threads, and brainstorm dumps
- [.agents/README.md](.agents/README.md) — reusable agent skills and usage guidance

## Repository Layout

```txt
team-brain/
├── CONCEPT.md
├── repos.yaml
├── sources/
│   └── index.md                    # human-readable source map (companion to repos.yaml)
├── inbox/
│   ├── chats.md
│   ├── fragments.md
│   ├── screenshots.md
│   ├── open-questions.md
│   ├── claims.md
│   ├── backlog.md
│   └── threads.md
├── plans/                          # active phase specs from /planning
│   └── _template/
│       └── phase-N.md
├── archive/                        # completed lifecycle material by namespace (created lazily)
│   └── <namespace>/
│       ├── ideas/YYYY-MM/
│       └── plans/YYYY-MM/
├── .agents/
│   ├── README.md
│   └── skills/                     # canonical skill source
├── .claude/skills/                 # mirror for Claude Code (managed by /skills-sync)
├── .cursor/skills/                 # mirror for Cursor
├── .codex/skills/                  # mirror for Codex
└── wiki/
    ├── index.md
    ├── logs/
    │   ├── index.md
    │   └── synced-prs.md
    ├── decisions/                  # ADRs under decisions/<zone>/, global numbering
    ├── product/                    # example product zone — rename to your first namespace
    ├── platform/                   # shared implementation substrate (incl. engineering/)
    └── general/                    # team workflow knowledge (created lazily)
```

Wiki pages are routed into **zones**: one `wiki/<namespace>/` zone per product/domain, `wiki/platform/` for implementation substrate shared across namespaces, and `wiki/general/` for workflow knowledge. The boundary rule: route by implementation sharing, not by topic — see [CONCEPT.md](CONCEPT.md).

## Recommended local setup

The wiki works best when the related repos are cloned side by side and available to the agent locally. See [repos.yaml](repos.yaml) for the full path list. Typical layout:

```txt
GitHub/
├── repo-a/
├── repo-b/
└── team-brain/
```

Local repos are the primary workflow because the skills can quickly read `CONCEPT.md`, `wiki/index.md`, `repos.yaml`, and source docs referenced by relative paths like `../repo-a/docs/architecture.md`. GitHub or `gh` access is a fallback when a source repo is missing locally.

## Agent Workflow

```
/brainstorm → /planning → /implement → /evaluate → /review-pr → merge → /wiki-sync
```

Each skill owns one verb. See [.agents/README.md](.agents/README.md) for the full reference.

| Skill | Invoke | What it does |
|---|---|---|
| `setup-brain` | `/setup-brain` | One-time (re-runnable) onboarding. **New brain**: guided fill-in of `repos.yaml`, namespaces, zones, and template placeholders. **Existing brain**: report-first migration of an existing wiki into this structure. Installs skill copies for the agent tools the team uses (Claude Code, Cursor, Codex, …). |
| `brainstorm` | `/brainstorm <topic>` | Explore a problem before building. Saves to `inbox/dump/` on request. |
| `planning` | `/planning <intent>` | Three-phase gate. Phase 1: propose breakdown (approval gate). Phase 2: write phase specs to `plans/<namespace>/<feature-slug>/` at `status: wip`. Phase 3: optionally flip a phase to `status: ready to ship` when a user wants to implement manually. |
| `implement` | `/implement <phase-file-or-feature>` | Implements a phase in the target repo resolved from `repos.yaml`. If the plan is still `wip`, it resolves open questions with the user one by one before coding. Runs `/simplify` and marks the phase `implemented-pending-pr`. |
| `simplify` | `/simplify <paths-or-diff>` | Scoped code-quality pass for recently changed implementation code. Preserves behavior while improving clarity, reuse, and maintainability. |
| `evaluate` | `/evaluate <feature-slug>` | Optional pre-PR gate, especially for manually implemented phases. Maps each acceptance criterion to code; reports `complete` / `partial` / `missing` / `unclear`. Skips phases still at `status: wip`. |
| `review-pr` | `/review-pr [<pr-number>]` | Pre-merge. Runs validation (lint/format/typecheck/UI), auto-detects linked issue, writes title + body + change-breakdown score, applies via `gh`. |
| `wiki-sync` | `/wiki-sync <pr-or-doc>` | Post-merge. **PR mode**: creates/flips ADR, updates wiki pages, appends log, archives the matching lifecycle files. **Doc mode**: ingests existing implemented knowledge directly. |
| `wiki-query` | `/wiki-query <question>` | Read-only. Searches wiki + ADRs + `repos.yaml`. Cites sources, distinguishes stable knowledge from uncertainty. |
| `wiki-lint` | `/wiki-lint` | Periodic health audit. |
| `wiki-adr` | `/wiki-adr` | Record an ad-hoc architecture decision outside the `/planning → /wiki-sync` flow. |
| `wiki-runbook` | `/wiki-runbook` | Document cross-repo operational procedures. |
| `workflow-from-chats` | `/workflow-from-chats <excerpts-or-target>` | Mine repeated chat feedback into durable workflow guidance. Routes findings to skill updates, wiki/runbook notes, planning guidance, inbox follow-ups, or no change. |
| `create-bug-issue` | `/create-bug-issue <bug>` | Captures a bug in the appropriate GitHub repo with the `bug` label. |
| `pr-score-log` | `/pr-score-log` | Lists merged PRs and the `review-pr` score totals from their PR bodies. |
| `rebase-onto-main` | `/rebase-onto-main` | Safely rebases a feature branch onto the configured base branch and writes an audit report. |
| `lifecycle-audit` | `/lifecycle-audit` | Report-first cleanup audit for historical ideas, plans, PRs, archives, and wiki-sync state. |
| `skills-sync` | `/skills-sync` | Admin workflow for syncing registered skills from this repo to configured agent surfaces. |

## Getting Started

The skills ship pre-installed for Claude Code (`.claude/skills/`), Cursor (`.cursor/skills/`), and Codex (`.codex/skills/`) as mirrors of the canonical `.agents/skills/`, so they're discoverable the moment you open the repo in any of those tools. After cloning, run `/setup-brain`: it detects whether you're configuring a fresh template or migrating an existing wiki, walks the customization checklist, prunes the surface mirrors for tools your team doesn't use (or adds a custom surface), and records the choices in `repos.yaml` under `skill_surfaces`. Re-running it later acts as a setup health check.

## Copy-Paste Setup Prompt

Paste this into Claude Code, Cursor, Codex, or another agent after opening this repo:

```txt
Set up this repository as an LLM-maintained cross-repo wiki and agent workflow.

Please read:
- README.md
- CONCEPT.md
- repos.yaml
- wiki/index.md
- .agents/README.md

Then register or follow the reusable skills in .agents/skills:
- setup-brain
- brainstorm
- planning
- implement
- simplify
- evaluate
- review-pr
- wiki-sync
- wiki-query
- wiki-lint
- wiki-adr
- wiki-runbook
- workflow-from-chats
- create-bug-issue
- pr-score-log
- rebase-onto-main
- lifecycle-audit
- skills-sync

When I want to configure this template or migrate an existing wiki into it, use setup-brain.
When I want to explore an idea, use brainstorm.
When I want to turn a brainstorm or intent into phase specs, use planning.
When I want to turn a phase into code, use implement.
When I have implemented a phase and want to verify it, use evaluate.
When I'm ready to open or update a PR, use review-pr.
When a PR has merged and the wiki needs syncing, use wiki-sync.
When I have a question about existing knowledge, use wiki-query.
When I want a wiki health pass, use wiki-lint.
When a durable architecture/infrastructure decision needs recording outside /planning, use wiki-adr.
When I want to document an operational procedure, use wiki-runbook.
When repeated chat feedback should become durable workflow guidance, use workflow-from-chats.
When I need to capture a bug for later, use create-bug-issue.
When I need merged PR score history, use pr-score-log.
When I need to sync a feature branch with the base branch, use rebase-onto-main.
When old lifecycle files need cleanup, use lifecycle-audit.
When skill copies drift across repos, use skills-sync.

Preserve source authority: repo-local docs and linked sources remain authoritative; this wiki synthesizes rather than copies them.
Track uncertainty in inbox/open-questions.md.
Track unsupported assertions in inbox/claims.md.
Update repos.yaml when introducing a new authoritative source.
Update wiki/index.md when adding a new page.
Append meaningful maintenance entries to wiki/logs/index.md.

First, run setup-brain: inspect the current repo, report what is already configured versus still needed, and walk me through the remaining setup for this team.
```

Claude Code, Cursor, and Codex discover the skills automatically from the pre-installed surface mirrors. For another tool that requires skills to live in a specific directory, `/setup-brain` installs the copies for you (it copies each folder from `.agents/skills/` into the tool's skills directory while preserving the `SKILL.md` file inside each folder, and records the chosen surfaces in `repos.yaml` under `skill_surfaces`). Ongoing drift between copies is managed by `/skills-sync`.

## How To Use This Wiki

### 1. Before starting work

Ask what already exists:

```txt
Use wiki-query: what do we know about <feature/system>?
Use wiki-query: which decisions affect <area>?
Use wiki-query: what open questions exist around <topic>?
```

### 2. During development

Repo-local docs remain authoritative for implementation details. See [repos.yaml](repos.yaml) for which repo owns which components.

When a rough idea surfaces while you're working — something worth thinking through but not yet ready to build — explore it with `/brainstorm`. The output saves to `inbox/dump/` on request and is the bridge from "vague idea" to "ready for `/planning`."

For raw, unstructured capture (an observation, half-formed thought, chat takeaway), `inbox/fragments.md` and `inbox/chats.md` are still fine. Skim them periodically and either `/brainstorm` the promising ones or delete dead ones.

When repeated chat feedback points to a stable team or agent preference, use `/workflow-from-chats` to decide whether it belongs in a skill, wiki/runbook page, planning guidance, inbox follow-up, or nowhere.

### 3. Design and planning

When a brainstorm solidifies into something worth building, use `/planning`:

```txt
Use planning: <paste your brainstorm doc or describe the feature>
```

`/planning` writes one detailed technical spec per phase, grouped under a namespace and feature folder: `plans/<namespace>/<feature-slug>/<phase-slug>.md`. Use `general` when the work is not tied to a specific product, customer, domain, or workstream. Each new spec is `status: wip`.

If you plan to implement the phase yourself, review the plan and resolve its open questions, then tell `/planning` to flip the phase to `ready to ship`. That status means a human has reviewed the phase and it is safe to build outside the `/implement` skill.

### 4. Implementation

You can also run `/implement` directly on a `wip` or `ready to ship` phase:

```txt
Use implement: plans/<namespace>/<feature-slug>/<phase-slug>.md
```

If the phase is still `wip`, `/implement` reads the open questions and asks you to resolve or route them one by one before coding. It then treats the resolved phase as implementation scope, resolves the target repo through `repos.yaml`, writes the code, runs `/simplify` on the changed files when available, and marks the phase `implemented-pending-pr`.

### 5. After implementation, before a PR

Run `/evaluate` when you implemented the phase yourself, or when you want a separate acceptance-criteria audit before opening a PR. It maps each acceptance criterion to code and reports gaps. It does **not** run lint/typecheck/UI (that's `/review-pr`) and does **not** touch the wiki.

### 6. Before opening a PR

Run `/review-pr` from whichever repo you're in. It runs validation, auto-detects a linked GitHub issue, and writes the PR title + body + score to GitHub. It also classifies the PR as `implementation`, `artifact` (only lands brainstorms/plans/strategy docs), or `mixed`, and stamps `related_pr` or `artifact_pr` on the lifecycle files accordingly — only implementation PRs advance a phase to `pr-open`. ADR work happens later in `/wiki-sync`.

### 7. After merge

Run `/wiki-sync <pr>`. It creates the ADR (or flips an existing one to `accepted`), updates affected wiki pages, appends a log entry, records the PR in `wiki/logs/synced-prs.md`, and archives completed plan/source files under `archive/<namespace>/`. Active or incomplete phases stay in `plans/<namespace>/<feature-slug>/`.

### 8. Periodic maintenance

`/wiki-lint` for stale pages, dangling links, runbooks needing exact commands, and pages that no longer match implementation.

Use `/lifecycle-audit` for older or messy files that predate the lifecycle metadata model. It reports proposed archive or metadata actions first and only applies changes after explicit approval.

## Rule Of Thumb

Repo docs explain how one part works. This wiki explains how the whole system fits together, why decisions were made, and what the team knows so far.
