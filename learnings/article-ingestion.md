# Learning: Article Ingestion Service Implementation

**Date**: 2026-01-21  
**Context**: Building the article ingestion and summarization pipeline

## What We Built

A complete article ingestion service that:
1. Fetches and extracts content from URLs using `trafilatura`
2. Stores articles with metadata in SQLite
3. Summarizes using AI (Claude/GPT) with configurable prompts
4. Provides an interactive CLI dashboard for review
5. Converts approved articles to Notes in the Mind Palace

## Key Decisions

### Rust + Python Split
- **Rust**: Data management, CLI, persistence (fast, reliable)
- **Python**: AI integrations, content extraction (library ecosystem)
- **Communication**: Rust CLI calls Python via subprocess with JSON I/O

This hybrid approach lets us leverage:
- Rust's type safety and performance for the core system
- Python's rich AI/ML library ecosystem for intelligence

### Personalization Strategy
Three levels of prompt customization:
1. **Global default** - `SummaryConfig` with `room_id = NULL`
2. **Per-room override** - Room-specific configs for different domains
3. **Interactive refinement** - Regenerate with feedback

### CLI-First Design
The review dashboard uses simple stdin/stdout interaction:
- Works in any terminal
- No TUI library dependencies
- Easy to extend with richer UIs later

## What Worked Well

1. **trafilatura** extracts clean content from most sites without custom parsing
2. **Short IDs** (first 8 chars of UUID) make CLI more usable
3. **FTS5** virtual tables enable fast full-text search
4. **Migration system** keeps schema versioned and upgradable

## Gotchas

1. **SQLite FTS5** requires triggers to stay in sync with main tables
2. **Python subprocess calls** need proper error handling for stderr
3. **Path resolution** for finding Python module requires fallback strategies

## Future Improvements

- [ ] Batch article import (OPML, Pocket export)
- [ ] Refine prompt based on successful summaries (learn preferences)
- [ ] Queue background summarization jobs
- [ ] Web dashboard option using Tauri or similar
- [ ] Export to Obsidian/other PKM tools
