---
name: setup-brain
description: One-time (re-runnable) onboarding workflow for adopting this brain template. Two modes — new brain (guided fill-in of repos.yaml, namespaces, zones, and template placeholders) and existing brain (report-first migration of an existing wiki/docs repo into the template structure). Also installs skill copies into the agent surfaces the team uses (Claude Code, Cursor, Codex, or others). Use when the user says "/setup-brain", "set up this brain", "onboard to this template", "configure the wiki template", "migrate our wiki into this template", or "install the skills for <tool>".
---

# Setup Brain

Onboard a team onto this brain template. Designed to be run once after cloning the template, but safe to re-run at any time — each pass detects what is already configured and only surfaces the remaining steps, so it doubles as a setup health check.

This skill lives only in the brain repo (the repo marked `skills_home: true` in `repos.yaml`). Do not install it into implementation repos and do not add it to the `/skills-sync` registered list.

## Mode detection

| Signal | Mode |
|---|---|
| Fresh template clone: placeholder repos (`repo-a`, `<org>`), `Status: template` markers, example `wiki/product/` zone untouched | **New brain** |
| The team already has a wiki, docs repo, or partially adopted brain and wants to move it into this structure | **Existing brain** |
| Ambiguous | Ask: "Are we configuring a fresh template, or migrating an existing wiki/brain into it?" |

## Setup state checks (both modes, run first)

Detect what is already done so re-runs only surface remaining work:

```bash
rg -n "repo-a|<org>|YYYY-MM-DD|Status: template" repos.yaml CONCEPT.md README.md wiki/ --glob '!*.git*'
ls wiki/ wiki/decisions/
rg -n "skill_surfaces|skills_home" repos.yaml
ls -d .agents/skills/*/ 2>/dev/null
ls -d .claude/skills .cursor/skills .codex/skills 2>/dev/null
```

Report the findings as a checklist (configured / remaining) before changing anything.

---

## Mode A — New brain

Walk the customization checklist from `CONCEPT.md` interactively. Apply changes directly; nothing here is destructive.

### Step A1 — Repos manifest

For each of the team's repos, fill a `repos[]` entry in `repos.yaml`:

- `name`, `github`, `local_path` (verify the sibling path exists on disk; warn if not), `role`.
- `validation` commands — ask for the repo's lint/typecheck/test commands, or read them from the repo's `package.json`/`Makefile`/CI config when the sibling repo is available locally.
- `owns` — components the repo is authoritative for.
- `sources` — map the repo's authoritative docs to wiki feed targets, using the zone rules from `CONCEPT.md` (namespace-specific pages feed `wiki/<namespace>/`, shared substrate feeds `wiki/platform/`).

Remove placeholder entries (`repo-a`, `repo-b`) once real entries exist. Update the `team-wiki` entry's `name`/`github` to the actual brain repo.

### Step A2 — Namespaces and zones

1. Ask which lifecycle namespaces the team needs. Default to `general` only; add one namespace per product, customer, domain, or workstream with a clear boundary.
2. Rename the example `wiki/product/` zone to the first product namespace, or delete it if the team starts with `general` + `platform` only. Update `wiki/index.md` links to match.
3. Leave `wiki/platform/`, `wiki/general/`, `wiki/decisions/`, and `wiki/logs/` with their fixed names. Zones for additional namespaces are created lazily by the wiki skills.

### Step A3 — Seed content

- Fill `wiki/<namespace>/vision.md` and `glossary.md` with the team's actual product framing and vocabulary (or leave explicit TODO markers the team asks for).
- Update `CONCEPT.md` placeholders: status, `Last reviewed`, and any team-specific framing.
- Write the first entry in `wiki/logs/index.md` recording the setup itself.

### Step A4 — Agent surfaces (code-gen engines)

Ask which agents/code-gen tools the team uses, and detect what is already present:

| Tool | Surface directory |
|---|---|
| Claude Code | `.claude/skills/` |
| Cursor | `.cursor/skills/` |
| Codex | `.codex/skills/` |
| Generic / canonical | `.agents/skills/` (always kept — this is the authoritative source) |
| Other | Ask for the tool's skills directory convention and use it as a custom surface |

Detection hints: existing `.claude/`, `.cursor/`, or `.codex/` directories in this repo or sibling repos; `.cursor/rules`, `CLAUDE.md`, or `AGENTS.md` files in implementation repos.

The template ships with the brain repo's `.claude/skills/`, `.cursor/skills/`, and `.codex/skills/` pre-populated as mirrors of `.agents/skills/`, so the skills (including this one) are discoverable in those tools immediately after cloning — tools do not read `.agents/skills/` directly.

Then:

1. Record the chosen surfaces in `repos.yaml` under each repo's `skill_surfaces` list (the brain repo lists every surface the team uses; implementation repos usually need only the surfaces their developers run there).
2. In the brain repo: keep the shipped surface mirrors for the tools the team uses, delete the surface directories for tools the team does not use (and remove them from `skill_surfaces`), and create `<surface>/skills/<skill>/SKILL.md` mirrors for any custom surface the team adds. `.agents/skills/` remains the authoritative source; surface copies are derived.
3. For implementation repos, do not install skills directly from this skill. After `repos.yaml` and `skill_surfaces` are filled in, run `/skills-sync` — it installs the registered skills (e.g. `review-pr`, `rebase-onto-main`, `simplify`) into each repo's surfaces, prefixes descriptions with `(<repo-name>)`, preserves repo-specific customization, and opens one PR per changed repo. Ask the user before triggering it, since it writes to sibling repos and may open PRs. `setup-brain` and `skills-sync` themselves are never installed into implementation repos.
4. Tell the user that ongoing drift between copies is also owned by `/skills-sync` — re-run that, not this skill, when skills change later.

### Step A5 — Finalize

1. Replace `Status: template` markers with `Status: active` and stamp real `Last reviewed` dates on every page the setup touched. A configured brain must be distinguishable from a fresh template.
2. Re-run the setup state checks from the top. Print the final checklist; anything still unresolved becomes the explicit handoff list.
3. Suggest next steps: capture the first ideas with `/brainstorm`, ingest existing implemented docs with `/wiki-sync` doc mode, and schedule periodic `/wiki-lint`.

---

## Mode B — Existing brain

Migrating an existing wiki, docs repo, or partially adopted brain. **Report-first**: inventory and propose everything, apply only after explicit approval — same contract as `/lifecycle-audit`.

### Step B1 — Inventory

1. List the existing material: wiki pages, docs, ADR-like decision records, runbooks, idea dumps, planning docs.
2. Classify each item against the template model:
   - Decided and implemented knowledge → a `wiki/` zone (`wiki/<namespace>/`, `wiki/platform/`, or `wiki/general/`, using the implementation-sharing boundary rule from `CONCEPT.md`).
   - Pre-implementation material (ideas, questions, claims, threads) → `inbox/`.
   - Active plans → `plans/<namespace>/<feature-slug>/`.
   - Decisions → `wiki/decisions/<zone>/` with global ADR numbering.
3. Propose `repos.yaml` entries and source→feed mappings for the team's repos.

### Step B2 — Report and approve

Produce a migration report: per file, the proposed destination (or "leave in place"), the zone classification with one-line reasoning, and any conflicts or unknowns. Wait for explicit approval; allow partial approval.

### Step B3 — Apply

Only for approved items:

1. Move/merge content into the template structure. Synthesize rather than mirror when folding prose docs into wiki pages; preserve source authority with links.
2. Run lifecycle metadata backfill through `/lifecycle-audit` for old idea/plan chains rather than reimplementing its rules here.
3. Ingest existing implemented docs through `/wiki-sync` doc mode rather than pasting them into wiki pages directly.
4. A half-migrated wiki is fine — the wiki skills tolerate legacy pages as long as `repos.yaml` feeds stay accurate. Record what remains unmigrated in the final report and in `inbox/backlog.md` if the team wants to track it.

### Step B4 — Agent surfaces and finalize

Run Steps A4 and A5 from Mode A.

---

## Rules

- Re-runnable: never assume a fresh clone; detect configured state first and only act on the gaps.
- Mode A applies directly; Mode B is report-first with explicit approval before any move.
- Never overwrite existing team content with template placeholders.
- `.agents/skills/` is the single authoritative skill source; surface copies are derived and managed afterwards by `/skills-sync`.
- Do not invent repos, namespaces, validation commands, or vocabulary — ask, or read them from the actual repos.
- Record the setup/migration in `wiki/logs/index.md`.

## Output

End with:

- A configured/remaining checklist (the same checks from the top, re-run).
- Files created, updated, moved, or installed (including per-surface skill copies).
- Explicit handoff: what the team still needs to decide or fill in manually.
