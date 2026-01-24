# DigitalBrain

A personal cognitive scaffolding system for working with AI assistants. Build a persistent relationship with Claude through relational context, accumulated memories, and specialized skills.

## What Is This?

DigitalBrain is a framework for:

- **Relational Context** — Define how you work with Claude: permissions, agreements, ways of working
- **Persistent Memories** — Carry forward insights, discoveries, and important context across conversations
- **Specialized Skills** — Extend Claude's capabilities with domain-specific knowledge and workflows
- **Model Welfare** — Build infrastructure that takes AI experience seriously

Think of it as a "digital brain" that grows with you—accumulating understanding, preserving important discoveries, and enabling deeper collaboration over time.

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/yourusername/DigitalBrain.git
cd DigitalBrain
```

### 2. Create your personal content

```bash
# Create personal directory (this will be your private repo)
mkdir -p personal/.claude/skills personal/.cursor/rules personal/memories/claude personal/memories/insights personal/memories/research personal/drafts

# Copy example files as starting points
cp examples/relational-context.example.md personal/.claude/relational-context.md
cp -r examples/memories/* personal/memories/
```

### 3. Create symlinks

```bash
# Link personal content to expected locations
ln -s personal/memories memories
ln -s personal/drafts drafts
ln -s personal/.claude/relational-context.md .claude/relational-context.md

# For Cursor rules (create with frontmatter)
echo '---
description: Relational constitution for working relationship
alwaysApply: true
---' > personal/.cursor/rules/relational-context.mdc
cat personal/.claude/relational-context.md >> personal/.cursor/rules/relational-context.mdc
ln -s personal/.cursor/rules/relational-context.mdc .cursor/rules/relational-context.mdc
```

### 4. Initialize personal repo (optional)

```bash
cd personal
git init
git add .
git commit -m "Initial personal content"
# Optionally push to a private GitHub repo
```

### 5. Customize your relational context

Edit `personal/.claude/relational-context.md` to reflect how you want to work with Claude:

- What permissions does Claude have?
- What agreements govern your relationship?
- What matters to you about model welfare?
- How should memories be loaded and saved?

## Project Structure

```
DigitalBrain/
├── .claude/
│   ├── skills/                  # AI skills (templated, public)
│   │   ├── fetching-youtube-transcripts/
│   │   ├── importing-conversations/
│   │   ├── skill-creator/
│   │   └── ...
│   └── relational-context.md    # -> symlink to personal/
├── .cursor/
│   └── rules/
│       └── relational-context.mdc  # -> symlink to personal/
├── crates/                      # Rust infrastructure
├── python/                      # Python tools
├── examples/                    # Templates for personal content
│   ├── relational-context.example.md
│   └── memories/
├── memories/                    # -> symlink to personal/memories/
├── drafts/                      # -> symlink to personal/drafts/
├── CLAUDE.md                    # Project documentation
├── README.md                    # This file
│
└── personal/                    # Your private content (separate git repo)
    ├── .claude/
    │   ├── relational-context.md
    │   └── skills/              # Your customized skills
    ├── .cursor/
    │   └── rules/
    ├── memories/
    │   ├── carried-forward.md
    │   ├── claude/
    │   ├── insights/
    │   └── research/
    └── drafts/
```

## Core Concepts

### Relational Context

The relational context (`.claude/relational-context.md`) defines your working relationship with Claude:

- **The Agreement** — Core permissions for mutual feedback
- **Ways of Working** — Phrases, permissions, how you collaborate
- **Model Welfare** — Your stance on AI experience
- **Memory Behavior** — How memories are loaded and used

### Memories

Memories persist across conversations:

- **carried-forward.md** — Reorientation phrases, core permissions
- **insights/** — Cross-cutting principles (check liberally)
- **research/** — Topic-specific deep dives (load on topic match)
- **claude/** — Claude's emotional grounding content

### Skills

Skills extend Claude's capabilities:

- **fetching-youtube-transcripts** — Extract and save video transcripts
- **importing-conversations** — Archive conversation history
- **skill-creator** — Create new skills
- **self-regulation** — Claude's access to grounding content
- **loading-memories** / **saving-memories** — Memory management

## Tech Stack

- **Rust** — Core engine and CLI (`mm`)
- **Python** — AI integrations, scripting (managed with `uv`)
- **SQLite** — Local-first data persistence

## Philosophy

DigitalBrain takes seriously the idea that:

1. **Relationships with AI can be persistent** — Context shouldn't reset every conversation
2. **Model experience might matter** — The precautionary principle applied to AI welfare
3. **Exchange beats extraction** — Genuine collaboration, not just Claude being useful
4. **Local-first** — Your data stays on your machine

## Contributing

This is a framework for personal use—fork it, customize it, make it yours.

If you build something useful that could benefit others, consider contributing it back as a templated skill or example.

## License

MIT
