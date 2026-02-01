---
name: writing-adding-footnotes
description: Add footnotes to an article, converting inline links to numbered references or adding new citations. Preserves original text while adding scholarly apparatus. Use when user says "add footnotes," "add citations," or "convert to footnotes."
allowed-tools: [ToolSearch, mcp__notion__notion-search, mcp__notion__notion-fetch, mcp__notion__notion-update-page, Read, Edit, WebSearch]
---

# Writing: Adding Footnotes

Add footnotes and citations to existing writing while preserving the original voice.

## Core Principle

**Preserve original phrasing wherever possible.** Footnotes are additive—they support the text, not replace it. Never rewrite the user's sentences to accommodate citations. The footnote apparatus should be invisible to the reading flow.

## Quick Start

1. Ask for the article location
2. Fetch content
3. Identify claims that need sources
4. Search and verify each claim
5. Add footnotes in consistent style
6. Generate footnotes section at end

## Instructions

### Step 1: Get the Article

Ask: *"Which article needs footnotes?"*

Accept:
- Notion page URL or title
- File path
- Pasted content

### Step 2: Identify What Needs Citing

Scan for:
- Factual claims (dates, numbers, quotes)
- References to external work
- `[needs source]` or `[] verify` tags
- Attributed quotes without links
- Claims that readers might question

### Step 3: Verify and Find Sources

For each claim:
1. Search web for authoritative source
2. Prefer primary sources (official announcements, papers, direct quotes)
3. Note publication date — prefer recent for current events
4. If claim cannot be verified, flag it: `[unverified]`

### Step 4: Add Footnotes

**Style A — Numbered (academic):**
```
The model achieves 95% accuracy on the benchmark.[^1]

[^1]: Smith et al., "Model Performance Study," 2026. https://example.com/paper
```

**Style B — Inline parenthetical:**
```
The model achieves 95% accuracy on the benchmark (Smith et al., 2026).
```

**Style C — Superscript with endnotes:**
```
The model achieves 95% accuracy on the benchmark.¹

---
¹ https://example.com/paper
```

Ask which style the user prefers, or default to **Style A** for Substack.

### Step 5: Generate Footnotes Section

At article end:

```markdown
---

## Notes

[^1]: Source description. [Link](url)
[^2]: Source description. [Link](url)
```

Or for simpler format:

```markdown
---

## Sources

1. [Title](url) — context
2. [Title](url) — context
```

## Footnote Content Guidelines

Each footnote should include:
- Author/organization (if known)
- Title or description
- Date (if relevant)
- URL

Keep footnote text minimal — readers shouldn't have to parse long footnotes.

## Anti-Patterns

❌ **Rewriting sentences to fit citations** — Add footnotes to existing text, don't restructure
❌ **Over-footnoting** — Not every sentence needs a citation; focus on contested or specific claims
❌ **Broken links** — Verify URLs work before adding
❌ **Paywalled sources without note** — Mark if source requires subscription

## Related Skills

- `writing-drafting-article` — Draft article from notes (uses inline links by default)
- `substack-writing` — Voice and style for Substack

## Example Interaction

**User:** Add footnotes to my draft article

**Claude:** Which article needs footnotes? Give me the Notion page or file path.

**User:** The "2026: Year We Become Better Operators" draft

**Claude:** *[Fetches content]*

I found 6 claims that could use sources:
1. Kimi K2.5 benchmark performance
2. Dario/Demis quotes from Davos
3. Agent harnesses trend
4. Claude constitution update
5. Multi-agent 17x error trap
6. Moltworker release

Some already have inline links. Want me to:
A) Convert existing inline links to footnotes + add missing sources
B) Only add footnotes for claims that don't have links yet
C) Something else?

**User:** A

**Claude:** Got it. Which footnote style do you prefer?
- Numbered `[^1]` with endnotes (academic)
- Superscript ¹ with endnotes (cleaner)
- Keep inline links, only add footnotes for new sources (hybrid)
