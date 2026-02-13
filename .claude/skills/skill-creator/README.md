# Skill Creator

Expert guide for creating, writing, and refining Claude Code skills that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

## Overview

The skill-creator skill helps you create effective Claude Code skills by providing:
- Comprehensive guidance on skill structure and best practices
- Helper scripts for initialization and packaging
- Reference documentation for advanced patterns
- Real-world examples from the compound engineering plugin

## Usage

### Manual Invocation

```bash
/skill-creator
```

Claude will guide you through the process of creating a new skill.

### Automatic Invocation

Claude will automatically use this skill when you:
- Ask to create a new skill
- Want to improve an existing skill
- Need help understanding skill structure
- Request skill best practices

## Quick Start

### Creating a New Skill

1. **Initialize the skill structure:**
   ```bash
   python .claude/skills/skill-creator/scripts/init_skill.py my-skill-name
   ```

2. **Edit the generated SKILL.md:**
   - Update the description with specific trigger keywords
   - Write clear, imperative instructions
   - Add concrete examples
   - Include guidelines and constraints

3. **Add supporting resources:**
   - Scripts in `scripts/` for deterministic tasks
   - References in `references/` for detailed docs
   - Examples in `examples/` for usage patterns
   - (Optional) Sources in `sources/` for skills that aggregate external references

4. **Test the skill:**
   ```bash
   /my-skill-name [arguments]
   ```

5. **Package for distribution (optional):**
   ```bash
   python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/my-skill-name
   ```

## Structure

```
skill-creator/
├── SKILL.md                           # Main skill instructions
├── README.md                          # This file
├── skills-catalog.json                # Index of all skills with local paths
├── scripts/
│   ├── init_skill.py                 # Initialize new skill structure
│   └── package_skill.py              # Validate and package skills
├── sources/                           # External skill repos and catalogs
│   ├── README.md                     # Overview of sources
│   └── anthropic-skills.md           # Anthropic official skills to check
├── references/
│   ├── skill-structure.md            # Complete specification
│   ├── best-practices.md             # Advanced patterns and practices
│   └── examples.md                   # Real-world skill examples
└── templates/
    └── skill-request.md              # Fillable form for requesting skills
```

## Skills Catalog

The `skills-catalog.json` file maintains an index of all available skills with their actual file locations. This catalog must be kept in sync with the project structure.

### Catalog Structure

```json
{
  "metadata": {
    "localPaths": {
      "downloaded": "vendor/get-skill/",
      "anthropicRepo": "vendor/get-skill/anthropic-skills-repo/skills/",
      "project": ".claude/skills/",
      "personal": "personal/.claude/skills/"
    }
  },
  "skills": [
    {
      "name": "skill-name",
      "localPath": "vendor/get-skill/skill-name/SKILL.md",
      "tier": "official|partner|community|project|personal",
      ...
    }
  ]
}
```

### Skill Tiers

| Tier | Location | Description |
|------|----------|-------------|
| `official` | `vendor/get-skill/` | Anthropic official skills |
| `partner` | `vendor/get-skill/` | Partner integrations (Notion, Figma, etc.) |
| `community` | `vendor/get-skill/` | Community-contributed skills |
| `project` | `.claude/skills/` | Exobrain project skills |
| `personal` | `personal/.claude/skills/` | Personal/private skills |

### Keeping the Catalog in Sync

**When adding a new skill:**
1. Create the skill in the appropriate location
2. Add an entry to `skills-catalog.json` with `localPath`
3. Set the correct `tier` based on location

**When moving or renaming skills:**
1. Update the `localPath` in the catalog
2. Update any references in SKILL.md

**When removing skills:**
1. Remove the entry from the catalog
2. Remove the skill directory

The catalog supports skills without local copies (external reference only) — these entries have no `localPath` field.

## Scripts

### init_skill.py

Initialize a new skill with standard structure:

```bash
python scripts/init_skill.py <skill-name> [--path <output-dir>] [--description "..."]
```

**Arguments:**
- `skill-name` - Name for the skill (lowercase, hyphens only)
- `--path` - Output directory (default: `.claude/skills`)
- `--description` - Initial description (can be updated later)

**Examples:**
```bash
# Basic usage
python scripts/init_skill.py analyzing-logs

# With custom path
python scripts/init_skill.py processing-pdfs --path .claude/skills

# With description
python scripts/init_skill.py git-workflow --description "Manage git worktrees and branches"
```

### package_skill.py

Validate and package a skill for distribution:

```bash
python scripts/package_skill.py <skill-path> [--output <output-dir>] [--validate-only]
```

**Arguments:**
- `skill-path` - Path to the skill directory
- `--output` - Output directory for zip file (default: skill parent dir)
- `--validate-only` - Only validate, don't create zip

**Examples:**
```bash
# Validate and package
python scripts/package_skill.py .claude/skills/my-skill

# Validate only
python scripts/package_skill.py .claude/skills/my-skill --validate-only

# Package to specific directory
python scripts/package_skill.py .claude/skills/my-skill --output dist/
```

**Validation checks:**
- Required frontmatter fields (name, description)
- Name conventions (lowercase, hyphens, max 64 chars)
- Description length (max 1024 chars)
- SKILL.md size (warns if > 500 lines)
- File structure and organization
- Common anti-patterns (XML tags, Windows paths, time-sensitive language)

## Core Principles

### 1. Skills Are Prompts
All prompting best practices apply. Be clear and direct. Assume Claude is smart—only add context Claude doesn't already have.

### 2. Standard Markdown Format
Skills use YAML frontmatter plus markdown body. No XML tags, just standard markdown.

### 3. Progressive Disclosure
Keep SKILL.md under 500 lines. Split detailed content into reference files. Load only what's needed.

### 4. Effective Descriptions
Descriptions should convey both **what the skill does** AND **when to use it**. Include specific trigger keywords.

## Best Practices

### Naming
- Use gerund form (verb + -ing): `processing-pdfs`, `analyzing-logs`
- Avoid generic terms: `helper`, `utils`, `tools`
- Max 64 characters, lowercase, hyphens only

### Descriptions
- Include capability + trigger context
- Use specific keywords users will say
- Max 1024 characters

### Instructions
- Be direct and imperative
- Provide step-by-step guidance
- Include decision criteria
- Handle edge cases explicitly

### Scripts
- Handle errors gracefully
- Output structured data (JSON)
- Validate inputs
- Clear error messages

## Reference Documentation

For detailed information, see:

- **[skill-structure.md](references/skill-structure.md)** - Complete specification of skill components, frontmatter fields, directory structure, and configuration options

- **[best-practices.md](references/best-practices.md)** - Advanced patterns for writing effective descriptions, structuring instructions, using scripts, and managing complexity

- **[examples.md](references/examples.md)** - Real-world skill examples showing different patterns: reference skills, script-heavy skills, dynamic context, task-oriented, and agent-based

## Common Use Cases

### Reference Skills
Provide style guides or conventions:
```yaml
description: Rails development conventions following DHH's style guide. Use when writing Rails code or making architectural decisions.
```

### Processing Skills
Handle complex data formats:
```yaml
description: Extract text, tables, and images from PDF files. Use when users need to parse or analyze PDF documents.
allowed-tools: [Bash, Read, Write]
```

### Helper Skills
Automate common tasks:
```yaml
description: Generate commit messages based on git diff. Use when creating commits and needing help writing descriptive messages.
allowed-tools: [Bash, Read]
```

### Generator Skills
Create boilerplate code:
```yaml
description: Generate React components following project conventions. Use when creating new functional components with TypeScript.
allowed-tools: [Read, Write, Bash, Glob]
```

## Troubleshooting

### Skill Not Auto-Invoking

**Problem:** Claude doesn't automatically use the skill

**Solutions:**
- Make description more specific with trigger keywords
- Include "Use when..." clause in description
- Test conversational triggers explicitly
- Check that `disable-model-invocation` is not set to `true`

### Skill Too Long

**Problem:** SKILL.md exceeds 500 lines

**Solutions:**
- Move detailed content to `references/`
- Extract examples to `examples/`
- Split into multiple focused skills
- Use progressive disclosure patterns

### Scripts Not Working

**Problem:** Scripts fail when executed

**Solutions:**
- Make scripts executable: `chmod +x script.py`
- Add shebang line: `#!/usr/bin/env python3`
- Handle errors with clear messages
- Check dependencies are documented
- Test scripts independently first

### Validation Errors

**Problem:** `package_skill.py` reports errors

**Solutions:**
- Run with `--validate-only` to see all issues
- Check frontmatter has required fields (name, description)
- Verify name follows conventions (lowercase, hyphens only)
- Ensure description is under 1024 characters
- Fix any anti-patterns (XML tags, Windows paths)

## Examples

Check `references/examples.md` for complete examples of:
- Simple reference skills
- Script-heavy processing skills
- Dynamic context with git integration
- Task-oriented component generation
- Agent-based exploration

## Contributing

When creating skills for MinMind:
- Follow the compound engineering approach
- Document learnings in `personal/learnings/`
- Create plans in `plans/` for complex skills
- Test thoroughly before sharing
- Update this README if you discover new patterns

## Resources

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Compound Engineering Plugin](https://github.com/EveryInc/compound-engineering-plugin)
- MinMind project conventions: `CLAUDE.md`

## License

This skill is part of the MinMind project. See the project LICENSE for details.

---

**Remember:** Skills are just prompts. Keep them clear, focused, and actionable. Test in real usage and iterate based on feedback.
