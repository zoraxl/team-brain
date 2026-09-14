---
name: brainstorm-design
description: >-
  Lightweight HTML UI mock before planning or implementation. Sketch placement,
  layout, and a few states as a single browser-openable file. Use when the user
  says "/brainstorm-design", "brainstorm design", "mockup", "/mockup", "ui mock",
  or wants to see layout options rather than a markdown brainstorm.
---

# Brainstorm Design

Quick visual sketch before `/planning` or `/implement`. Output is **one self-contained HTML file** the user can open in a browser.

This is the visual peer of `/brainstorm`. Use `/brainstorm` for problem/scope. Use this when the question is *where it sits, how it lays out, what states it has*.

Brain-only. Do not install into implementation repos. Do not write production app code.

## When to use

- Explicit: `/brainstorm-design`, `brainstorm design`, `mockup`, `/mockup`, `ui mock`
- Implicit: "where should this live?", "show me layout options", "what should this screen look like?"

Keep it light. Two or three options and the important states are enough. Do not build a design system, a theme kit, or a pixel-perfect spec.

## What to read

- The user's problem and any screenshots or links.
- A team design-language page if one exists (for example `wiki/<namespace>/design-language.md`). Use those tokens when present.
- Just enough of the target app to name real routes, components, or chrome. Do not invent a second palette.

## Workflow

1. Restate the layout question in one sentence.
2. Ask at most 1–2 clarifying questions only if the surface is unclear.
3. Sketch **2–3 options** in real product chrome (sidebar, header, page) — not floating cards on white.
4. Show the states that change the choice (default, empty, error, collapsed — only those that matter).
5. Mark a recommended option only when one is clearly better; keep rejected options with a one-line reason.
6. Stop. Do not plan phases or write app code.

## Output

One HTML file: inline CSS, no build step, no framework. A short note at the top is enough:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mockup — <short topic></title>
  <!--
  namespace: <namespace or general>
  status: brainstorm-design
  related_plan:
  -->
</head>
<body>
  <main>
    <h1>…</h1>
    <p>YYYY-MM-DD · design sketch, not a plan · <code>target-repo</code></p>
    <!-- recommended option -->
    <!-- other options + one-line why-not -->
    <!-- open details -->
  </main>
</body>
</html>
```

Starter CSS — use team tokens if they exist, otherwise this neutral fallback. Do not add decorative gradients, shadows, or a custom brand accent.

```css
body{margin:0;padding:32px 20px;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f4f4f5;color:#18181b}
main{max-width:72rem;margin:0 auto}
.frame{border:1px solid #d4d4d8;border-radius:8px;background:#fff;overflow:hidden}
.note{color:#52525b;font-size:13px}
```

If a layout reflows, add a narrow (~390px) treatment for the recommended option. Skip a full light/dark system unless the user asks.

## Rules

- Static HTML only. Name real files the change would touch.
- Grounded labels. Use the product's language when known.
- No second design system. Neutral fallback above, or the team's existing materials.
- Useful as `source_dump`: recommended placement, key states, open details.

## Handoff

> Save this design brainstorm?
>
> 1. Save to `inbox/mocks/YYYY-MM-DD-mockup-<slug>.html`.
> 2. Skip — keep it in chat only.

If they pick (1): create `inbox/mocks/` if needed, write the HTML, set `namespace` in the HTML comment (`general` when unbound).

Then:

> Ready for `/planning` when the recommended option looks right. Point the plan's `source_dump` at this HTML file.

Do not invoke `/planning` automatically.
