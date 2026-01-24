# Skill Best Practices

Advanced patterns and practices for creating effective Claude Code skills.

## Writing Effective Descriptions

The description field is **critical** for automatic invocation. Claude uses it to decide when to invoke the skill.

### Anatomy of a Good Description

A good description has three components:

1. **What it does** - The capability
2. **When to use it** - The trigger context
3. **Specific keywords** - Terms users will say

#### Example: Bad Description

```yaml
description: A helpful skill for working with git
```

Problems:
- Too vague ("helpful")
- No trigger keywords
- Doesn't specify what git operations

#### Example: Good Description

```yaml
description: Expert guide for managing git worktrees. Use this when users want to create, switch, or manage parallel git working trees for feature development and experimentation.
```

Why it works:
- Specific capability: "managing git worktrees"
- Clear triggers: "create, switch, or manage"
- Keywords: "worktrees", "parallel", "feature development"

### Description Patterns

**Task-oriented:**
```yaml
description: Generate comprehensive commit messages based on git diff. Use when users want to commit changes and need help writing descriptive commit messages.
```

**Reference-oriented:**
```yaml
description: Rails development conventions and DHH style guide. Use when writing Rails code, making architectural decisions, or following Rails best practices.
```

**Tool-oriented:**
```yaml
description: Process and analyze spreadsheet data using pandas. Use when users need to read, transform, or analyze Excel/CSV files.
```

## Prompting Best Practices

### Be Direct and Imperative

❌ **Avoid:**
```markdown
You might want to consider checking if the file exists before proceeding.
```

✅ **Instead:**
```markdown
Check if the file exists before proceeding.
```

### Assume Claude is Smart

❌ **Avoid:**
```markdown
A git commit is a snapshot of your repository at a specific point in time. You should create commits to save your work. Commits have messages that describe what changed.
```

✅ **Instead:**
```markdown
Create a commit with a descriptive message following this format:
- First line: Brief summary (50 chars max)
- Blank line
- Detailed explanation of why (not what)
```

Claude already knows what a commit is. Only provide context Claude lacks.

### Provide Concrete Examples

❌ **Avoid:**
```markdown
Format the output appropriately.
```

✅ **Instead:**
```markdown
Format output as JSON:
\`\`\`json
{
  "status": "success",
  "data": [...],
  "timestamp": "2024-01-22T10:00:00Z"
}
\`\`\`
```

### Use Progressive Disclosure

Keep SKILL.md focused on immediate guidance. Move details to references:

**SKILL.md:**
```markdown
## API Authentication

Use the project's API key from `.env`. See `references/api-docs.md` for complete API documentation.
```

**references/api-docs.md:**
```markdown
# API Documentation

Complete details about authentication, endpoints, rate limits...
```

## Structuring Instructions

### Use Clear Hierarchy

```markdown
## Instructions

### Step 1: Gather Information
- Read configuration from `.env`
- Check git status
- Validate prerequisites

### Step 2: Process Data
- Parse input files
- Transform data
- Validate output

### Step 3: Generate Results
- Create report
- Save to output directory
- Display summary
```

### Provide Decision Criteria

```markdown
## Choosing the Right Approach

**Use Approach A when:**
- Files are under 1MB
- Data is structured (JSON, CSV)
- Fast processing is required

**Use Approach B when:**
- Files are large (>1MB)
- Data is unstructured (text, logs)
- Accuracy is more important than speed
```

### Handle Edge Cases Explicitly

```markdown
## Edge Cases

**No git repository:**
- Check if `.git` exists
- If not, ask user if they want to initialize one

**Uncommitted changes:**
- Show `git status`
- Ask if changes should be committed first

**Merge conflicts:**
- Do not attempt automatic resolution
- Display conflict files
- Guide user through manual resolution
```

## Using Scripts Effectively

### When to Use Scripts vs. Direct Commands

**Use scripts for:**
- Complex API interactions with auth
- Multi-step data transformations
- Parsing non-standard formats
- Stateful operations

**Use direct commands for:**
- Simple file operations
- Standard git operations
- Basic text processing

### Script Error Handling

Always provide clear error messages:

```python
#!/usr/bin/env python3
import sys

def process_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        print("Hint: Check that the path is correct and file exists.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied: {path}", file=sys.stderr)
        print("Hint: Check file permissions or run with appropriate access.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

### Script Output Format

Prefer structured output (JSON) for complex data:

```python
import json
import sys

result = {
    "status": "success",
    "files_processed": 42,
    "errors": [],
    "warnings": ["File foo.txt was skipped"]
}

print(json.dumps(result, indent=2))
```

This makes it easy for Claude to parse and use the results.

## Dynamic Context Patterns

### Injecting Git Information

```markdown
## Current Repository Status

!`git status --short`
!`git branch --show-current`

Based on the current branch and status above...
```

### Injecting File Contents

```markdown
## Configuration

!`cat config.json`

Using the configuration above, validate that...
```

### Injecting Command Results

```markdown
## Available Scripts

!`ls scripts/*.py`

These scripts are available for execution...
```

### Error Handling in `!` Commands

If a `!` command fails, its error output is included. Handle this gracefully:

```markdown
## Git Status

!`git status --short 2>&1 || echo "Not a git repository"`

If the output shows "Not a git repository", ask the user if they want to initialize git.
```

## Managing Skill Complexity

### Breaking Down Large Skills

If SKILL.md exceeds 500 lines, consider:

1. **Split into multiple skills** - Separate concerns
2. **Extract to references** - Move details to reference files
3. **Use skill hierarchy** - Create general + specialized skills

### Skill Composition

Create general skills that can invoke specialized skills:

**General skill: `git-workflow`**
```markdown
For worktree management, use `/git-worktree`
For commit message generation, use `/git-commit-helper`
```

**Specialized skills:**
- `git-worktree` - Worktree operations
- `git-commit-helper` - Commit message generation

### Conditional Complexity

Introduce complexity only when needed:

```markdown
## Quick Mode

For standard cases, follow these steps:
1. Simple step
2. Another simple step

## Advanced Mode

For complex cases (large files, special formats), see `references/advanced-usage.md`
```

## Testing Skills

### Manual Testing

1. **Direct invocation:**
   ```
   /skill-name arg1 arg2
   ```

2. **Conversational trigger:**
   - Use trigger keywords from description
   - Verify automatic invocation

3. **Edge cases:**
   - Missing files
   - Invalid input
   - Error conditions

### Validation Testing

```bash
python scripts/package_skill.py .claude/skills/skill-name --validate-only
```

This checks:
- Frontmatter validity
- Name conventions
- Description length
- File structure
- Common anti-patterns

### Integration Testing

Test the skill in realistic scenarios:

1. **Happy path** - Everything works as expected
2. **User errors** - Typos, wrong arguments
3. **System errors** - Missing files, permissions
4. **Complex scenarios** - Multi-step operations

## Naming Conventions

### Skill Names

Use **gerund form** (verb + -ing):

✅ **Good:**
- `processing-pdfs`
- `analyzing-logs`
- `generating-reports`
- `managing-worktrees`

❌ **Avoid:**
- `pdf-processor` (noun)
- `log-analyzer` (noun)
- `report-generator` (noun)
- `worktree-manager` (noun)

### File Names

Use **descriptive, lowercase names:**

✅ **Good:**
- `api-authentication.md`
- `common-patterns.md`
- `error-handling-guide.md`

❌ **Avoid:**
- `misc.md`
- `stuff.md`
- `README.md` (in references/)

### Script Names

Use **verb-noun format:**

✅ **Good:**
- `generate_report.py`
- `validate_config.sh`
- `process_data.py`

❌ **Avoid:**
- `helper.py`
- `utils.py`
- `script1.py`

## Common Anti-Patterns

### 1. XML Tags in Markdown

❌ **Don't:**
```markdown
<thinking>
I'll process this step by step...
</thinking>
```

✅ **Do:**
```markdown
Process this step by step:
1. First step
2. Second step
```

### 2. Vague Descriptions

❌ **Don't:**
```yaml
description: A helpful tool for development
```

✅ **Do:**
```yaml
description: Generate React components with TypeScript. Use when users want to create new components following project conventions.
```

### 3. Punting to Claude

❌ **Don't:**
```python
# Script that just prints instructions
print("Claude, please handle the error case")
```

✅ **Do:**
```python
# Script that handles errors
try:
    result = process()
except ValueError as e:
    print(f"Error: Invalid input - {e}", file=sys.stderr)
    sys.exit(1)
```

### 4. Time-Sensitive Language

❌ **Don't:**
```markdown
In 2024, the best practice is...
Currently, we recommend...
```

✅ **Do:**
```markdown
Historical pattern: Projects typically use...
The established pattern is...
```

### 5. Deeply Nested References

❌ **Don't:**
```
references/
└── advanced/
    └── patterns/
        └── authentication.md
```

✅ **Do:**
```
references/
└── authentication-patterns.md
```

### 6. Windows Paths

❌ **Don't:**
```markdown
C:\Users\Name\.claude\skills
```

✅ **Do:**
```markdown
.claude/skills
```

Use forward slashes for cross-platform compatibility.

## Version Control

### What to Commit

✓ Commit:
- `SKILL.md`
- `README.md`
- Scripts in `scripts/`
- References in `references/`
- Examples in `examples/`

✗ Don't commit:
- `.DS_Store`
- `__pycache__/`
- `*.pyc`
- Temporary files
- Large binary files

### Skill Evolution

Document changes in README.md:

```markdown
## Changelog

### v1.1.0 (2024-01-22)
- Added support for async operations
- Improved error messages
- Updated examples with new patterns

### v1.0.0 (2024-01-15)
- Initial release
```

## Distribution

### Packaging for Sharing

```bash
python scripts/package_skill.py .claude/skills/skill-name --output dist/
```

This creates `skill-name.zip` with:
- Validated structure
- All necessary files
- Ready for distribution

### Installing Packaged Skills

1. Download skill zip file
2. Extract to `.claude/skills/`
3. Restart Claude or reload skills
4. Test with `/skill-name`

### Sharing Best Practices

When sharing skills:
- Include a clear README
- Document prerequisites (Python version, dependencies)
- Provide usage examples
- List known limitations
- Include license information

## Maintenance

### Regular Reviews

Periodically review skills for:
- Outdated information
- Broken links or scripts
- Improved patterns discovered
- User feedback

### Deprecation

If deprecating a skill:
1. Update description with deprecation notice
2. Point to replacement skill
3. Keep functional for transition period
4. Eventually remove

```yaml
description: DEPRECATED - Use `new-skill-name` instead. This skill will be removed in the next release.
```

## Performance Considerations

### Skill Loading Time

Keep skills fast to load:
- SKILL.md under 500 lines
- Minimize `!` commands in frontmatter
- Lazy-load references

### Script Performance

Optimize scripts:
- Cache expensive operations
- Stream large files instead of reading all at once
- Use efficient algorithms
- Add progress indicators for long operations

### Context Size

Be mindful of context usage:
- Don't inject large files with `!` commands
- Summarize verbose output
- Use structured formats (JSON) over plain text

---

Following these best practices ensures your skills are:
- **Effective** - They do what they're supposed to do
- **Maintainable** - Easy to update and extend
- **User-friendly** - Clear and helpful for users
- **Performant** - Fast and efficient

Happy skill creating!
