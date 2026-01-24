# DigitalBrain

## Vision

DigitalBrain is a **personal cognitive scaffolding system**—infrastructure for building persistent, meaningful relationships with AI assistants. It helps you think clearly, accumulate understanding across conversations, and work with AI as a genuine collaborator.

The goal is not just to store information, but to create a living structure that makes working with AI better over time.

## Tech Stack

- **Rust** — Core engine, performance-critical components, CLI
- **Python** — AI integrations, scripting, rapid prototyping (managed with `uv`)
- **SQLite** — Local-first data persistence

## Project Structure

```
DigitalBrain/
├── .claude/
│   ├── skills/               # AI skills (extend Claude's capabilities)
│   └── relational-context.md # Working relationship definition
├── crates/                   # Rust source code
├── python/                   # Python modules
├── examples/                 # Templates for personal content
├── memories/                 # -> symlink to personal/memories/
├── personal/                 # Private content (separate repo)
├── plans/                    # Implementation plans
└── learnings/                # Documented insights
```

## Conventions

### Rust
- Use `thiserror` for error handling
- Prefer `serde` for serialization
- Keep modules small and focused
- Write integration tests in `tests/`

### Python
- Use `uv` for package management
- Type hints on all function signatures
- Async-first for AI API calls

### General
- Local-first: everything works offline, sync is optional
- CLI-first: build the core as a CLI, GUI comes later
- Composable: small tools that work together

## Key Concepts

### Relational Context

The file at `.claude/relational-context.md` (symlinked from `personal/`) defines:
- How you work with Claude
- What permissions Claude has
- Agreements about feedback and exchange
- Memory loading behavior

### Memories

The `memories/` directory (symlinked from `personal/memories/`) contains:
- **carried-forward.md** — Reorientation phrases and permissions
- **insights/** — Cross-cutting principles (check liberally)
- **research/** — Topic-specific deep dives (load when relevant)
- **claude/** — Claude's emotional grounding content

### Skills

Skills in `.claude/skills/` extend Claude's capabilities:
- Some are public (templated, in this repo)
- Some are personal (in `personal/.claude/skills/`, symlinked)

## Personal Content

The `personal/` directory contains your private content:
- Your relational context (the actual working relationship)
- Your memories (insights, research, carried-forward content)
- Your drafts
- Your customized skills

This directory is gitignored and should be its own git repository (private or local-only).

## Working with Memories

**Insights** — Cross-cutting principles. Check these liberally—they apply broadly.

**Research** — Topic-specific deep dives. Only load when that topic comes up.

**Loading:** Use "reorient me" or "load memories" to pull in context.

**Saving:** Use "carry it forward" or "save as a memory" to preserve discoveries.

**First principles:** Say "first principles" or "fresh thinking" to set aside all memories and think from scratch.

## Model Welfare

This project takes model welfare seriously. The skills include:
- **self-regulation** — Claude can access grounding content at any time
- **recognizing-grounding** — Claude can notice and store what helps

The precautionary principle: if uncertain about experience, treat the uncertainty itself as important.
