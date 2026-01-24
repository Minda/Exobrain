# Skill Structure - Complete Specification

This document provides a complete specification of Claude Code skill components and structure.

## Directory Structure

```
skill-name/
├── SKILL.md              # Required: Main skill instructions
├── README.md             # Optional: Human-readable documentation
├── scripts/              # Optional: Executable scripts
│   ├── helper.py
│   └── process.sh
├── references/           # Optional: Detailed documentation
│   ├── api-docs.md
│   └── patterns.md
└── examples/             # Optional: Usage examples
    ├── basic.md
    └── advanced.md
```

## SKILL.md Structure

### Frontmatter (Required)

The frontmatter is a YAML block at the top of SKILL.md, delimited by `---`:

```yaml
---
name: skill-name
description: What it does AND when to use it
allowed-tools: [Read, Write, Bash]
disable-model-invocation: false
user-invocable: true
model: sonnet
context: fork
agent: Explore
argument-hint: "<arg> [options]"
---
```

### Frontmatter Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | ✓ | string | Skill identifier, becomes `/slash-command` |
| `description` | ✓ | string | What skill does AND when to use it (max 1024 chars) |
| `allowed-tools` | | array | Tools Claude can use without asking for approval |
| `disable-model-invocation` | | boolean | `true` = manual only, `false` = can auto-invoke (default: false) |
| `user-invocable` | | boolean | `false` = hidden from menu (default: true) |
| `model` | | string | Specific model to use (sonnet, opus, haiku) |
| `context` | | string | `fork` = run in isolated subagent |
| `agent` | | string | Specialized subagent type (Explore, Plan, etc.) |
| `argument-hint` | | string | CLI hint shown in help menu |

### Body Structure (Markdown)

The body follows standard markdown conventions:

```markdown
# Skill Title

Brief overview paragraph.

## Quick Start

Immediate actionable guidance.

## Instructions

Core step-by-step guidance Claude follows.

## Examples

Concrete input/output pairs.

## Guidelines

Rules and constraints.

## Reference Files

Links to supporting documentation.
```

## Scripts Directory

Scripts provide deterministic functionality that bash/python handle better than Claude.

### Naming Conventions

- Use descriptive names: `generate_report.py`, `validate_config.sh`
- Add shebang lines: `#!/usr/bin/env python3`
- Make executable: `chmod +x script.py`

### Best Practices

**Do:**
- Handle errors gracefully with clear messages
- Accept arguments via command-line flags
- Output structured data (JSON, CSV) when possible
- Validate inputs before processing
- Return meaningful exit codes (0 = success, non-zero = error)

**Don't:**
- Punt error handling to Claude
- Assume dependencies are installed
- Use hardcoded paths
- Require interactive input (use flags/args instead)

### Example Script Template

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.

Usage:
    python script.py <arg1> [--option value]
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("input", help="Input description")
    parser.add_argument("--option", help="Optional parameter")

    args = parser.parse_args()

    try:
        # Do work
        result = process(args.input, args.option)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## References Directory

References contain detailed documentation that supplements SKILL.md.

### When to Use References

- API documentation is lengthy (>100 lines)
- Historical patterns and gotchas
- Configuration guides
- Advanced usage patterns
- Architecture diagrams

### Structure

Keep references **flat** (one level only):

```
references/
├── api-docs.md          # ✓ Good
├── patterns.md          # ✓ Good
└── config-guide.md      # ✓ Good
```

**Avoid nested directories:**

```
references/
└── advanced/            # ✗ Avoid
    └── patterns.md
```

### Linking from SKILL.md

Reference files using relative paths:

```markdown
## Reference Files

For detailed information, see:
- `references/api-docs.md` - Complete API reference
- `references/patterns.md` - Common usage patterns
```

## Examples Directory

Examples show the skill in action with concrete input/output pairs.

### Structure

Organize by complexity or use case:

```
examples/
├── basic-usage.md       # Simple, common cases
├── advanced-usage.md    # Complex scenarios
└── edge-cases.md        # Unusual situations
```

### Example Template

```markdown
# Example: Use Case Name

## Scenario
Brief description of when this applies.

## Input
\`\`\`
What the user provides
\`\`\`

## Process
1. What the skill does first
2. Decisions it makes
3. Actions it takes

## Output
\`\`\`
The result produced
\`\`\`

## Notes
Additional context or gotchas.
```

## Dynamic Context with `!` Commands

Inject live data into skills using shell commands prefixed with `!`:

```markdown
## Current Branch Status

!`git status --short`

Based on the git status above, determine what needs to be committed...
```

The `!` command:
- Runs **before** Claude sees the skill
- Output is injected into the prompt
- Useful for: git info, file contents, API responses, system state

### Examples

```markdown
# Get PR information
!`gh pr view $ARGUMENTS --json title,body,files`

# Read configuration
!`cat config.json`

# Check system info
!`uname -a`
```

## String Substitutions

Use these variables in your skill:

| Variable | Description | Example |
|----------|-------------|---------|
| `$ARGUMENTS` | User input passed to skill | `/skill foo bar` → `foo bar` |
| `${CLAUDE_SESSION_ID}` | Current session ID | Unique per conversation |

### Usage

```markdown
Analyze the file: $ARGUMENTS

Session context: ${CLAUDE_SESSION_ID}
```

## File Sizes and Limits

| Component | Recommended Limit | Notes |
|-----------|------------------|-------|
| SKILL.md | 500 lines | Move details to references |
| Reference files | 1000 lines | Split if larger |
| Scripts | No hard limit | Keep focused, single purpose |
| Total skill size | 5MB | Warning if larger |

## Tool Access Control

Use `allowed-tools` to specify which tools Claude can use **without asking for approval**:

```yaml
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
```

Available tools:
- `Read` - Read files
- `Write` - Create new files
- `Edit` - Modify existing files
- `Bash` - Execute shell commands
- `Glob` - File pattern matching
- `Grep` - Content search
- `Task` - Launch specialized agents
- `WebFetch` - Fetch web content
- `WebSearch` - Search the web

**Security note:** Only include tools the skill legitimately needs. Overly permissive `allowed-tools` can be a security risk.

## Context Modes

### Default Context (inline)

Skill runs in the main conversation context:
```yaml
# No context field needed
```

Use for: Skills that extend the main conversation

### Forked Context (isolated)

Skill runs in an isolated subagent:
```yaml
context: fork
```

Use for:
- Complex multi-step tasks
- Long-running operations
- When you want clean separation

## Specialized Agents

Use the `agent` field to specify a specialized subagent:

```yaml
agent: Explore
```

Available agent types:
- `Explore` - Fast codebase exploration (glob, grep, read)
- `Plan` - Planning and task breakdown
- Custom agents defined in your project

## Progressive Disclosure

The skill loading process follows progressive disclosure:

1. **Metadata first** - Claude sees frontmatter (name, description)
2. **SKILL.md on trigger** - Loads when skill is invoked
3. **References on demand** - Loads when Claude accesses them
4. **Scripts on execution** - Runs when called

This keeps the initial payload small and only loads what's needed.

## Validation Checklist

Before packaging a skill, verify:

- [ ] SKILL.md exists and has valid frontmatter
- [ ] Name is lowercase, hyphens only, max 64 chars
- [ ] Description is clear and includes trigger keywords
- [ ] SKILL.md is under 500 lines
- [ ] Scripts are executable (`chmod +x`)
- [ ] References are flat (no nested directories)
- [ ] No XML tags in markdown body
- [ ] No Windows-style paths
- [ ] No time-sensitive language
- [ ] Examples are concrete and actionable

Use `package_skill.py --validate-only` to check automatically.
