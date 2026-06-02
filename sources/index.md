# Sources Index

Status: template
Last reviewed: YYYY-MM-DD

> **Canonical source manifest:** [`../repos.yaml`](../repos.yaml). Skills (`/wiki-sync`, `/wiki-query`, `/planning`, `/implement`, `/evaluate`, `/review-pr`, `/create-bug-issue`, and `/skills-sync`) read `repos.yaml` directly to resolve repo paths, source→wiki feed mappings, validation commands, and skill destinations.
>
> This file is a **human-readable companion** — narrative notes about the team's source material that don't fit cleanly into YAML. Keep it in sync with `repos.yaml` or delete it if `repos.yaml` is enough.

## When to use this file

- Capturing context that doesn't belong in YAML (e.g. "the architecture doc in `repo-a` is being rewritten; expect drift through Q2").
- Pointing readers at non-repo sources (Notion, Linear, Slack archives).
- Tracking ephemeral inputs that aren't worth a `repos.yaml` entry yet.

## Repository Ownership (narrative)

See [`../repos.yaml`](../repos.yaml) for the authoritative ownership list. Add narrative below only when YAML can't capture the nuance.

| Repo | Notes |
|---|---|
| `repo-a` | Replace with team-specific narrative — e.g., active rewrite, deprecation status, ownership changes. |
| `repo-b` | Replace with team-specific narrative. |
| `team-wiki` | This repo. Cross-repo synthesis, ADRs, inbox, and `plans/`. |

## Ephemeral Sources

Use [`../inbox/`](../inbox/) for chat notes, screenshots, meeting notes, and rough ideas that don't have a stable repo-local home yet.

## Adding a new authoritative source

1. Add an entry under the appropriate `repos[].sources[]` list in [`../repos.yaml`](../repos.yaml).
2. Optionally append a narrative note here if context warrants.
3. Run `/wiki-lint` to verify the `feeds:` targets exist as wiki pages.
