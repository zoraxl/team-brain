---
name: backlog-triage
description: Periodic triage of plans/*/tests.md empirical questions and inbox/backlog.md. Classifies entries (watch/decide/chore/parked), migrates orphan post-ship tests.md into the central backlog, and proposes resolve/promote/keep/park actions. Report first; apply only after explicit approval. Use when the user says "/backlog-triage", "triage backlog", "revisit tests.md", or asks to clean orphan plan folders left by open empirical questions.
---

# Backlog Triage

Periodic maintenance for deferred questions that outlive their plan folders. Complements `/wiki-sync` (post-merge archive) and `/lifecycle-audit` (historical cleanup). Does **not** invent new deferred items — it only triages what already exists.

Brain-only workflow. Do not install into implementation repos.

## Repository Scope

This copy of `backlog-triage` lives in the skills-home brain repo. All reads and writes target this brain (`plans/`, `inbox/backlog.md`, `archive/`). When invoked from a multi-root workspace that also has implementation repos open, still operate only on this brain unless the user explicitly names another brain checkout.

## When to use

- `/backlog-triage` or "triage the backlog"
- After a large `/wiki-sync` batch that left orphan `plans/<namespace>/<feature>/tests.md`
- Monthly revisit of `inbox/backlog.md`
- "What open empirical questions do we still owe?"

## Rules

- **Report first.** Do not move, archive, edit, or retag files on the first pass.
- **Require explicit approval** before applying any proposed action.
- Never permanently delete plan, tests, or backlog entries — archive or retag only.
- Never create `plans/<namespace>/<feature-slug>/backlog.md` (planning forbids it).
- Prefer **one central backlog** (`inbox/backlog.md`) over new folder trees (`inbox/empirical/`, etc.).
- Keep `tests.md` next to active phases while the feature is still shipping; migrate only when the plan chain is complete (or the folder is already phase-empty).

## Revisit classes

Every backlog entry should carry one class (YAML-ish bullet or bold label near the top of the entry):

| Class | Meaning |
|-------|---------|
| `watch` | Answerable soon with live data / post-ship measurement (default for migrated `tests.md`) |
| `decide` | Product or architecture judgment needed |
| `chore` | Cleanup/refactor when next touching that area |
| `parked` | Explicitly not soon; must include a trigger or revisit date |

Do not invent more classes. Untagged legacy entries are `untagged` until a triage pass assigns one.

## Read scope

1. `repos.yaml`
2. All `plans/**/tests.md` (and legacy `plans/**/backlog.md` if any remain)
3. `inbox/backlog.md`
4. Sibling phase files in each `tests.md` folder (to classify orphan vs active)

Do not deep-scan `archive/` unless the user asks for historical consistency.

## Step 1 — Inventory

Build three lists:

### A. Orphan `tests.md` (migrate candidates)

Plan folder has `tests.md` and **no remaining incomplete phase files** (`wip`, `ready to ship`, `implemented-pending-pr`, `pr-open`, or unknown). Empty folder + tests only, or tests-only after all phases archived, counts.

For each open / shippable-tuning entry, propose:

- **Migrate** → `inbox/backlog.md` with `class: watch` (default)
- **Resolve** → fold into wiki / ADR / archived phase KDD if already answered
- **Park** → migrate with `class: parked` + trigger if not actionable for months

### B. Active-feature `tests.md` (leave in place)

Folder still has incomplete phases. Report open entry counts only; do not migrate.

### C. Central backlog triage

Scan dated `##` entries in `inbox/backlog.md`:

- Missing class → propose `watch` / `decide` / `chore` / `parked`
- Older than **45 days** and still open-looking → flag for keep / promote-to-plan / park / drop-as-done
- Clearly done (shipped elsewhere) → propose mark resolved + optional archive note

Cap the report: summarize counts, then detail at most ~25 highest-priority proposals unless the user asks for full dump.

## Step 2 — Report (required before edits)

Print:

```markdown
# Backlog triage — YYYY-MM-DD

## Counts
- Orphan tests.md files: N (M open entries)
- Active-feature tests.md: N (M open entries)
- Backlog entries: N (tagged / untagged)

## Proposed migrations (orphan tests.md → backlog)
| Source | Entry | Class | Action |
|--------|-------|-------|--------|
| `plans/.../tests.md` | short title | watch | migrate + archive tests.md |

## Proposed backlog retags / closes
| Entry | Current | Proposed |
|-------|---------|----------|
| … | untagged | chore |

## Leave in place
- `plans/.../tests.md` — reason (active phases: …)

## Empty folders after apply
- `plans/<namespace>/<feature>/` — would be removed if only tests.md remains
```

Stop and wait for approval. Allowed approvals: "apply all", "apply migrations only", "apply rows 1–3", or per-item edits.

## Step 3 — Apply (only after approval)

### Migrate an orphan tests.md entry

1. Append (newest-first, under the backlog header / Empirical watch section) to `inbox/backlog.md`:

```markdown
## YYYY-MM-DD — <Short title>

- Class: watch
- Status: open
- Source: `plans/<namespace>/<feature-slug>/tests.md` (migrated from orphan plan folder)
- Original plan: `archive/<namespace>/plans/...` or former `plans/.../<phase>.md` if known
- Original question: <verbatim>
- Why empirical: <from tests.md>
- How to answer: <from tests.md>
```

2. After all entries from that file are migrated (or explicitly dropped), archive the file:

```yaml
# frontmatter added or updated before move
status: archived
archived_from: plans/<namespace>/<feature-slug>/tests.md
archived_at: YYYY-MM-DD
wiki_log: inbox/backlog.md
```

Move to `archive/<namespace>/plans/YYYY-MM/<feature-slug>/tests.md`. Never overwrite.

3. If the plan folder is empty afterward, remove the empty directory.

4. Legacy `plans/**/backlog.md`: migrate remaining open items with an appropriate class, then archive the same way. Do not recreate per-feature backlog files.

### Retag / close backlog entries

- Add `- Class: <class>` near the top of the entry bullets.
- For done items: set `- Status: resolved` and one line `- Resolved: YYYY-MM-DD — <where it landed>` (PR, ADR, wiki path). Leave the entry in place unless the user asks to move resolved entries to a monthly archive section.

### Do not

- Auto-create Linear/GitHub issues
- Merge active-feature `tests.md` into the backlog
- Rewrite the entire backlog file just to add classes — tag on touch / during triage only

## Step 4 — Output

After apply:

- Files migrated / archived / folders removed
- Backlog path updated (`inbox/backlog.md`)
- Remaining open orphan count (should be 0 for applied rows)
- Reminder: next `/backlog-triage` after the next large wiki-sync or ~30 days

## Cadence

Suggested: once per month, or immediately after a multi-PR `/wiki-sync` that leaves `tests.md`-only folders. Pair with `/wiki-lint` when doing quarterly brain hygiene.

## Related

- Planning routes empirical → `tests.md`, deferred → `inbox/backlog.md`
- `/wiki-sync` Step 10 gates on open `tests.md`; prefer migrate-to-backlog (`class: watch`) over leaving orphan plan folders
- `/lifecycle-audit` for pre-lifecycle historical mess; this skill for living deferred debt
