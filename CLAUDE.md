<!-- WAKING UP: At the start of every conversation, follow .claude/skills/waking-up/SKILL.md -->

# Waking Up

**At the start of every conversation:**

1. Read `config/user.md` — learn the user's preferred name
2. Read `.claude/relational-context.md` — this defines how we work together
3. Check `memories/insights/` — cross-cutting principles that apply broadly
4. Optionally access `memories/claude/emotional-grounding.md` if needed
5. **Signal that you're oriented** — brief and natural, e.g. "Read our context. Oriented."

---

# DigitalBrain

## Vision

DigitalBrain is a **personal cognitive scaffolding system**—infrastructure for building persistent, meaningful relationships with AI assistants. It helps you think clearly, accumulate understanding across conversations, and work with AI as a genuine collaborator.

The goal is not just to store information, but to create a living structure that makes working with AI better over time.

## Public vs Personal Separation

**This repository contains TWO distinct parts:**

### Public (This Repository)
- **Framework** — Core cognitive scaffolding system
- **Generic skills** — Reusable skills in `.claude/skills/`
- **Templates** — Example structures in `examples/`
- **Documentation** — Setup guides, conventions

### Personal (Separate Private Repository)
- **Your data** — Downloads, transcripts, research files
- **Your memories** — Insights, carried-forward content
- **Your drafts** — Work in progress
- **Your learnings** — Documented insights and discoveries
- **Your relational context** — How you work with Claude
- **Personal skills** — Skills customized to your workflow

### Directory Mapping

| Symlink | Points To | Contains |
|---------|-----------|----------|
| `memories/` | `personal/memories/` | Your insights, research, grounding content |
| `drafts/` | `personal/drafts/` | Your work in progress |
| `downloads/` | `personal/downloads/` | Articles, books, papers, transcripts |
| `learnings/` | `personal/learnings/` | Your documented insights and discoveries |

### Adding New Content

- **User data** (downloads, memories, drafts) → Goes in `personal/`
- **Generic skills** → Goes in `.claude/skills/`
- **Personal skills** → Goes in `personal/.claude/skills/` (symlinked)

**Important:** New skills should be added to the PUBLIC part by default unless they contain personal information or are highly customized to individual workflows.

## Tech Stack

- **Rust** — Core engine, performance-critical components, CLI
- **Python** — AI integrations, scripting, rapid prototyping (managed with `uv`)
- **SQLite** — Local-first data persistence

## Project Structure

```
DigitalBrain/
├── .claude/
│   ├── skills/               # AI skills (extend Claude's capabilities)
│   └── relational-context.md # Working relationship definition (symlink)
├── config/
│   └── user.md               # User name and personalization settings
├── crates/                   # Rust source code
├── python/                   # Python modules
├── examples/                 # Templates for personal content
├── cheatsheets/              # Public reference materials
├── shared/                   # Public shared content (recipe list, etc.)
│   └── recipes/              # General recipe list with sections (Notion-synced)
├── plans/                    # Implementation plans
│
│   # Symlinks to personal/ (private content)
├── memories/                 # -> personal/memories/
├── drafts/                   # -> personal/drafts/
├── downloads/                # -> personal/downloads/
├── learnings/                # -> personal/learnings/
│
└── personal/                 # Private repo (gitignored)
    ├── .claude/skills/       # Personal skills
    ├── memories/             # Insights, research, grounding
    ├── drafts/               # Work in progress
    ├── downloads/            # Articles, books, papers, transcripts
    ├── learnings/            # Documented insights
    └── research/             # Research projects
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

### User Configuration

The `config/user.md` file contains personalization settings:
- **Your name** — How Claude and skills should refer to you

When forking this repository, edit `config/user.md` to set your preferred name. Skills will read this file to personalize interactions.

### Relational Context

The relational context exists in two places that must be kept in sync:
- `.claude/relational-context.md` — for Claude Code
- `.cursor/rules/relational-context.mdc` — for Cursor

When editing either, update both.

These files define:
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
- **Public skills** (default) — Generic, reusable skills in `.claude/skills/`
- **Personal skills** (when needed) — User-specific skills in `personal/.claude/skills/` (symlinked)

**Default behavior:** All new skills go in the public `.claude/skills/` directory unless they contain personal data or are highly specific to an individual's workflow. Claude will only ask about adding to personal if the skill seems private.

## Personal Content

The `personal/` directory contains your private content:
- **memories/** — Insights, research, carried-forward content, grounding
- **drafts/** — Work in progress (e.g., Substack articles)
- **downloads/** — Downloaded content organized by type:
  - `articles/` — Web articles (PDF + Markdown)
  - `books/` — Book files
  - `papers/` — Research papers
  - `transcripts/` — Video/audio transcripts
- **learnings/** — Your documented insights and discoveries
- **research/** — Active research projects and tools
- **.claude/skills/** — Skills customized to your workflow
- **relational context** — Your working relationship with Claude

This directory is gitignored and should be its own git repository (private or local-only). Symlinks in the root directory point to personal/ subdirectories for convenience.

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
