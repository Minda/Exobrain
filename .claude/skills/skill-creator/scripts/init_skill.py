#!/usr/bin/env python3
"""
Initialize a new Claude Code skill with standard structure.

Usage:
    python init_skill.py <skill-name> [--path <output-dir>]

Example:
    python init_skill.py analyzing-logs --path .claude/skills
"""

import argparse
import sys
from pathlib import Path


SKILL_TEMPLATE = """---
name: {name}
description: {description}
allowed-tools: []
---

# {title}

Brief overview of what this skill does.

## Quick Start

Immediate actionable guidance for using this skill.

## Instructions

Core guidance Claude follows when using this skill:

1. **First step** - What to do first
2. **Second step** - What to do next
3. **Third step** - Final actions

## Examples

### Example 1: Common Use Case

**Input:**
```
User request example
```

**Output:**
```
Expected result
```

## Guidelines

**Do:**
- Clear actionable items
- Specific instructions
- Concrete examples

**Don't:**
- Vague guidance
- Assumptions about context
- Time-sensitive information

## Reference Files

For detailed information, see:
- `references/detailed-guide.md` - In-depth documentation
- `examples/sample-usage.md` - More examples

---

Remember: Keep instructions clear, focused, and actionable.
"""


README_TEMPLATE = """# {title}

{description}

## Usage

**Manual invocation:**
```
/{name} [arguments]
```

**Automatic invocation:**
Claude will use this skill automatically when the conversation matches the description.

## Structure

- `SKILL.md` - Main skill instructions
- `scripts/` - Helper scripts and utilities
- `references/` - Detailed documentation
- `examples/` - Usage examples and samples

## Development

To modify this skill:

1. Edit `SKILL.md` for main instructions
2. Add scripts to `scripts/` for deterministic tasks
3. Add references to `references/` for detailed docs
4. Add examples to `examples/` for concrete samples

## Testing

Test the skill by:
1. Manual invocation: `/{name}`
2. Conversational triggers using keywords from the description
3. Edge cases and error scenarios
"""


REFERENCE_TEMPLATE = """# {title} - Detailed Guide

This is a reference document for the {name} skill. It contains detailed information that supplements the main SKILL.md file.

## Overview

Detailed explanation of the skill's purpose and capabilities.

## Usage Patterns

### Pattern 1: Common Scenario

Description of when and how to use this pattern.

### Pattern 2: Advanced Usage

More complex usage scenarios.

## Configuration

If the skill requires configuration, document it here.

## API Reference

If the skill interacts with APIs, document them here.

## Troubleshooting

Common issues and their solutions:

### Issue 1
**Problem:** Description of the problem
**Solution:** How to fix it

### Issue 2
**Problem:** Another common issue
**Solution:** Resolution steps

## Historical Patterns

Lessons learned and patterns that have emerged over time.
"""


EXAMPLE_TEMPLATE = """# {title} - Examples

Concrete examples of using the {name} skill.

## Example 1: Basic Usage

**Scenario:** Common use case description

**Input:**
```
What the user provides or asks for
```

**Process:**
1. Step-by-step what the skill does
2. Decisions it makes
3. Actions it takes

**Output:**
```
The result produced
```

## Example 2: Advanced Usage

**Scenario:** More complex use case

**Input:**
```
Advanced request
```

**Process:**
1. How the skill handles complexity
2. Special considerations
3. Edge cases addressed

**Output:**
```
Complex result
```

## Example 3: Edge Case

**Scenario:** Handling unusual situations

**Input:**
```
Edge case request
```

**Process:**
1. How the skill detects the edge case
2. Special handling required
3. Fallback strategies

**Output:**
```
Appropriate handling
```
"""


def validate_skill_name(name: str) -> bool:
    """Validate skill name follows conventions."""
    if len(name) > 64:
        print(f"Error: Skill name too long (max 64 chars): {name}", file=sys.stderr)
        return False

    if not name.islower():
        print(f"Error: Skill name must be lowercase: {name}", file=sys.stderr)
        return False

    if not all(c.isalnum() or c == '-' for c in name):
        print(f"Error: Skill name can only contain lowercase letters, numbers, and hyphens: {name}", file=sys.stderr)
        return False

    if name.startswith('anthropic-') or name.startswith('claude-'):
        print(f"Error: Skill name cannot start with 'anthropic-' or 'claude-': {name}", file=sys.stderr)
        return False

    if any(word in name for word in ['helper', 'utils', 'tools']):
        print(f"Warning: Consider using a more specific name instead of generic terms like 'helper', 'utils', or 'tools'", file=sys.stderr)

    return True


def create_skill(name: str, output_dir: Path, description: str = None) -> bool:
    """Create a new skill with standard structure."""

    # Validate name
    if not validate_skill_name(name):
        return False

    # Create skill directory
    skill_dir = output_dir / name
    if skill_dir.exists():
        print(f"Error: Skill directory already exists: {skill_dir}", file=sys.stderr)
        return False

    try:
        # Create directories
        skill_dir.mkdir(parents=True)
        (skill_dir / "scripts").mkdir()
        (skill_dir / "references").mkdir()
        (skill_dir / "examples").mkdir()

        # Create title from name
        title = name.replace('-', ' ').title()

        # Use default description if not provided
        if not description:
            description = f"A skill for {name.replace('-', ' ')}. Update this description to be more specific."

        # Create SKILL.md
        skill_content = SKILL_TEMPLATE.format(
            name=name,
            title=title,
            description=description
        )
        (skill_dir / "SKILL.md").write_text(skill_content)

        # Create README.md
        readme_content = README_TEMPLATE.format(
            name=name,
            title=title,
            description=description
        )
        (skill_dir / "README.md").write_text(readme_content)

        # Create reference template
        reference_content = REFERENCE_TEMPLATE.format(
            name=name,
            title=title
        )
        (skill_dir / "references" / "detailed-guide.md").write_text(reference_content)

        # Create example template
        example_content = EXAMPLE_TEMPLATE.format(
            name=name,
            title=title
        )
        (skill_dir / "examples" / "sample-usage.md").write_text(example_content)

        # Create placeholder for scripts
        (skill_dir / "scripts" / ".gitkeep").write_text("")

        print(f"✓ Created skill: {skill_dir}")
        print(f"\nNext steps:")
        print(f"1. Edit {skill_dir}/SKILL.md - Update description and instructions")
        print(f"2. Add scripts to {skill_dir}/scripts/ (if needed)")
        print(f"3. Update references and examples")
        print(f"4. Test with: /{name}")

        return True

    except Exception as e:
        print(f"Error creating skill: {e}", file=sys.stderr)
        # Clean up partial creation
        if skill_dir.exists():
            import shutil
            shutil.rmtree(skill_dir)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new Claude Code skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_skill.py analyzing-logs
  python init_skill.py processing-pdfs --path .claude/skills
  python init_skill.py git-workflow --description "Manage git worktrees and branches"
        """
    )

    parser.add_argument(
        "name",
        help="Skill name (lowercase, hyphens only, e.g., 'analyzing-logs')"
    )

    parser.add_argument(
        "--path",
        type=Path,
        default=Path(".claude/skills"),
        help="Output directory for the skill (default: .claude/skills)"
    )

    parser.add_argument(
        "--description",
        help="Skill description (can be updated later in SKILL.md)"
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    args.path.mkdir(parents=True, exist_ok=True)

    # Create the skill
    success = create_skill(args.name, args.path, args.description)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
