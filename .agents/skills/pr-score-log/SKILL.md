---
name: pr-score-log
description: List merged GitHub PRs after a given PR number in a markdown table with PR link, review-pr total score numerator only, and merged date. Uses gh and jq. Use when the user asks for a PR score log, merged PR scores since a number, or a table of PR scores.
version: 1.0.0
allowed-tools: ["Bash"]
triggers:
  - "pr.{0,15}score.{0,15}log"
  - "merged.{0,15}pr.{0,15}score"
  - "pr.{0,15}table.{0,15}(after|since)"
  - "list.{0,15}(merged.{0,15})?pr"
  - "score.{0,15}table.{0,15}(pr|pull)"
---

# PR Score Log

Read-only: list merged PRs in the current or specified repo with PR number greater than a cutoff. Print a markdown table of PR link, score, and merged date.

The score is the numeric total from the PR body, parsed from `/review-pr`'s `**Total Score: X/Y**` line. Output **X only**, not the denominator.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated.
- `jq` installed.
- Run from a git directory with a GitHub remote, or pass `GH_REPO`.

## Inputs

| Input | Required | Default | Notes |
|-------|----------|---------|-------|
| `MIN_PR` | Yes | - | Only PRs with `number > MIN_PR` (exclusive). |
| `LIMIT` | No | `500` | `gh pr list --limit`; raise if you have more merged PRs. |
| `GH_REPO` | No | current `gh` repo | `owner/name` to target another repository. |
| `AUTHOR` | No | `@me` | GitHub author filter. Use `@me` for the current user. |

## Command

```bash
MIN_PR="${MIN_PR:?set MIN_PR to the exclusive lower bound PR number}"
LIMIT="${LIMIT:-500}"
AUTHOR="${AUTHOR:-@me}"
EXTRA=()
[[ -n "${GH_REPO:-}" ]] && EXTRA=(--repo "$GH_REPO")

gh pr list --state merged --author "$AUTHOR" --json number,url,mergedAt,body \
  --limit "$LIMIT" "${EXTRA[@]}" | jq --argjson min "$MIN_PR" -r '
  [.[] | select(.number > $min)] | sort_by(.number)
  | (["| PR Link | Score | Merged |", "| --- | --- | --- |"] +
    [.[] |
      ((if .body == null then "—" else
        (try (.body | capture("\\*\\*Total Score:\\s*(?<sum>[0-9]+)/(?<max>[0-9]+)\\*\\*") | .sum) catch "—")
      end) as $sc |
      "| " + .url + " | " + $sc + " | " + (.mergedAt | split("T")[0]) + " |")
    ])
  | .[]
'
```

## Output

A markdown table:

| PR Link | Score | Merged |
| --- | --- | --- |
| ... | ... | YYYY-MM-DD |

## Edge Cases

- `gh` errors - fix authentication, set a default repo, or set `GH_REPO`.
- No rows - only header rows print; say there are no matching merged PRs.
- Missing scores - PRs not created with `review-pr` may show `—`; that is expected.
- Many PRs - increase `LIMIT`.

## Agent Notes

- Do not run lint/typecheck; this is read-only.
- Paste the resulting table into the chat for the user.
- If the user says "after #N", use `MIN_PR=N` (exclusive).
