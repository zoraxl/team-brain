---
name: wiki-sync
description: Use to sync the wiki from a merged PR or from a source doc/file path. Two modes — PR mode (post-merge: creates ADR if needed, flips ADR to accepted, updates wiki pages, appends log, records idempotency, archives related plan/source files) and doc mode (ingests existing implemented knowledge from a file or doc path directly). Use when the user says "wiki-sync", "/wiki-sync", "sync the wiki", "update the wiki from this PR", "ingest this PR", "ingest this doc", or "add this to the wiki".
---

# Wiki Sync

Two input modes — **PR mode** for post-merge sync, **doc mode** for ingesting existing implemented knowledge that has no PR or predates the workflow.

---

## Mode detection

| Input | Mode |
|-------|------|
| A number, `owner/repo#NNN`, PR URL, or `sha:abc` | **PR mode** |
| A file path, glob, or prose description of a source doc | **Doc mode** |
| No argument | List recent unsynced PRs and prompt — runs PR mode on selection |

---

## PR Mode

Use after a PR merges to the default branch in an implementation repo (any repo registered under `repos[]` in `repos.yaml`).

### Inputs

1. PR number on the default repo: `/wiki-sync 1234` (defaults to the first `role: implementation` repo in `repos.yaml`)
2. Cross-repo PR: `/wiki-sync owner/repo#1234`
3. PR URL: `/wiki-sync https://github.com/owner/repo/pull/1234`
4. Merged commit SHA: `/wiki-sync sha:abc123`
5. No argument: list the most recently merged PRs not yet in `wiki/logs/synced-prs.md`, prompt the user to pick one

### Step 1 — Read context

Read `repos.yaml`, `CONCEPT.md`, `wiki/index.md`, and `wiki/decisions/index.md`.

### Step 2 — Resolve the PR

```bash
gh pr view <pr> --repo <owner/repo> --json title,body,files,mergedAt,labels,state,headRefName,closingIssuesReferences
```

Require `state=MERGED`. If the PR is not yet merged, stop and tell the user.

Canonicalize the PR identity before idempotency checks:

- Prefer the GitHub API owner/repo and PR number.
- Treat PR URLs and `owner/repo#N` references as the same PR when the repo name and PR number match.
- Check `wiki/logs/synced-prs.md` by canonical identity, not exact URL text only.

If the canonical PR identity already appears in `wiki/logs/synced-prs.md`, report "already synced", note any known archive state if relevant, and stop without moving files again.

### Step 3 — Identify and verify the bound plan file and source idea

Look for a reference to a plan file in this order:

1. The PR body `## Lifecycle` section, accepting `Plan: plans/<namespace>/<feature-slug>/<phase-slug>.md` or `Plan: plans/<namespace>/<feature-slug>/`.
2. A line matching `plans/<namespace>/<feature-slug>/<phase-slug>.md` elsewhere in the PR body.
3. Scan `plans/` for a phase slug that matches the PR title or branch name.
4. Ask the user: "Which plan file or folder does this PR correspond to? (e.g. `plans/general/auth-rewrite/phase-1-token-storage.md`, `plans/general/workflow-fix/`, or 'none')"

If the user says "none" or no plan file is found, skip plan/source archive cleanup at the end.

When a plan file is found, resolve the source idea from:

1. The PR body `## Lifecycle` section line `Source idea: ...`.
2. The plan frontmatter field `source_dump`.
3. A source idea file whose `related_plan` points at the plan path or folder.

Do not invent a source idea if none is found.

Before proceeding with archive cleanup, verify the lifecycle chain:

- The PR body `Plan:` value must match the resolved plan path or folder.
- The PR body `Source idea:` value, when present, must match the plan `source_dump`.
- The source idea `related_plan`, when present, must match the resolved plan path or folder.
- The plan/source `related_pr`, when present, must match the canonical PR identity.
- If any values conflict, stop archive cleanup and ask the user to confirm the correct chain. Continue wiki/ADR sync if possible, but do not archive conflicting lifecycle files.

### Step 4 — Resolve or create the ADR

Look for an existing bound ADR in this order:

1. Any closing issue with an `adr:NNN` label → read `wiki/decisions/adr-NNN-*.md`
2. A line matching `wiki/decisions/adr-NNN-` in the PR body
3. The head branch name matching `^adr-NNN-`

**If an existing ADR is found:** proceed to Step 5 to flip its status.

**If no ADR is found:** create one now.

- Find the highest existing ADR number:
  ```bash
  ls wiki/decisions/adr-*.md | sort | tail -1
  ```
  Increment by 1. Use zero-padded 3-digit format: `adr-001-`, `adr-002-`, etc.

- Derive the slug from the PR title or plan file name (kebab-case).

- Write `wiki/decisions/adr-NNN-<slug>.md`:

  ```markdown
  # ADR NNN: <Title>

  Status: accepted
  Date: YYYY-MM-DD
  Implemented-by: <PR URL>
  Implemented-on: YYYY-MM-DD

  ## Context

  <1-2 sentences on why this was built and what problem it solves — derive from PR body or plan file>

  ## Key Design Decisions

  Bullet list of the meaningful choices made in this phase. Derive from the "Key Design Decisions" section of the plan file. Each bullet should state the choice and the reason behind it.

  - **<Decision>** — <why this approach was chosen over alternatives>
  - …

  ## Alternatives Considered

  <For each rejected alternative: what it was and why it was ruled out. Derive from plan file if available, otherwise "Not recorded.">

  ## Consequences

  <Bullet list of outcomes and trade-offs — what this enables, what it costs, what to watch.>

  ## Sources

  - PR: <PR URL>
  - Plan: `<plan file path if available>`

  ## Related

  - [Decision index](index.md)
  ```

- Update `wiki/decisions/index.md` — add a row for the new ADR.

### Step 5 — Update ADR status (if ADR already existed)

In `wiki/decisions/adr-NNN-<slug>.md`:

- Change `Status: proposed` → `Status: accepted`
- Add after the status line:
  - `Implemented-by: <PR URL>`
  - `Implemented-on: YYYY-MM-DD`

### Step 6 — Identify affected wiki pages

```bash
gh pr view <pr> --repo <owner/repo> --json files --jq '.files[].path'
```

For each changed file, look up `repos[name].sources[path].feeds` in `repos.yaml` to find the downstream wiki pages.

### Step 7 — Update affected wiki pages

For each wiki page from Step 6: read the current page, add or update a brief synthesis section. Do not paste the diff wholesale. Preserve source authority with a link or path. Mark uncertainty explicitly.

### Step 7.5 — Write Tunable Knobs to engineering wiki

If the plan file has a "Tunable Knobs and Notes" section with any content, append it to `wiki/engineering/tunable-knobs.md` (create the file if it doesn't exist):

```markdown
## <ADR title> (ADR NNN)

> Source: `<plan file path>` — ingested YYYY-MM-DD

<Paste the Tunable Knobs section verbatim from the plan file>
```

This preserves operational knowledge (thresholds, caps, timeouts, signals to watch) that would otherwise become harder to find after the plan file is archived. If there are no tunable knobs, skip this step.

### Step 8 — Append to wiki log

Append to `wiki/logs/index.md`:

```md
### YYYY-MM-DD — <ADR title or PR title>

- PR: <PR URL>
- ADR: <ADR path> (status → accepted)
- Wiki pages updated: <list>
- Sources consulted: <list of changed source files>
```

If `wiki/logs/index.md` exceeds ~20 entries, move older entries to `wiki/logs/YYYY-MM.md` and keep the last 5 in `index.md`.

### Step 9 — Record in synced-prs ledger

Append to `wiki/logs/synced-prs.md` (create if missing):

```
<PR URL> synced <YYYY-MM-DD>
```

### Step 10 — Archive plan and source idea files

Archive cleanup is allowed only when the whole linked idea/plan chain is complete. A source idea linked to a plan folder remains active until every linked phase file is synced, archived, or explicitly included in the completed scope. Do not archive a source idea merely because one phase in its plan folder merged.

Treat these statuses as complete for archive-scope checks: `implemented-and-synced` and `archived`. Treat `pr-open` as complete only when `related_pr` matches the merged PR being synced and the phase is explicitly included in the PR lifecycle scope. Treat `wip`, `ready to ship`, `implemented-pending-pr`, missing status, and unknown statuses as incomplete.

If a plan file was identified in Step 3:

1. **Resolve namespace.** Prefer the plan frontmatter field `namespace`. If missing, fall back to the path prefix in `plans/<namespace>/`. If the namespace cannot be resolved, stop before archive cleanup and ask the user.

2. **Hard gate — linked phases incomplete.** Before archiving, scan all sibling phase files in `plans/<namespace>/<feature-slug>/` and classify each phase as complete or incomplete using the archive-scope rules above. If any are incomplete, do not archive the source idea, `tests.md`, or full plan folder. Archive only phase files explicitly matched to the merged PR and leave the chain active:

   > **Not archiving full chain:** the following phases under `plans/<namespace>/<feature-slug>/` are not complete: `<list of files>`. The source idea and plan folder stay active until the whole linked chain is done. If unfinished phases were intentionally abandoned, route that context to `inbox/backlog.md` or confirm a legacy cleanup/backfill path.

3. **Gate — unresolved tests.md entries.** If `plans/<namespace>/<feature-slug>/tests.md` exists, scan it for entries with `Status: open`. If any are found and the feature folder is otherwise complete, ask before archiving `tests.md` or the source idea.

4. **Mark the implemented phase before archive.** A merged PR is implementation evidence for the identified phase when the phase is named by the PR lifecycle section or confirmed by the user. Before moving, add or update frontmatter:
   ```yaml
   status: implemented-and-synced
   implemented_at: YYYY-MM-DD
   wiki_log: <log path>
   related_pr: <PR URL>
   ```

5. **Archive the phase file.** Use the sync date for the archive month (`YYYY-MM`). Before moving, add or update frontmatter:
   ```yaml
   status: archived
   archived_from: <original plan path>
   archived_at: YYYY-MM-DD
   wiki_log: <log path>
   related_pr: <PR URL>
   ```

   Move the file to `archive/<namespace>/plans/YYYY-MM/<feature-slug>-<phase-slug>.md` or another collision-safe equivalent. Never overwrite an existing archive file; append a short suffix if needed.

6. **Archive `tests.md` only when the feature folder is complete.** If only `tests.md` remains and all entries are resolved, or the user confirms archival despite open entries, archive `tests.md` under `archive/<namespace>/plans/YYYY-MM/`. Do not permanently delete it.

7. **Remove empty original plan folders after archive.** After archiving all in-scope phase files and any archived `tests.md`, check the original `plans/<namespace>/<feature-slug>/` folder. If no files remain, remove the empty folder. If any file remains, leave the folder in place and print the remaining files.

8. **Mark and archive the source idea only when safe.** If a source idea was resolved, the lifecycle chain verifies, and every linked phase is complete, update its frontmatter with `status: implemented-and-synced`, `related_plan`, `related_pr`, and `wiki_log`, then archive it to `archive/<namespace>/ideas/YYYY-MM/` with `status: archived`, `archived_from`, and `archived_at`. Do not archive a source idea that may feed other active plans or has incomplete linked phases.

9. Print what was archived, which lifecycle statuses were updated, and which empty active folders were removed. `/wiki-sync` must not permanently delete plan, idea, or test files.

### Step 11 — Output

List:
- ADR path and status (created or flipped to accepted)
- Wiki files updated
- Log entry path
- Plan/source files archived (if any)
- Empty active folders removed (if any)

---

## Doc Mode

Use when ingesting **existing implemented knowledge** from a source doc or file — no PR required. Typical cases:
- A raw fragment in `inbox/` that's now ready to promote
- Existing repo docs that predate the `/planning` workflow
- External material (specs, meeting notes) describing something already shipped

### Inputs

- A file path: `/wiki-sync ../repo-a/docs/architecture/overview.md`
- A glob: `/wiki-sync ../repo-a/docs/*.md`
- A prose description with an attached file reference

### Step 1 — Read context

Read `repos.yaml`, `CONCEPT.md`, `wiki/index.md`.

### Step 2 — Read the source material

Read the provided file(s). Extract:
- New product/system concepts
- Architecture or data-flow facts
- Durable decisions or tradeoffs
- Implementation details that cross repo boundaries

### Step 3 — Identify affected wiki pages

Look up the source path in `repos[name].sources[path].feeds` in `repos.yaml`. If the path isn't registered, determine the best-fit wiki page from context and ask the user to confirm before writing.

If no existing wiki page is relevant, ask whether to create one or add to `inbox/fragments.md` for later promotion.

### Step 4 — Update wiki pages

For each target wiki page: synthesize the new knowledge into the appropriate section. Rules:
- Do not copy source docs wholesale.
- Preserve source authority with a link or path.
- Synthesize; do not mirror.
- Mark uncertainty explicitly.
- If the material affects operations, update `wiki/engineering/runbooks.md`.
- If the material changes cross-repo architecture, update `wiki/system/architecture.md` or `wiki/system/data-flow.md`.
- If the source path isn't already in `repos.yaml`, add it to the correct `repos[name].sources[]` entry.

### Step 5 — Append to wiki log

Append to `wiki/logs/index.md`:

```md
### YYYY-MM-DD — Ingested <source path>

- Source: <file path(s)>
- Wiki pages updated: <list>
- ADR: <if a durable decision was identified, link or "none">
```

### Step 6 — Output

List files touched, sources consulted, log entry path. If a durable decision was found with no ADR, note: "Consider running `/wiki-adr` to record this as a formal decision."

---

## Inbox Curation (Replaces wiki-digest-fragments)

When the user asks to digest or curate the inbox (e.g. "digest fragments", "process inbox", "what's in inbox"), use Doc mode against the relevant `inbox/` files. Rules specific to inbox curation:

- Group fragments by theme before deciding promotion.
- For each fragment, choose one action: leave in inbox, convert to `inbox/open-questions.md`, record in `inbox/claims.md`, promote into an existing wiki page, or suggest an ADR.
- Preserve original wording when phrasing carries product or domain intuition.
- Do not over-polish early ideas. Keep contradictions visible.
- Do not delete raw inbox material unless it is clearly superseded; the wiki log entry should record where it went.

---

## Rules (all modes)

- Do not copy source docs wholesale into the wiki.
- Preserve source authority with links or paths.
- Synthesize; do not mirror.
- Mark uncertainty explicitly.
- Do not present speculation as settled knowledge.
- The wiki contains only decided and implemented knowledge — if material is still speculative, direct it to `inbox/fragments.md` or `inbox/open-questions.md` instead.
