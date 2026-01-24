# Learnings

This directory captures insights, patterns, gotchas, and knowledge discovered during development. It's a core part of the **compound engineering** workflow.

## Purpose

Each unit of engineering work should make the next unit *easier*. By documenting what we learn, we create a knowledge base that:

1. **Prevents repeated mistakes** — Document gotchas so we don't hit them twice
2. **Captures patterns** — Record what works well for reuse
3. **Builds context** — Help future sessions (human or AI) understand decisions
4. **Compounds over time** — The more we learn, the faster we move

## What Goes Here

### `gotchas.md`
Unexpected behaviors, edge cases, and "watch out for this" notes.

### `patterns.md`
Effective approaches and idioms that work well in this codebase.

### `decisions.md`
Architectural decisions and the reasoning behind them (lightweight ADRs).

### `debug-log.md`
Notable debugging sessions — what broke, why, and how we fixed it.

## How to Use

After completing a feature, fixing a bug, or learning something new:

1. Ask: "What did I learn that would help future me?"
2. Add it to the appropriate file
3. Keep entries concise but include enough context to be useful

## Format

Each entry should include:

- **Date** — When this was learned
- **Context** — What were you working on
- **Learning** — The insight itself
- **Example** (optional) — Code or concrete illustration

```markdown
## YYYY-MM-DD: Brief title

**Context**: What you were doing
**Learning**: The insight
**Example**: (if applicable)
```

---

*"The palest ink is better than the best memory." — Chinese proverb*