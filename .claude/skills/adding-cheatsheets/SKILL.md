# Adding Cheatsheets Skill

Add HTML cheatsheets to your DigitalBrain project's cheatsheets folder. This skill helps you save, organize, and optionally enhance HTML reference pages.

## Trigger

Use this skill when:
- User provides HTML code for a cheatsheet
- User wants to save a reference page
- User asks to "add this cheatsheet" or "save this as a cheatsheet"
- User shares HTML documentation they want to preserve

## Process

### 1. Receive the HTML Content

First, get the HTML content from the user. They might:
- Paste the full HTML
- Provide a URL to fetch from
- Give you partial HTML that needs a basic structure

### 2. Validate and Process

Check the HTML for:
- Valid structure (DOCTYPE, html, head, body tags)
- Self-contained nature (inline CSS preferred)
- Title tag for naming the file

If the HTML is incomplete, wrap it in a basic structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Title from content or user]</title>
    <style>
        /* Basic dark theme styles if none provided */
    </style>
</head>
<body>
    [Content]
</body>
</html>
```

### 3. Determine the Filename

Generate filename from (in order of preference):
1. User-specified name
2. Title tag content
3. Main heading (h1) content
4. Ask the user

Format: `kebab-case.html` (e.g., `docker-commands.html`, `react-hooks-reference.html`)

### 4. Check for Duplicates

```bash
ls cheatsheets/*.html | grep -i "[similar-name]"
```

If a similar file exists, ask user if they want to:
- Replace the existing file
- Save with a different name
- Cancel the operation

### 5. Save the Cheatsheet

```python
# Use the provided script to save and process
python .claude/skills/adding-cheatsheets/scripts/add_cheatsheet.py \
    --input "content.html" \
    --output "cheatsheets/filename.html" \
    --title "Optional Title"
```

Or directly write:
```python
file_path = "cheatsheets/[filename].html"
# Write the HTML content
```

### 6. Update the Index (if exists)

If `cheatsheets/index.html` exists, add an entry for the new cheatsheet.

### 7. Confirm Success & Public Sharing

Report back:
- Saved location: `cheatsheets/[filename].html`
- File size
- Whether it's viewable in browser
- Any enhancements made

### 8. Remind About Public Sharing (IMPORTANT)

**Always include this reminder:**

> **To make this cheatsheet publicly accessible:**
>
> Once you push this to GitHub, you can share it publicly using raw.githack.com:
>
> 1. Get the GitHub raw URL:
>    `https://raw.githubusercontent.com/[username]/[repo]/[branch]/cheatsheets/[filename].html`
>
> 2. Convert it using raw.githack.com:
>    - Go to https://raw.githack.com/
>    - Paste your raw GitHub URL
>    - Get the CDN URL for sharing
>
> Example:
> - GitHub raw: `https://raw.githubusercontent.com/yourusername/DigitalBrain/main/cheatsheets/exo-frontier-ai.html`
> - Public URL: `https://rawcdn.githack.com/yourusername/DigitalBrain/[commit-hash]/cheatsheets/exo-frontier-ai.html`
>
> The CDN URL will properly serve the HTML with correct MIME types and make it viewable as a webpage.

## Examples

### Example 1: Complete HTML Provided

User: "Add this cheatsheet about Git commands" [provides full HTML]

Response:
1. Validate the HTML structure ✓
2. Extract title: "Git Commands Reference"
3. Generate filename: `git-commands-reference.html`
4. Save to `cheatsheets/git-commands-reference.html`
5. "Saved your Git commands cheatsheet to `cheatsheets/git-commands-reference.html`. You can open it directly in your browser."
6. Include the raw.githack.com reminder for public sharing

### Example 2: Partial Content

User: "Save this CSS Grid cheatsheet" [provides only body content]

Response:
1. Wrap in full HTML structure with dark theme
2. Add mobile viewport and basic styling
3. Save as `css-grid-cheatsheet.html`
4. "Created a complete HTML cheatsheet with dark theme styling and saved to `cheatsheets/css-grid-cheatsheet.html`"

### Example 3: From URL

User: "Can you save this cheatsheet: [URL]"

Response:
1. Fetch the content using WebFetch
2. Extract and validate HTML
3. Ensure it's self-contained (inline any external CSS if needed)
4. Save with appropriate name
5. "Fetched and saved the cheatsheet to `cheatsheets/[name].html`. I've made it self-contained for offline viewing."

## Optional Enhancements

When saving, you can offer to:

1. **Add dark mode**: If the cheatsheet lacks dark theme
2. **Make responsive**: Add mobile viewport and responsive CSS
3. **Inline resources**: Convert external CSS/JS to inline
4. **Add navigation**: If multiple cheatsheets exist, add a back-to-index link
5. **Optimize size**: Minify CSS if very large

## File Organization

```
cheatsheets/
├── README.md              # Describes the collection
├── index.html            # Optional index page
├── git-commands.html     # Individual cheatsheets
├── docker-compose.html
├── react-hooks.html
└── ...
```

## Best Practices

1. **Keep it self-contained**: No external dependencies except fonts
2. **Use descriptive names**: Clear, searchable filenames
3. **Preserve attribution**: Keep original author credits
4. **Dark theme friendly**: Most developers prefer dark themes
5. **Mobile responsive**: Should work on all devices

## Error Handling

- If HTML is malformed: Attempt to fix or ask user for clarification
- If file exists: Always ask before overwriting
- If too large (>1MB): Warn user and suggest optimizations
- If contains external dependencies: Offer to inline them or warn about offline viewing

## Python Helper Script

The skill includes a helper script at `scripts/add_cheatsheet.py` that can:
- Validate HTML structure
- Add missing elements
- Inline external resources
- Generate appropriate filenames
- Update the index file