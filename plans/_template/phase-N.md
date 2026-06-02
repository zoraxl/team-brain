---
status: wip
namespace: general
source_dump:
related_pr:
wiki_log:
---

# Phase N: <Title>

## Objective

What this phase achieves and why it matters. Include the problem being solved and what the system looks like after this phase is complete.

## Context

Background the reader needs: what exists today, what is broken or missing, what prior phases delivered (if any).

## Before vs After

Concrete comparison showing what changes. Use code blocks or tables where helpful.

## Architecture

ASCII diagram or prose describing how the components fit together after this phase. Include data flow, call order, and which existing systems are modified.

## Implementation

Step-by-step breakdown. For each step:
- What gets built or changed (actual function names, file paths, DB columns, schema changes)
- Why this step is needed
- Any non-obvious details or constraints

## Key Design Decisions

Bullet list of the meaningful choices made and the reasoning behind them. Include rejected alternatives and why they were ruled out.

## Tunable Knobs and Notes

Any constants, thresholds, timeouts, or caps that were chosen for cost/performance reasons and may need adjustment. Explain the signal to watch for and what to change. Omit this section if it does not apply.

## Lifecycle Notes

How implementers should update lifecycle status after this phase is built. State which phase files should move to `implemented-pending-pr` after implementation/evaluation, which linked source idea should remain active until the full linked chain is done, and what `/review-pr` must stamp once a PR exists. Omit this section if it does not apply.

## Open Questions

Concrete questions that remain unresolved for this phase. Each item should be a real question, not a hand-wavy maybe.

`/planning` Phase 3 (review) cannot flip this phase to `ready to ship` until every entry here is either:

- resolved in-place (typically by adding a Key Design Decision and removing the question),
- routed to `plans/<namespace>/<feature-slug>/tests.md` (empirical questions answerable only by implementation or post-ship measurement),
- routed to `inbox/backlog.md` (deferred, out-of-scope, or needs a separate decision).

If there are no open questions, omit this section.
