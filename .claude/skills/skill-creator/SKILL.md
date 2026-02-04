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

Creating a skill involves seven steps:

1. **Check existing skills catalog** - Review 200+ available skills before creating new ones
2. **Understand the use case** - Clarify what the skill does and when it triggers
3. **Identify reusable components** - Scripts, references, examples
4. **Initialize the skill** - Use `init_skill.py` or create manually
5. **Write the SKILL.md** - Clear instructions using best practices
6. **Package the skill** - Validate and bundle for distribution (optional)
7. **Iterate and refine** - Test in real conversations and improve

## Core Principles

### Skills Are Prompts
All prompting best practices apply. Be clear and direct. Assume Claude is smart—only add context Claude doesn't already have.

### Standard Markdown Format
Skills use YAML frontmatter plus markdown body. No XML tags, just standard markdown headings and formatting.

### Progressive Disclosure
Following the Agent Skills Discovery RFC pattern, minimize context usage through three levels:
1. **Index metadata** (~100 tokens) - Name and description only
2. **Full instructions** (<5000 tokens) - Complete SKILL.md when activated
3. **Supporting resources** - Scripts/references fetched on-demand

Keep SKILL.md under 500 lines. Split detailed content into reference files. Load only what's needed when needed.

### Effective Descriptions
Descriptions should convey both **what the skill does** AND **when to use it**. Write in third person for automatic invocation.

## Step 0: Check Existing Skills Catalog

Before creating a new skill, check if one already exists in the catalog of 126 indexed skills.

### Check the Catalog

Read the skills catalog to search for existing solutions:
```bash
# Search by name keyword
cat .claude/skills/skill-creator/skills-catalog.json | jq '.skills[] | select(.name | contains("keyword"))'

# Search by category
cat .claude/skills/skill-creator/skills-catalog.json | jq '.skills[] | select(.category == "Development")'

# Find skills with local copies
cat .claude/skills/skill-creator/skills-catalog.json | jq '.skills[] | select(.localPath != null)'
```

### Skill Tiers and Locations

The catalog indexes skills across five tiers with actual file locations:

| Tier | Count | Location | Description |
|------|-------|----------|-------------|
| `official` | 16 | `get-skill/` | Anthropic official skills |
| `partner` | 40 | `get-skill/` | Partner integrations (Notion, Figma, Vercel, etc.) |
| `community` | 44 | `get-skill/` | Community-contributed skills |
| `project` | 19 | `.claude/skills/` | DigitalBrain project skills |
| `personal` | 7 | `personal/.claude/skills/` | Personal/private skills |

Skills with a `localPath` field have local copies you can read directly. Skills without it are external references only.

### If a Similar Skill Exists

1. **Read the local copy** — If `localPath` exists, read the SKILL.md directly
2. **Check if it meets your needs** — Many skills are configurable
3. **Consider extending it** — Fork and modify rather than duplicate
4. **Install from source** — Use the `githubUrl` to add to your project

### Common Skill Categories

Before creating a new skill, check these popular categories:
- **Document Processing**: PDF, Word, Excel, PowerPoint manipulation
- **Development**: Testing, debugging, code review, git workflows
- **AI/ML**: Model training, datasets, evaluation, research
- **Security**: Vulnerability analysis, fuzzing, secure coding
- **Infrastructure**: Terraform, Kubernetes, AWS, deployment
- **Creative & Design**: Art generation, UI design, video creation
- **Workflow**: Session management, memory, personal workflows

If no existing skill matches your needs, proceed to Step 1.

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
- File parsing and data transformation (especially when files are large)
- Complex calculations
- Integration with external tools

**IMPORTANT for Large Files:**
When dealing with large files (>10MB), ALWAYS use scripts instead of loading content into Claude's context:
- Parse and extract only what's needed
- Use streaming/chunked processing
- Generate summaries or indices
- Return structured data, not raw content

Example: For a 277MB JSON file, create a Python script that:
1. Loads the file in the script
2. Extracts schema/statistics/samples
3. Returns only the analysis results to Claude
Never use Read tool or cat/head commands that would load large content into context.

### References (`references/`)
Use for detailed documentation that supplements the main SKILL.md:
- API documentation
- Configuration guides
- Advanced examples
- Historical patterns and gotchas

### Sources (`sources/`)
Use for curated external skill repositories and catalogs to check *before* building:
- Anthropic official skills repo
- Community catalogs and indexes
- Canonical implementations to reference or extend

*(The skill-creator itself has a `sources/` directory; individual skills add it only when they aggregate external references.)*

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

The skill-creator itself also has:
```
sources/               # External skill repos and catalogs (check before building)
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

### Available Tools

These are the 17 built-in tools you can specify in `allowed-tools`:

| Tool | Description | Requires Permission |
|------|-------------|---------------------|
| `Read` | Read file contents | No |
| `Glob` | Find files by pattern | No |
| `Grep` | Search file contents | No |
| `Task` | Launch a sub-agent | No |
| `TodoWrite` | Create/manage task lists | No |
| `BashOutput` | Retrieve output from background shell | No |
| `KillShell` | Kill a background bash shell | No |
| `AskUserQuestion` | Ask user multiple-choice questions | No |
| `Write` | Create or overwrite files | Yes |
| `Edit` | Targeted edits to files | Yes |
| `Bash` | Execute shell commands | Yes |
| `NotebookEdit` | Modify Jupyter notebook cells | Yes |
| `WebFetch` | Fetch a URL | Yes |
| `WebSearch` | Search the web | Yes |
| `Skill` | Invoke another skill | Yes |
| `SlashCommand` | Run a custom slash command | Yes |
| `ExitPlanMode` | Prompt user to exit plan mode | Yes |

**Tip:** Tools that don't require permission are safe to include in `allowed-tools`. For tools that require permission, the user will still be prompted unless you add them to `allowed-tools`.

**Pattern matching** is supported for granular control:

```yaml
allowed-tools:
  - Bash(git *)           # Only git commands
  - Bash(npm run test *)  # Only test commands
  - Bash(gh *)            # Only GitHub CLI
  - Read(~/.zshrc)        # Specific file
  - Read(./secrets/**)    # Glob patterns
```

### Naming Conventions

**Follow the Agent Skills Discovery RFC standard:**
- 1-64 characters, lowercase alphanumeric and hyphens only
- No leading/trailing or consecutive hyphens
- Consistent with `.well-known/skills/` URI pattern

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

### Local Distribution

For distribution or sharing:

```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/<skill-name>
```

This:
- Validates the skill structure
- Checks required frontmatter
- Creates a distributable zip file
- Reports any issues

### Web Distribution via .well-known

Following the Agent Skills Discovery RFC, you can make skills discoverable at:
```
https://yoursite.com/.well-known/skills/
```

To publish for web discovery:

1. **Create index.json** listing all skills:
```json
{
  "skills": [{
    "name": "your-skill-name",
    "description": "Brief description for discovery",
    "files": ["your-skill-name/SKILL.md", "..."]
  }]
}
```

2. **Deploy to web server** maintaining the structure
3. **Test discovery** at `/.well-known/skills/index.json`

This enables automatic discovery by any agent implementing the RFC standard.

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

❌ **Loading large files into context** - Never use Read tool or show file contents for files >10MB. Instead:
  - Create a script that processes the file and returns summaries/analysis
  - Use streaming or chunked processing in the script
  - Extract only the specific data needed
  - Return structured results, not raw content
  Example: For a 277MB JSON, create a Python script that analyzes it and returns only the schema and statistics

## Anthropic Skills Repository

**Official reference:** [https://github.com/anthropics/skills](https://github.com/anthropics/skills)

Anthropic’s public repo contains example skills (creative, technical, enterprise, document) and the official Agent Skills spec. When creating a new skill:

1. **Check before building** — See `sources/anthropic-skills.md` for a curated list of skills to consider **downloading or referencing first** so you don’t duplicate existing capabilities.
2. **Use the template** — The repo’s [template](https://github.com/anthropics/skills/tree/main/template) and [spec](https://github.com/anthropics/skills/tree/main/spec) align with this skill’s structure.
3. **Install via Claude Code** — In Claude Code you can add the marketplace (`/plugin marketplace add anthropics/skills`) and install `document-skills` or `example-skills`, then invoke by name (e.g. “Use the PDF skill to…”).

Disclaimer: skills there are for demonstration; implementations in your environment may differ. Test before relying on them.

## Reference Files

**When helping create or refine a skill, scan each row below against the use case. Load the relevant reference file when a topic applies.**

### `references/skill-structure.md` — Complete Specification

| Section | What's There |
|---------|--------------|
| Directory Structure | File layout, required vs optional files |
| Frontmatter Fields | All YAML fields with types and defaults |
| Body Structure | Standard markdown sections |
| Scripts Directory | Script conventions, execution patterns |
| References Directory | How to organize supplementary docs |
| Dynamic Context | `!` commands, string substitutions |
| File Sizes & Limits | Token budgets, line limits |
| Tool Access Control | `allowed-tools` patterns |
| Context Modes | `fork` mode, isolated subagents |
| Validation Checklist | Pre-publish verification |

### `references/best-practices.md` — Writing & Design Patterns

| Section | What's There |
|---------|--------------|
| Writing Effective Descriptions | Anatomy of good descriptions, patterns |
| Prompting Best Practices | Direct style, assume Claude is smart |
| Structuring Instructions | Step-by-step vs decision trees |
| Using Scripts Effectively | When to script vs let Claude code |
| Dynamic Context Patterns | Injecting live data |
| Managing Skill Complexity | Quick mode vs advanced mode |
| Testing Skills | Manual, automatic, edge case testing |
| Naming Conventions | Gerund form, what to avoid |
| Common Anti-Patterns | 15+ mistakes to avoid |
| Maintenance | Version control, changelogs, updates |

### `references/examples.md` — 5 Complete Skill Examples

| Example | Pattern | What It Shows |
|---------|---------|---------------|
| DHH Rails Style | Simple reference | Style guide, conventions only |
| PDF Processing | Script-heavy | Bundled scripts, error handling |
| Git Commit Helper | Dynamic context | `!` commands, live git data |
| React Component | Task-oriented | Checklists, file creation workflow |
| Codebase Explorer | Agent-based | `context: fork`, subagent delegation |

### `references/advanced-skill-patterns.md` — 6 Advanced Patterns

| Pattern | When to Use |
|---------|-------------|
| Progressive Disclosure | SKILL.md getting too long; need on-demand loading |
| Bundled Scripts | Claude gets operations wrong or inconsistent |
| Workflow Branching | Skill handles different types of requests |
| Output Verification | Need to validate what Claude produced |
| Quality Philosophy | Output needs craftsmanship, not just correctness |
| Environmental Adaptation | Behavior varies by available tools/integrations |

### Sources (check before building)

| File | Purpose |
|------|---------|
| `sources/anthropic-skills.md` | Anthropic official skills repo — curated list to check first |
| `sources/README.md` | Overview of all sources for skills |
| `skills-catalog.json` | Local catalog of 200+ skills (at skill-creator root) |

### Other References

| File | Purpose |
|------|---------|
| `references/agent-skills-discovery-rfc.md` | Cloudflare RFC for `.well-known/skills/` discovery |
| `templates/skill-request.md` | Fillable form for requesting new skills |

## Getting Help

If you need help creating a skill:
1. Describe what you want the skill to do
2. Explain when it should be invoked
3. Share any scripts, docs, or examples you want to include
4. Claude will guide you through the creation process using this skill

---

**Remember:** Skills are just prompts. Keep them clear, focused, and actionable. Test in real usage and iterate based on feedback.
