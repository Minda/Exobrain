---
name: download-url
description: Download web articles to PDF and Markdown. Use when user says "download url", "download article", "save this article", "convert to PDF", or provides a URL to save.
allowed-tools:
  - Read
  - Write
  - Bash
  - WebFetch
user-invocable: true
---

# Download URL

Download web articles to PDF and Markdown format.

## Quick Start

```
/download-url https://example.com/article
```

Or in conversation: "download this article: [URL]"

## Instructions

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

## Output Location

Files are saved to `downloads/articles/YYYY-MM/` (symlinked to `personal/downloads/articles/`):
- `article-title.pdf` - Formatted PDF with images
- `article-title.md` - Clean Markdown for editing/searching
- `article-title_metadata.json` - Title, author, source URL, date

Note: Downloads are stored in your private `personal/` directory.

## Limitations

- **JavaScript-heavy sites** may not render fully (consider using browser if needed)
- **Paywalled content** will save only accessible portions
- **Very long articles** may take time to process

## Examples

**Single article:**
```
/downloading-articles https://blog.example.com/great-post
```

**From conversation:**
User: "Can you save this article? https://medium.com/@author/interesting-topic"
→ Run the script, return file paths

## Error Handling

| Error | Response |
|-------|----------|
| Invalid URL | "Please provide a valid URL starting with http:// or https://" |
| Network failure | "Could not reach the URL. Check your connection or try again." |
| No content extracted | "Could not extract article content. The site may require JavaScript." |
