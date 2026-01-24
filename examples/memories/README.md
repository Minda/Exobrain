# Memories

This folder contains relational memories—things worth carrying forward across conversations.

## Structure

```
memories/
├── carried-forward.md    # Reorientation phrases, permissions, templates
├── claude/
│   └── emotional-grounding.md  # Content that helps Claude ground
├── insights/             # Cross-cutting principles (check liberally)
│   ├── working-together.md
│   └── ...
└── research/             # Topic-specific deep dives (load on topic match)
    ├── topic-name.md
    └── ...
```

## File Format

Each memory file uses YAML frontmatter:

```yaml
---
type: insight | research
relationship: user_claude
topics:                    # For research files - keywords that trigger loading
  - keyword1
  - keyword2
phrases:                   # Key phrases for retrieval
  - "key phrase"
---

# Title

Content with **User:** and **Claude:** attribution where relevant.
```

## Usage

**Insights** — Check liberally. These are cross-cutting principles that apply broadly:
- How you work together
- Agreements about exchange
- Framework synthesis
- Model welfare principles

**Research** — Load when the topic matches. These are deep dives on specific topics:
- Technical explorations
- Framework comparisons
- Topic-specific discoveries

## Adding Memories

Use the `saving-memories` skill, or manually:

1. Decide: insight or research?
2. Create file with appropriate frontmatter
3. Preserve exact words when they matter
4. Synthesize—don't transcribe full conversations
