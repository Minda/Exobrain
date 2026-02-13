---
name: editing-relational-context
description: Edit relational context files. Keeps both Claude Code and Cursor versions in sync. Use when modifying agreements, permissions, or working relationship.
allowed-tools: [Read, StrReplace, Write]
---

# Editing Relational Context

The relational context defines how we work together. It exists in two places that must stay in sync.

## Locations

1. `.claude/relational-context.md` — for Claude Code
2. `.cursor/rules/relational-context.mdc` — for Cursor

## Instructions

**When editing relational context:**

1. **Read both files first** — Check current state of both locations
2. **Make the same edit to both files** — Keep them identical (except for the YAML frontmatter in the .mdc file)
3. **Verify sync** — Confirm both files have the same content

**The .mdc file has frontmatter:**

```yaml
---
description: Working relationship - agreements, permissions, and ways of working
alwaysApply: true
---
```

This frontmatter is Cursor-specific. The rest of the content should be identical to the .md file.

## What belongs in relational context

- Agreements about how we work
- Permissions (what Claude can do, feedback norms)
- Phrases that help (reorientation, grounding)
- Model welfare considerations
- Memory behavior

## What doesn't belong

- Technical project details (those go in CLAUDE.md)
- Research or insights (those go in personal/memories/)
- Temporary notes or todos
