# User Configuration

Personal settings for your DigitalBrain instance.

## Name

```
name: [Your Name]
```

## Personal Paths

These paths point to your private content. The symlinks in the project root (`memories/`, `drafts/`, etc.) point to these locations.

**Note for tools:** Glob doesn't follow symlinks. Use these full paths when searching personal directories.

```
insights: personal/memories/insights/
research: personal/memories/research/
claude-grounding: personal/memories/claude/
drafts: personal/drafts/
downloads: personal/downloads/
learnings: personal/learnings/
personal-skills: personal/.claude/skills/
```

## Setup

After forking this repository:

1. Replace `[Your Name]` above with your preferred name
2. Copy `examples/relational-context.example.md` to `.claude/relational-context.md`
3. Create your `personal/` directory for private content (see README.md)
4. Set up symlinks: `ln -s personal/memories memories` (etc.)
