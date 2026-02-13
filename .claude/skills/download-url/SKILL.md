---
name: download-url
description: Download web articles to PDF and Markdown. Supports single articles or entire documentation sites with automatic PDF combining. Use when user says "download url", "download article", "save this article", "download entire site", "get all pages", or provides URLs to save.
allowed-tools:
  - Read
  - Write
  - Bash
  - WebFetch
  - TodoWrite
user-invocable: true
---

# Download URL

Download web articles to PDF and Markdown format. Supports both single articles and multi-page documentation sites.

## Quick Start

**Single article:**
```
/download-url https://example.com/article
```

**Multi-page site (with combining):**
```
/download-url https://docs.example.com/guide/ --combine
```

Or in conversation: "download this article: [URL]"

## Instructions

### Single Article Workflow

1. **Get URL** from `$ARGUMENTS` or ask user for article URL

2. **Run download script:**
   ```bash
   uv run --script .claude/skills/download-url/scripts/download_article.py "<URL>"
   ```

3. **Check result** - script outputs JSON:
   ```json
   {
     "success": true,
     "title": "Article Title",
     "pdf_path": "downloads/articles/2026-02/article-title.pdf",
     "md_path": "downloads/articles/2026-02/article-title.md"
   }
   ```

4. **Report to user:**
   - On success: Share file paths as clickable links
   - On failure: Show error message and suggest alternatives

### Multi-Page/Documentation Workflow

When user requests downloading multiple related pages (e.g., "download all pages from this site", "get the complete documentation"):

1. **Identify the scope:**
   - Use WebFetch to explore the main page and find all subpages
   - Look for navigation menus, sitemap, or linked pages
   - Focus on pages from the same domain/section

2. **Download each page individually:**
   ```bash
   # Download each related page
   uv run --script .claude/skills/download-url/scripts/download_article.py "<URL1>"
   uv run --script .claude/skills/download-url/scripts/download_article.py "<URL2>"
   # ... continue for all pages
   ```

3. **Combine related PDFs:**
   ```bash
   # Combine PDFs matching a pattern
   uv run --script .claude/skills/download-url/scripts/combine_pdfs.py \
     --pattern "domain-name" \
     --output "downloads/articles/YYYY-MM/domain-complete.pdf" \
     --title "Site Name - Complete Documentation"
   ```

   **Important notes for combining:**
   - Only combine PDFs that are clearly related (same site/topic)
   - Use a descriptive pattern to avoid mixing unrelated content
   - The pattern is case-insensitive and matches partial filenames
   - Already-merged files (containing 'complete', 'merged', 'combined', 'collection') are automatically excluded

4. **Clean up (optional):**
   - After successful merge, optionally remove individual PDFs
   - Keep the markdown files for searchability

5. **Report results:**
   - Provide the merged PDF location
   - Note total pages and number of documents combined

## Output Location

Files are saved to `downloads/articles/YYYY-MM/` (gitignored top-level directory):
- `article-title.pdf` - Formatted PDF with images
- `article-title.md` - Clean Markdown for editing/searching
- `article-title_metadata.json` - Title, author, source URL, date

## Limitations

- **JavaScript-heavy sites** may not render fully (consider using browser if needed)
- **Paywalled content** will save only accessible portions
- **Very long articles** may take time to process

## Examples

### Single Article
```
/download-url https://blog.example.com/great-post
```

### Multi-Page Documentation

**User request:** "Download all pages from the Coefficient Giving Navigating Transformative AI fund"

**Process:**
1. Use WebFetch to find all related pages and subpages
2. Download each page individually
3. Combine with pattern matching:
   ```bash
   uv run --script .claude/skills/download-url/scripts/combine_pdfs.py \
     --pattern "coefficient-giving" \
     --output "downloads/articles/2026-02/coefficient-giving-complete.pdf" \
     --title "Coefficient Giving - Complete Documentation"
   ```
4. Report: "Combined 11 documents into coefficient-giving-complete.pdf (49 pages)"

### Pattern Matching Examples

| User Request | Pattern to Use | Notes |
|--------------|----------------|-------|
| "All OpenAI docs" | `--pattern "openai"` | Matches all PDFs with "openai" in name |
| "Today's downloads" | Check date folder | Look in `downloads/articles/YYYY-MM/` |
| "Anthropic papers" | `--pattern "anthropic"` | Case-insensitive matching |

### From Conversation
User: "Can you download this entire documentation site and combine it into one PDF?"
→ Identify scope, download all pages, combine with matching pattern
→ Return merged PDF path with summary

## Best Practices for Multi-Page Downloads

1. **Always check scope first** - Use WebFetch to understand site structure before mass downloading
2. **Group related content** - Download pages from the same section/topic together
3. **Use descriptive patterns** - Make patterns specific enough to avoid mixing unrelated PDFs
4. **Preserve individual files** - Keep markdown files even after combining PDFs for searchability
5. **Check for existing downloads** - Avoid re-downloading if files already exist (check by date)

## Workflow Decision Tree

```
User wants to download content
├─ Single article/page?
│  └─ Use single download workflow
└─ Multiple related pages?
   ├─ Same website/documentation?
   │  ├─ Use WebFetch to find all pages
   │  ├─ Download each individually
   │  └─ Combine with pattern matching
   └─ Different sources?
      └─ Download individually, don't combine

IMPORTANT: Only combine PDFs that are clearly related!
```

## Error Handling

| Error | Response |
|-------|----------|
| Invalid URL | "Please provide a valid URL starting with http:// or https://" |
| Network failure | "Could not reach the URL. Check your connection or try again." |
| No content extracted | "Could not extract article content. The site may require JavaScript." |
| No matching PDFs for pattern | "No PDFs found matching pattern. Check the pattern or download files first." |
| Merge failed | "Could not combine PDFs. Check that files are valid and accessible." |
