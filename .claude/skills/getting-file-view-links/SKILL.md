---
name: getting-file-view-links
description: Get web links to view a file in the repo (GitHub, raw, and for HTML a shareable view). Use when the user asks for a link to view a file, share a file, open a file in the browser, or get a URL for a file.
allowed-tools: [Read, Bash]
---

# Getting File View Links

Produce web links so the user (or someone else) can view a file in this repository. Works for any file path under the repo; for HTML files, also provide a link that renders as a webpage.

## When to use

- User asks for a "link to view this file", "web link for this file", "share this file", or "open in browser"
- User wants a URL to send to someone so they can view the file
- After saving a file (e.g. a cheatsheet or recipe index), user wants the live URLs

## Instructions

### 1. Resolve the file path

- Get the file path from the user or from context (e.g. the file just created or in focus).
- Path must be relative to the **repository root** (e.g. `public/cheatsheets/index.html`, `shared/recipes/index.html`, `shared/recipes/2026-02/easy-lentil-soup-recipe.md`).

### 2. Resolve repo origin (for GitHub URLs)

- If the repo has a GitHub remote, use it: `git remote get-url origin` (e.g. `https://github.com/username/Exobrain.git` or `git@github.com:username/Exobrain.git`).
- Extract **owner** and **repo** (e.g. `username`, `Exobrain`). Default branch is usually `main`.
- If not on GitHub or no remote, say so and give only local options (e.g. open via `file://` or a local server).

### 3. Build the URLs

For a file at path `PATH` (e.g. `public/cheatsheets/agi-radar-chart.html`):

| Link type   | URL pattern |
|------------|--------------|
| **GitHub** (view on GitHub) | `https://github.com/OWNER/REPO/blob/BRANCH/PATH` |
| **Raw**    (raw content)    | `https://raw.githubusercontent.com/OWNER/REPO/BRANCH/PATH` |

Use `main` for BRANCH unless you know otherwise.

### 4. For HTML files: shareable view

HTML at the raw URL often won’t render as a page (Content-Type or CORS). For a **shareable link that renders as a webpage**:

1. Take the **Raw** URL above.
2. Tell the user: go to **https://raw.githack.com/** and paste the raw URL.
3. raw.githack.com returns a CDN URL that renders the HTML as a normal webpage; they can copy that to share.

### 5. Report back

Give the user:

- **File:** `PATH`
- **GitHub:** `https://github.com/OWNER/REPO/blob/main/PATH`
- **Raw:** `https://raw.githubusercontent.com/OWNER/REPO/main/PATH`
- **If HTML:** "For a shareable webpage link: paste the Raw URL into https://raw.githack.com/"

If the repo isn’t on GitHub or isn’t pushed yet, say that and suggest pushing first or using a local server (e.g. `uvicorn shared.recipes.server:app` for the recipes app).

## Examples

**User:** "Give me a link to view the recipes index"

- File: `shared/recipes/index.html`
- GitHub: `https://github.com/username/Exobrain/blob/main/shared/recipes/index.html`
- Raw: `https://raw.githubusercontent.com/username/Exobrain/main/shared/recipes/index.html`
- For a shareable webpage: paste the Raw URL into https://raw.githack.com/

**User:** "How do I share this cheatsheet?"

- Same pattern for e.g. `public/cheatsheets/exo-frontier-ai.html`: GitHub URL, Raw URL, and raw.githack.com for HTML.

## Guidelines

- Always use the path relative to the repo root.
- Don’t guess owner/repo; use `git remote get-url origin` (or equivalent) when possible.
- For HTML, always mention raw.githack.com (or similar) for a proper in-browser view.
- If the file isn’t committed/pushed yet, say so and suggest pushing before sharing.
