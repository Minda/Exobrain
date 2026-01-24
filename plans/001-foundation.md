# Plan 001: Foundation Architecture

**Status**: Draft  
**Created**: 2025-01-20  
**Author**: Claude + Min  

## Overview

Establish the foundational architecture for MinMind—the scaffolding upon which the Mind Palace will be built. This plan focuses on the core primitives and data structures that everything else will build upon.

## Goals

1. Define the core domain model (Rooms, Notes, Links, Geniuses)
2. Set up Rust project structure with workspace
3. Create Python package for AI integrations
4. Implement basic CLI skeleton
5. Establish SQLite schema for local persistence

## Non-Goals (for this phase)

- GUI or web interface
- Sync/collaboration features
- Advanced AI orchestration
- Plugin system

## Architecture

### Core Concepts

```
┌─────────────────────────────────────────────────────┐
│                    MIND PALACE                       │
├─────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │  Room   │──│  Room   │──│  Room   │  ...        │
│  │ (Work)  │  │(Personal)│ │(Learning)│             │
│  └────┬────┘  └────┬────┘  └────┬────┘             │
│       │            │            │                   │
│  ┌────▼────────────▼────────────▼────┐             │
│  │            Notes / Ideas          │             │
│  │    (linked, tagged, searchable)   │             │
│  └────────────────┬──────────────────┘             │
│                   │                                 │
├───────────────────▼─────────────────────────────────┤
│                 BASEMENT                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Genius 1 │  │ Genius 2 │  │ Genius N │         │
│  │ (Claude) │  │ (GPT)    │  │ (Local)  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

### Domain Model

#### Room
A conceptual space for organizing related thoughts and work.

```rust
struct Room {
    id: Uuid,
    name: String,
    description: Option<String>,
    parent_id: Option<Uuid>,  // Rooms can nest
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}
```

#### Note
The atomic unit of thought/information.

```rust
struct Note {
    id: Uuid,
    room_id: Uuid,
    title: String,
    content: String,          // Markdown
    note_type: NoteType,      // Idea, Task, Reference, Log
    status: Option<Status>,   // For actionable notes
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

enum NoteType {
    Idea,       // A thought to develop
    Task,       // Something to execute
    Reference,  // Information to recall
    Log,        // A record of what happened
}

enum Status {
    Active,
    Completed,
    Archived,
}
```

#### Link
Bidirectional connections between notes.

```rust
struct Link {
    id: Uuid,
    source_id: Uuid,
    target_id: Uuid,
    link_type: Option<String>,  // "related", "blocks", "supports", etc.
    created_at: DateTime<Utc>,
}
```

#### Genius
An AI agent that can be consulted.

```rust
struct Genius {
    id: Uuid,
    name: String,
    provider: Provider,       // Anthropic, OpenAI, Local
    model: String,            // "claude-3-opus", "gpt-4", etc.
    system_prompt: Option<String>,
    config: serde_json::Value,
}

enum Provider {
    Anthropic,
    OpenAI,
    Ollama,
    Custom,
}
```

### Project Structure

```
MinMind/
├── Cargo.toml              # Workspace root
├── CLAUDE.md
├── plans/
├── learnings/
│
├── crates/
│   ├── minmind-core/       # Domain model, traits
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── room.rs
│   │       ├── note.rs
│   │       ├── link.rs
│   │       └── genius.rs
│   │
│   ├── minmind-store/      # SQLite persistence
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs
│   │       └── sqlite.rs
│   │
│   └── minmind-cli/        # CLI application
│       ├── Cargo.toml
│       └── src/
│           └── main.rs
│
└── python/
    ├── pyproject.toml      # uv managed
    └── minmind/
        ├── __init__.py
        └── geniuses/       # AI provider integrations
            ├── __init__.py
            ├── base.py
            ├── anthropic.py
            └── openai.py
```

### SQLite Schema

```sql
-- Rooms table
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    parent_id TEXT REFERENCES rooms(id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Notes table
CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(id),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    note_type TEXT NOT NULL,
    status TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Links table
CREATE TABLE links (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES notes(id),
    target_id TEXT NOT NULL REFERENCES notes(id),
    link_type TEXT,
    created_at TEXT NOT NULL
);

-- Geniuses table
CREATE TABLE geniuses (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    system_prompt TEXT,
    config TEXT NOT NULL  -- JSON
);

-- Full-text search for notes
CREATE VIRTUAL TABLE notes_fts USING fts5(
    title, content, content='notes', content_rowid='rowid'
);

-- Indexes
CREATE INDEX idx_notes_room ON notes(room_id);
CREATE INDEX idx_links_source ON links(source_id);
CREATE INDEX idx_links_target ON links(target_id);
```

## Implementation Steps

### Step 1: Rust Workspace Setup
- [ ] Create `Cargo.toml` workspace
- [ ] Initialize `minmind-core` crate
- [ ] Initialize `minmind-store` crate  
- [ ] Initialize `minmind-cli` crate

### Step 2: Core Domain Model
- [ ] Implement `Room` struct and methods
- [ ] Implement `Note` struct and methods
- [ ] Implement `Link` struct and methods
- [ ] Implement `Genius` struct (interface only)
- [ ] Add serde serialization

### Step 3: SQLite Persistence
- [ ] Set up `rusqlite` with migrations
- [ ] Implement CRUD for rooms
- [ ] Implement CRUD for notes
- [ ] Implement CRUD for links
- [ ] Implement full-text search

### Step 4: CLI Skeleton
- [ ] Set up `clap` for argument parsing
- [ ] Implement `room` subcommand (list, create, delete)
- [ ] Implement `note` subcommand (list, create, edit, delete)
- [ ] Implement `search` subcommand

### Step 5: Python Package Setup
- [ ] Create `pyproject.toml` with uv
- [ ] Create base `Genius` abstract class
- [ ] Implement Anthropic integration
- [ ] Implement OpenAI integration

## Success Criteria

1. Can create rooms and nest them
2. Can create notes in rooms with different types
3. Can link notes together
4. Can search notes by content
5. Can invoke a Genius from Python and get a response
6. All operations work via CLI

## Open Questions

1. Should notes support attachments (images, files)?
2. How should we handle conversation history with Geniuses?
3. Do we need tags in addition to rooms for organization?
4. Should the Rust CLI call Python for Genius interactions, or should we have separate interfaces?

## Dependencies

### Rust
- `uuid` — ID generation
- `chrono` — Timestamps
- `serde` / `serde_json` — Serialization
- `rusqlite` — SQLite
- `clap` — CLI parsing
- `thiserror` — Error handling

### Python
- `anthropic` — Claude API
- `openai` — OpenAI API
- `pydantic` — Data validation
- `httpx` — HTTP client (async)

---

## Notes

*Space for notes during implementation*