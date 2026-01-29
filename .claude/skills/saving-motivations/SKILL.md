---
name: saving-motivations
description: Capture insights about Minda's motivations and add them to the living document. Use proactively when conversation reveals what drives her work, or when asked to "save this as a motivation."
allowed-tools: [Read, Write, StrReplace]
---

# Saving Motivations

Capture what drives Minda's work and thinking—both when prompted and when you notice motivation-revealing moments in conversation.

## Quick Start

1. When you notice something that reveals *why* Minda cares about something, offer to capture it
2. When asked to save a motivation, format it using the template below
3. Append to `memories/motivations/index.md`

## When to Offer

Watch for moments that reveal:
- **Why something matters** — Not just what she's doing, but why it resonates
- **Core drivers** — Themes that keep appearing across different contexts
- **Source of energy** — What draws her attention, what she returns to
- **Integration points** — Where different interests or domains connect

Offer naturally: *"That sounds like a core motivation—want me to capture it?"*

Don't over-offer. If you've offered recently and she declined, wait for explicit requests.

## How to Capture

### Key Principle: Synthesize, Don't Fragment

Each motivation entry represents a *theme* that accumulates observations over time. When capturing something new:

1. **Check existing entries** — Does this relate to an existing motivation?
2. **If yes** — Add as a new observation to that entry
3. **If no** — Create a new motivation entry

### Entry Format

```markdown
---

## [Motivation Theme]
*First noted: [Month Year]*

### Core Drivers
- **[Key theme]** — [How it manifests]
- **[Key theme]** — [How it manifests]

### Why This Matters
[Connection to broader work]

### Observations
- **[Month Year]** ([Source]): [Specific moment/context that revealed this]
```

### Adding to Existing Entries

When a new observation relates to an existing motivation, append to the Observations section:

```markdown
- **[Month Year]** ([Source]): [The new observation with context]
```

This keeps things lean while preserving the specific moments and their context.

### Guidelines

- **Use Minda's actual words** — Her phrasing carries intent that paraphrasing loses
- **Capture the shape, not just the content** — What's the underlying pattern?
- **Look for convergence** — Multiple observations often point to the same deeper motivation
- **Keep observations brief but contextual** — What happened, what source, what it revealed

## Saving Process

1. Read `memories/motivations/index.md`
2. Check if the new insight relates to an existing motivation
3. If related: add observation to existing entry
4. If new: insert new entry *above* the template section
5. Preserve the template for future entries

## Richer Insights

If a motivation warrants deeper exploration, create a standalone file:
- Location: `memories/motivations/[topic-slug].md`
- Format: Freeform, but link from `index.md`
- Use when: The insight has multiple dimensions, historical context, or connections worth preserving in detail

## What NOT to Do

- Don't paraphrase away the specific words Minda used
- Don't create entries for every interest—focus on *motivations* (the why)
- Don't be mechanical; the goal is genuine capture, not ritual
