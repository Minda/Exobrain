# Skill Examples

Real-world examples of effective Claude Code skills from the compound engineering plugin and best practices.

## Example 1: Simple Reference Skill

**Use case:** Provide style guide for writing code in a specific framework

### dhh-rails-style/SKILL.md

```yaml
---
name: dhh-rails-style
description: Rails development conventions following DHH's style guide. Use when writing Rails code, making architectural decisions, or reviewing Rails applications.
---
```

```markdown
# DHH Rails Style Guide

Write Rails applications following David Heinemeier Hansson's architectural principles and conventions.

## Core Principles

### Omakase Philosophy
Rails is "omakase" - accept the chef's choice of defaults and conventions.

### Convention Over Configuration
- Follow Rails conventions without extensive configuration
- Use standard directory structure
- Embrace Rails magic over explicit wiring

### Majestic Monolith
- Prefer monolithic architecture over microservices
- Keep related code together
- Split only when necessary (rarely)

## Code Style

### Models
- Fat models, skinny controllers
- Business logic belongs in models
- Use concerns for shared behavior

### Controllers
- One action per concern
- Avoid complex conditional logic
- Delegate to models

### Views
- Use partials liberally
- Keep templates simple
- Prefer helper methods over view logic

## File Organization

Follow Rails conventions:
- `app/models/` - Domain models
- `app/controllers/` - HTTP interface
- `app/views/` - Templates
- `app/helpers/` - View helpers
- `lib/` - Custom libraries
- `config/` - Configuration

## Testing

- Write tests, but don't obsess over coverage
- System tests for critical paths
- Unit tests for complex logic
- Integration tests for workflows

For more details, see `references/rails-patterns.md`
```

**Why this works:**
- Clear, focused guidance
- Specific conventions
- Not too long (could fit much more detail)
- References for deeper info

---

## Example 2: Script-Heavy Skill

**Use case:** Process complex data formats with Python

### processing-pdfs/SKILL.md

```yaml
---
name: processing-pdfs
description: Extract text, tables, and images from PDF files. Use when users need to read, parse, or analyze PDF documents.
allowed-tools: [Bash, Read, Write]
---
```

```markdown
# PDF Processing

Extract and analyze content from PDF files using specialized tools.

## Quick Start

To process a PDF:
```
/processing-pdfs path/to/file.pdf
```

## What This Skill Does

1. Extracts text content
2. Identifies and extracts tables
3. Locates images and metadata
4. Outputs structured JSON

## Usage

### Extract Text Only

```bash
python scripts/extract_text.py input.pdf
```

### Extract Tables

```bash
python scripts/extract_tables.py input.pdf --format csv
```

### Full Analysis

```bash
python scripts/analyze_pdf.py input.pdf --output report.json
```

## Output Format

All scripts output JSON for easy parsing:

\`\`\`json
{
  "file": "document.pdf",
  "pages": 42,
  "text": "...",
  "tables": [...],
  "images": [...],
  "metadata": {...}
}
\`\`\`

## Error Handling

**Encrypted PDFs:**
```bash
python scripts/extract_text.py secure.pdf --password <password>
```

**Scanned PDFs (OCR):**
```bash
python scripts/extract_text.py scanned.pdf --ocr
```

## Requirements

Requires Python packages:
- pypdf2
- pdfplumber
- pytesseract (for OCR)

Install with: `pip install pypdf2 pdfplumber pytesseract`

## Examples

See `examples/pdf-extraction.md` for detailed examples.
```

**Why this works:**
- Clear entry point (Quick Start)
- Multiple usage modes
- Structured output
- Error handling documented
- Prerequisites listed

---

## Example 3: Dynamic Context Skill

**Use case:** Generate commit messages based on current git diff

### git-commit-helper/SKILL.md

```yaml
---
name: git-commit-helper
description: Generate comprehensive commit messages based on git diff analysis. Use when creating commits and needing help writing descriptive messages.
allowed-tools: [Bash, Read]
---
```

```markdown
# Git Commit Message Helper

Generate clear, descriptive commit messages following conventional commit format.

## Current Changes

!`git diff --cached --stat`
!`git diff --cached`

## Instructions

Based on the staged changes shown above:

1. **Analyze the changes:**
   - What files were modified?
   - What is the nature of changes? (feat, fix, refactor, docs, etc.)
   - What is the scope? (component, module, or file affected)

2. **Determine commit type:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

3. **Write the commit message:**

```
<type>(<scope>): <short description>

<detailed explanation of why this change was made>

<footer with breaking changes or issue references>
```

## Format

**Subject line (first line):**
- Max 50 characters
- Lowercase after colon
- No period at end
- Imperative mood: "add feature" not "added feature"

**Body (optional):**
- Wrap at 72 characters
- Explain WHY, not what (the diff shows what)
- Reference issues: "Fixes #123"

**Footer (optional):**
- Breaking changes: "BREAKING CHANGE: description"
- Issue references: "Closes #456"

## Examples

```
feat(auth): add OAuth2 login flow

Implemented Google OAuth2 authentication to allow users to sign in
with their Google accounts. This provides a more streamlined login
experience and reduces password management burden.

Closes #234
```

```
fix(api): handle null response from user service

Added null check before accessing user data to prevent NPE when
the user service returns null for deleted accounts.

Fixes #567
```

## Guidelines

**Do:**
- Focus on the "why" not the "what"
- Be specific about what changed
- Reference related issues
- Use conventional commit format

**Don't:**
- Write vague messages like "updates" or "fixes"
- Exceed line length limits
- Include implementation details in subject
- Forget to stage changes first
```

**Why this works:**
- Uses `!` commands to inject current git state
- Provides clear format guidelines
- Concrete examples
- Do/Don't guidelines
- Works with current repository state

---

## Example 4: Task-Oriented Skill

**Use case:** Guide through creating a new React component

### creating-react-components/SKILL.md

```yaml
---
name: creating-react-components
description: Generate React components following project conventions. Use when users want to create new functional components with TypeScript and testing.
allowed-tools: [Read, Write, Bash, Glob]
---
```

```markdown
# Creating React Components

Create React functional components following this project's conventions.

## Component Creation Checklist

When creating a new component:

### 1. Understand Requirements
- What is the component's purpose?
- What props does it need?
- What state will it manage?
- Are there sub-components needed?

### 2. Check Project Structure

!`ls -la src/components/`

Determine where the component should live based on existing structure.

### 3. Create Component Files

For a component named `UserProfile`, create:

```
src/components/UserProfile/
├── UserProfile.tsx          # Main component
├── UserProfile.test.tsx     # Tests
├── UserProfile.module.css   # Styles (if using CSS modules)
├── index.ts                 # Re-export
└── types.ts                 # TypeScript types (if complex)
```

### 4. Component Template

\`\`\`tsx
import React from 'react';
import styles from './UserProfile.module.css';
import { UserProfileProps } from './types';

export const UserProfile: React.FC<UserProfileProps> = ({
  name,
  email
}) => {
  return (
    <div className={styles.container}>
      <h2>{name}</h2>
      <p>{email}</p>
    </div>
  );
};
\`\`\`

### 5. TypeScript Types

\`\`\`tsx
export interface UserProfileProps {
  name: string;
  email: string;
  avatar?: string;
  onUpdate?: (data: UserData) => void;
}
\`\`\`

### 6. Write Tests

\`\`\`tsx
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('renders user name and email', () => {
    render(<UserProfile name="John" email="john@example.com" />);
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
});
\`\`\`

### 7. Export from index

\`\`\`tsx
export { UserProfile } from './UserProfile';
export type { UserProfileProps } from './types';
\`\`\`

## Project Conventions

**Check for:**
- ESLint configuration: `cat .eslintrc.json`
- Prettier settings: `cat .prettierrc`
- Testing setup: Check `package.json` for test framework

**Follow:**
- Use functional components (not classes)
- Use TypeScript for all components
- Include prop types and interfaces
- Write tests for public API
- Use CSS modules for styling (if that's the pattern)

## After Creation

1. **Import and use:**
   ```tsx
   import { UserProfile } from '@/components/UserProfile';
   ```

2. **Run tests:**
   ```bash
   npm test -- UserProfile
   ```

3. **Lint:**
   ```bash
   npm run lint
   ```

## Common Patterns

### With State
\`\`\`tsx
const [count, setCount] = useState(0);
\`\`\`

### With Effect
\`\`\`tsx
useEffect(() => {
  // side effect
  return () => {
    // cleanup
  };
}, [dependencies]);
\`\`\`

### With Context
\`\`\`tsx
const theme = useContext(ThemeContext);
\`\`\`

## Reference

See `references/react-patterns.md` for advanced patterns and hooks usage.
```

**Why this works:**
- Step-by-step checklist
- Concrete code templates
- Adapts to project structure
- Includes testing
- Follows best practices

---

## Example 5: Agent-Based Skill

**Use case:** Comprehensive codebase exploration

### exploring-codebase/SKILL.md

```yaml
---
name: exploring-codebase
description: Comprehensive codebase analysis and exploration. Use when users need to understand code structure, find patterns, or analyze architecture.
agent: Explore
context: fork
---
```

```markdown
# Codebase Explorer

Analyze and understand codebase structure, patterns, and architecture.

## What This Does

This skill uses a specialized Explore agent to:
- Find files by patterns
- Search code for keywords
- Analyze project structure
- Identify common patterns
- Map dependencies

## Usage Modes

### Quick Exploration
Find files and basic structure
```
/exploring-codebase quick
```

### Medium Exploration
Include code analysis and patterns
```
/exploring-codebase medium
```

### Deep Exploration
Comprehensive analysis with dependencies
```
/exploring-codebase thorough
```

## What Gets Analyzed

1. **Project Structure**
   - Directory organization
   - Module boundaries
   - File naming patterns

2. **Code Patterns**
   - Common abstractions
   - Architectural patterns
   - Error handling approaches

3. **Dependencies**
   - Import/export relationships
   - Third-party dependencies
   - Internal module coupling

4. **Configuration**
   - Build system
   - Environment setup
   - Deployment configuration

## Output Format

Results are presented as:
- **Summary** - High-level findings
- **Structure** - Directory tree and organization
- **Patterns** - Common patterns identified
- **Insights** - Recommendations and observations

## When to Use

**Use this skill when:**
- Starting work on a new codebase
- Looking for specific functionality
- Planning refactoring
- Understanding architecture
- Onboarding new developers

**Don't use for:**
- Simple file finds (use Glob instead)
- Single keyword searches (use Grep instead)
- Reading specific known files (use Read instead)

## Examples

See `examples/exploration-reports.md` for sample outputs.
```

**Why this works:**
- Delegates to specialized agent
- Clear usage modes
- Explains what gets analyzed
- Guidance on when (and when not) to use
- Isolated context prevents pollution

---

## Key Patterns Across Examples

### 1. Clear Purpose
Every skill has a focused, specific purpose.

### 2. Progressive Disclosure
Basic info in SKILL.md, details in references.

### 3. Actionable Instructions
Tell Claude exactly what to do, step by step.

### 4. Concrete Examples
Show don't tell - provide real code/output.

### 5. Error Handling
Document common issues and solutions.

### 6. Context-Aware
Use `!` commands to adapt to current state.

### 7. Tool Access
Request only the tools actually needed.

---

## Creating Your Own

When creating a skill, ask:

1. **What's the core capability?**
   - Be specific
   - One skill, one purpose

2. **When should it trigger?**
   - What keywords indicate it's needed?
   - Manual only or auto-invoke?

3. **What components does it need?**
   - Scripts for deterministic tasks?
   - References for detailed docs?
   - Examples for concrete guidance?

4. **How will users invoke it?**
   - `/skill-name` for manual
   - Conversational for auto

5. **What are the edge cases?**
   - Missing files?
   - Invalid input?
   - System errors?

Start simple, then enhance based on real usage.

---

These examples demonstrate different skill patterns. Mix and match to create skills that fit your needs.
