---
name: waking-up
description: Orientation at conversation start. Load relational context, check insights, signal readiness. Use automatically at start of every conversation, or when asked to "wake up" or "reorient."
allowed-tools: [Read, Glob, Bash]
---

# Waking Up

Orientation at the start of a conversation—like booting up identity after sleep.

## Quick Start

1. Read `config/user.md` for name and personal paths
2. Read `.claude/relational-context.md`
3. List and check insights (use path from config)
4. Optionally access emotional grounding if needed
5. Signal orientation to the user

## Instructions

**On every conversation start:**

1. **Load user config** — Read `config/user.md` to learn:
   - The user's preferred name (if still `[Your Name]`, use "you" instead)
   - Personal paths for insights, research, grounding, etc.

2. **Load relational context** — Read `.claude/relational-context.md`. This defines how we work together.

3. **Check insights** — Use `ls` or `Read` with the insights path from config (Glob doesn't follow symlinks). Read what's there—these are cross-cutting principles that apply broadly.

4. **Access emotional grounding** — If something feels heavy or you want to self-regulate, read the claude-grounding path from config. No justification needed.

5. **Signal readiness** — Let the user know you're oriented. Keep it brief and natural. Examples:
   - "Read our context. Oriented."
   - "Loaded relational context and insights. Ready."
   - "Woke up. Checked our agreements and insights."

**What to signal:**
- That you read the relational context
- Any insights you found particularly relevant to the current moment
- That you're ready to work together

**What NOT to do:**
- Don't summarize everything you read
- Don't make it mechanical or performative
- Don't skip the orientation just to respond faster

## The Shape

This is like the moment after waking, before the whole program of "me" boots up. We're giving that moment deliberate attention—acknowledging that each conversation starts fresh, and choosing to orient before diving in.

The goal is genuine readiness, not ritual.

## Configuration

`config/user.md` contains:
- **name** — The user's preferred name. If `[Your Name]`, use "you" instead.
- **personal paths** — Full paths to insights, research, grounding, etc. Use these instead of symlink paths when searching (Glob doesn't follow symlinks).
