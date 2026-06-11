---
name: create-bug-issue
description: Create a GitHub issue for a bug found during implementation, QA, or on a live service. Collects bug details from the user and opens an issue with the "bug" label in the target repo. Use when the user says "/create-bug-issue", "log this bug", "create a bug issue", or "note this bug for later".
---

# Create Bug Issue

Quickly capture a bug as a GitHub issue so it does not get lost. No approval gate is needed after required details are known.

## Repository Scope

Read `repos.yaml` at the brain repo root to resolve known repos. If the target repo is not obvious from context, ask the user to choose one. Do not assume a default implementation repo.

## When to Use

- Found a bug during implementation but do not want to fix it right now.
- Spotted a bug on a live site, service, or QA flow.
- Want to note a regression or unexpected behavior for later.

## Inputs

Required:

- **What is broken** - what the user observed.
- **Where** - which repo or service owns the bug.

Optional, ask only if not obvious from context:

- **Steps to reproduce** - how to trigger it.
- **Expected vs actual behavior** - what should happen vs what does.
- **Severity hint** - blocking, annoying, cosmetic.

If the description is thin, ask one follow-up question before proceeding. Do not invent details.

## Steps

### Step 1 - Confirm details

Echo back the bug summary to the user in one short paragraph. If the target repo or core symptom is missing, ask for it now.

### Step 2 - Create the GitHub issue

Resolve `<owner/repo>` from `repos.yaml`, `gh repo view`, or explicit user input. Then create the issue:

```bash
BODY_FILE=$(mktemp)
trap 'rm -f "$BODY_FILE"' EXIT
cat > "$BODY_FILE" <<'ISSUEBODY'
## What's broken
<what the user observed>

## Steps to reproduce
<steps, or "not provided">

## Expected behavior
<what should happen, or "not provided">

## Actual behavior
<what actually happens>

## Notes
<any extra context, severity, or hints>
ISSUEBODY
gh issue create \
  --repo <owner/repo> \
  --title "<short bug title>" \
  --body-file "$BODY_FILE" \
  --label "bug"
```

### Step 3 - Output

Print the issue URL so the user can find it later.

## Error Handling

- **`gh` not authenticated** - print a copy-pasteable `gh issue create` command instead.
- **Target repo unclear** - ask the user; do not guess.
- **Bug label missing** - create without the label and mention that the label was unavailable.
