---
name: simplify
description: Simplify and refine recently modified implementation code for clarity, consistency, reuse, performance, and maintainability while preserving exact behavior. Use when the user says "/simplify", "simplify this", "clean up this code", after /implement finishes, or after /evaluate confirms implementation completeness and needs a scoped code-quality pass.
---

# Simplify

Simplifies and refines code for clarity, consistency, and maintainability while preserving all functionality. Focus on recently modified code unless the user explicitly names a broader scope.

## Repository Scope

This skill usually runs against an implementation repo changed by `/implement` or checked by `/evaluate`. Use `repos.yaml` to resolve sibling repo paths and handle each repo separately when a diff spans multiple repos.

## Operating Principles

- Preserve exact functionality. Do not change features, outputs, side effects, API contracts, persistence shape, or user-visible behavior.
- Apply the target repo's local standards first: read relevant `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, package conventions, and nearby code before changing style.
- Prefer readable, explicit code over compact tricks. Avoid nested ternaries; use clear branches for multiple conditions.
- Prefer project patterns and existing helpers over new abstractions.
- Remove low-information comments, redundant branches, dead compatibility code, unnecessary helpers, avoidable casts, broad types, and duplicated derived state when behavior is clearly unchanged.
- Keep helpful abstractions that improve organization. Do not flatten code just to reduce line count.
- Preserve unrelated user changes. Do not broaden scope beyond the selected diff or explicitly named paths unless needed to understand existing patterns.

## Scope Selection

1. If the user provided explicit scope after `/simplify` (paths, symbols, a diff, or a natural-language area), use that scope.
2. Otherwise inspect both unstaged and staged changes in the target repo:
   - `git diff --no-color`
   - `git diff --cached --no-color`
3. Treat the combined non-empty output as the scope.
4. If there is no local diff, fall back to concrete files, symbols, or changes mentioned in the conversation.
5. If that also does not exist, fall back to the current `HEAD` commit with `git show --stat --patch --no-color HEAD`.
6. If the scope spans multiple repos, handle each repo separately and keep findings and fixes grouped by repo.

## Review Pass

Review the scoped changes for:

- Code quality: low-information comments, unnecessary nullable state, catch-all `try`/`catch`, premature abstraction, weak type escape hatches, duplicated or derived state, and dead code.
- Performance: blocking work in hot paths, uncached expensive operations, busy waits, string concatenation in loops, N+1 I/O, and chatty logging or telemetry in loops.
- Reuse: existing helpers, local patterns, schema utilities, UI components, validation functions, test helpers, or repo conventions the scoped changes should reuse.

Only recommend changes that preserve behavior and are justified by the scoped code path.

## Fixing Rules

1. Aggregate findings and discard anything outside the selected scope.
2. Apply targeted fixes when they clearly reduce complexity, improve consistency, or reuse existing patterns without behavior changes.
3. Skip findings that need user/product judgment, require a wider refactor than the original change, depend on uncertain performance assumptions, or would make the code cleverer instead of clearer.
4. Keep edits small and local. Do not run broad formatters unless the repo workflow requires it for touched files.
5. After substantive edits, run the most relevant lightweight checks for touched files when practical. If checks are unavailable or too expensive, say so.

## Final Response

Summarize:

- What you simplified.
- Which checks ran and their result.
- Any valid recommendations you skipped, with a short reason.

Keep the summary concise and scoped to the changed code.
