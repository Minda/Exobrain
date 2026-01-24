---
name: skill-creator
description: Expert guide for creating, writing, and refining Claude Code skills. Use this when the user wants to create a new skill, update an existing skill, or learn about skill structure and best practices.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Skill Creator

A comprehensive guide for creating effective Claude Code skills that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

## Context

If you have a `memories/insights/` directory, check for relevant working principles before creating skills. Skills should embody the principles of how you work together.

## Quick Start

Creating a skill involves six steps:

1. **Understand the use case** - Clarify what the skill does and when it triggers
2. **Identify reusable components** - Scripts, references, examples
3. **Initialize the skill** - Use `init_skill.py` or create manually
4. **Write the SKILL.md** - Clear instructions using best practices
5. **Package the skill** - Validate and bundle for distribution (optional)
6. **Iterate and refine** - Test in real conversations and improve

## Core Principles

### Skills Are Prompts
All prompting best practices apply. Be clear and direct. Assume Claude is smart—only add context Claude doesn't already have.

### Standard Markdown Format
Skills use YAML frontmatter plus markdown body. No XML tags, just standard markdown headings and formatting.

### Progressive Disclosure
Keep SKILL.md under 500 lines. Split detailed content into reference files. Load only what's needed when needed.

### Effective Descriptions
Descriptions should convey both **what the skill does** AND **when to use it**. Write in third person for automatic invocation.

## Step 1: Understand the Use Case

Ask these questions:

**Functionality Questions:**
- What specific task or capability does this skill provide?
- What are concrete examples of when someone would use this?
- What tools or APIs does it need access to?
- Does it need to run scripts or access external resources?

**Trigger Questions:**
- Should Claude invoke this automatically or only manually (via `/skill-name`)?
- What keywords or phrases should trigger automatic invocation?
- What context clues indicate this skill is needed?

## Step 2: Identify Reusable Components

Organize your skill with these component types:

### Scripts (`scripts/`)
Use for deterministic tasks that bash/python handle better than Claude:
- API calls with authentication
- File parsing and data transformation
- Complex calculations
- Integration with external tools

### References (`references/`)
Use for detailed documentation that supplements the main SKILL.md:
- API documentation
- Configuration guides
- Advanced examples
- Historical patterns and gotchas

### Examples (`examples/`)
Use for concrete input/output pairs that show the skill in action:
- Before/after code samples
- Sample conversations
- Common usage patterns

## Step 3: Initialize the Skill

### Using the Helper Script

```bash
python .claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path .claude/skills
```

This creates:
```
skill-name/
├── SKILL.md           # Main instructions
├── scripts/           # Helper scripts
├── references/        # Detailed docs
└── examples/          # Usage examples
```

### Manual Creation

1. Create directory: `mkdir -p .claude/skills/<skill-name>`
2. Create SKILL.md with frontmatter
3. Add supporting directories as needed

## Step 4: Write the SKILL.md

### Required Frontmatter

```yaml
---
name: skill-name                    # Lowercase, hyphens only, max 64 chars
description: What it does AND when to use it. Be specific and include trigger keywords. Max 1024 chars.
allowed-tools: [Read, Write, Bash]  # Optional: tools Claude can use without asking
disable-model-invocation: false     # Optional: true = manual only
user-invocable: true                # Optional: false = hidden from menu
model: sonnet                       # Optional: specific model to use
context: fork                       # Optional: run in isolated subagent
agent: Explore                      # Optional: use specialized subagent
---
```

### Naming Conventions

**Use gerund form (verb + -ing):**
- ✅ `processing-pdfs`
- ✅ `analyzing-spreadsheets`
- ✅ `generating-commit-messages`

**Avoid:**
- ❌ `helper`, `utils`, `tools`
- ❌ `anthropic-*`, `claude-*`
- ❌ Plural nouns without action verbs

### Body Structure

Use this standard structure:

```markdown
# Skill Name

Brief overview sentence.

## Quick Start

Immediate actionable guidance. What to do first.

## Instructions

Core guidance Claude follows when using this skill.
- Step-by-step procedures
- Decision criteria
- Edge cases to handle

## Examples

Concrete input/output pairs showing the skill in action.

## Guidelines

Rules and constraints:
- What to do
- What NOT to do
- When to ask for clarification
```

### Writing Style

**Be Direct and Imperative:**
- ✅ "Create a plan before coding"
- ❌ "You might want to consider creating a plan"

**Provide Context Claude Lacks:**
- ✅ "The codebase uses thiserror for error handling"
- ❌ "Use appropriate error handling"

**Use Progressive Disclosure:**
- Keep SKILL.md focused on immediate guidance
- Link to references for detailed information
- Example: "See `references/api-docs.md` for complete API reference"

### Dynamic Context with `!` Commands

Inject live data into skills using shell commands:

```markdown
## Current Pull Request

!`gh pr view $ARGUMENTS --json title,body,files`

Based on the PR above, review the changes...
```

The `!` command runs before Claude sees the skill, injecting fresh data.

### String Substitutions

Use these variables in your skill:

- `$ARGUMENTS` - User input passed to the skill
- `${CLAUDE_SESSION_ID}` - Current session identifier

Example:
```markdown
Analyze the file: $ARGUMENTS
```

## Step 5: Package the Skill (Optional)

For distribution or sharing:

```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/<skill-name>
```

This:
- Validates the skill structure
- Checks required frontmatter
- Creates a distributable zip file
- Reports any issues

## Step 6: Iterate and Refine

Test your skill in real conversations:

1. **Manual invocation**: Try `/skill-name` with various arguments
2. **Automatic invocation**: Have conversations where the skill should trigger
3. **Edge cases**: Test with missing information, errors, ambiguity
4. **Refinement**: Update based on what works and what doesn't

### Common Improvements

- **Tighten the description** - Make trigger keywords more specific
- **Add examples** - Show concrete usage patterns
- **Extract references** - Move detailed docs out of SKILL.md
- **Add guard rails** - Specify what NOT to do
- **Improve scripts** - Handle errors, add validation

## Anti-Patterns to Avoid

❌ **XML tags in body content** - Use standard markdown only

❌ **Vague descriptions** - "A helpful skill" → "Expert guide for creating Claude Code skills"

❌ **Deeply nested references** - Keep references/ flat, one level max

❌ **Excessive options** - Provide smart defaults, only ask when necessary

❌ **Windows-style paths** - Use forward slashes: `.claude/skills/` not `.claude\skills\`

❌ **Scripts that punt to Claude** - If the script can handle it deterministically, do it in the script

❌ **Time-sensitive info** - Instead of "In 2024...", use "Historical pattern: ..."

## Reference Files

For detailed information, see:
- `references/skill-structure.md` - Complete specification of skill components
- `references/best-practices.md` - Detailed prompting and design patterns
- `references/examples.md` - More skill examples from the compound engineering plugin

## Getting Help

If you need help creating a skill:
1. Describe what you want the skill to do
2. Explain when it should be invoked
3. Share any scripts, docs, or examples you want to include
4. Claude will guide you through the creation process using this skill

---

**Remember:** Skills are just prompts. Keep them clear, focused, and actionable. Test in real usage and iterate based on feedback.
