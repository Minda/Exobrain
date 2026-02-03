---
name: committing-work
description: Commit changes to the correct GitHub repositories with readable, memorable commit messages. Use when user says "commit", "git commit", "commit my changes", or wants to save their work to git.
allowed-tools: [Read, Glob, Grep, Bash(git *), Bash(cd *), AskUserQuestion]
---

# Committing Work

**User's intent:** *"Make sure that all of the directories in the project make it into the correct github repository. Ensure that the git comment makes sense."*

This skill commits changes to the correct repositories with commit messages that are *"easy to read and remember what work was completed later."*

## Quick Start

1. Check both repos for changes (only commit those that have changes)
2. Review what changed in each
3. Draft commit messages
4. **Always** confirm with user before committing
5. Commit and return links

## Repository Structure

This project has TWO git repositories:

| Repository | Location | Remote | Contains |
|------------|----------|--------|----------|
| **PUBLIC** | `/Users/min/Documents/Projects/DigitalBrain/` | `github.com/Minda/DigitalBrain` | Framework, generic skills, templates |
| **PRIVATE** | `/Users/min/Documents/Projects/DigitalBrain/personal/` | `github.com/Minda/MindaMind` | Memories, drafts, personal skills, downloads |

## Instructions

### 1. Detect Changes

*"Intelligently detect which have changes and only commit those."*

```bash
# PUBLIC repo
cd /Users/min/Documents/Projects/DigitalBrain && git status --short

# PRIVATE repo
cd /Users/min/Documents/Projects/DigitalBrain/personal && git status --short
```

If neither has changes: "Nothing to commit in either repository."

### 2. Review Changes

For each repo with changes:

1. Run `git status` to see modified/added/deleted files
2. Run `git diff` to understand what changed — scroll through, take notes
3. Check `git log --oneline -5` to see recent commit style

**Flag potential issues** — *"skill flag this kind of thing"*:
- Files deleted in one repo and added in another (may have moved between repos)
- Unrelated changes bundled together (may need separate commits)
- Files that shouldn't be committed (secrets, large binaries)

### 3. Draft Commit Messages

**User's quality bar:** *"Single sentence that encapsulates the intent of the commit."*

**Format:** *"plain descriptive prose plus feat:, fix:, docs:"* — *"whatever helps keep the commit readable, memorable and concise"*

```
<type>: <description>

Co-Authored-By: Claude <name> <noreply@anthropic.com>
```

**Types:**
- `feat:` — new feature or capability
- `fix:` — bug fix
- `docs:` — documentation changes
- `refactor:` — restructuring without behavior change
- `chore:` — maintenance, cleanup, config

**Good examples:**
- `feat: Add committing-work skill for multi-repo commits`
- `docs: Update relational context with new permissions`
- `chore: Reorganize memory files into topic folders`

### 4. Confirm with User

*"Always check the statements and ask for user feedback first."*

Show:
1. Which repo(s) will be committed
2. Summary of files being committed
3. Proposed commit message(s)

Ask: "Does this look right? Any changes to the commit message?"

**Wait for approval before proceeding.**

### 5. Commit and Return

```bash
git add <specific files>
git commit -m "$(cat <<'EOF'
<type>: <description>

Co-Authored-By: Claude <name> <noreply@anthropic.com>
EOF
)"
```

After committing, return:
- Commit hash and message for each repo
- Note whether pushed or local-only

## Examples

**User:** "commit my changes"

**Claude:**
1. Checks both repos — finds changes in PRIVATE only
2. Reviews: 3 modified files in `memories/insights/`
3. Drafts: `docs: Add skill design patterns to insights`
4. Shows user and asks for confirmation
5. After approval, commits and returns hash

**User:** "/commit added the new PDF skill"

**Claude:**
1. Checks both repos — finds changes in PUBLIC
2. Reviews: new `skills/processing-pdfs/` directory
3. Uses user's hint in message: `feat: Add PDF processing skill`
4. Confirms with user, then commits

## Guidelines

| Always | Never |
|--------|-------|
| Confirm commit message with user first | Push to remote unless explicitly asked |
| Add specific files by name | Use `git add -A` or `git add .` |
| Create NEW commits | Amend unless explicitly requested |
| Flag files that moved between repos | Commit secrets (.env, credentials, API keys) |
| Match existing commit style | Skip the confirmation step |
