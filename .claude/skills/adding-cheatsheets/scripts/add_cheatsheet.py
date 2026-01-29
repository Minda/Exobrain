#!/usr/bin/env python3
"""
Add HTML cheatsheet to the cheatsheets folder with validation and enhancement.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Tuple
import html.parser
from html.parser import HTMLParser


class HTMLValidator(HTMLParser):
    """Basic HTML structure validator."""

    def __init__(self):
        super().__init__()
        self.has_doctype = False
        self.has_html = False
        self.has_head = False
        self.has_body = False
        self.has_title = False
        self.title_content = ""
        self.in_title = False
        self.h1_content = ""
        self.in_h1 = False

    def handle_decl(self, decl):
        if decl.lower().startswith('doctype'):
            self.has_doctype = True

    def handle_starttag(self, tag, attrs):
        if tag == 'html':
            self.has_html = True
        elif tag == 'head':
            self.has_head = True
        elif tag == 'body':
            self.has_body = True
        elif tag == 'title':
            self.has_title = True
            self.in_title = True
        elif tag == 'h1' and not self.h1_content:
            self.in_h1 = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'h1':
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title:
            self.title_content += data.strip()
        elif self.in_h1:
            self.h1_content += data.strip()


def validate_html(content: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate HTML structure and extract title.
    Returns: (is_complete, title, error_message)
    """
    validator = HTMLValidator()
    try:
        validator.feed(content)
    except html.parser.HTMLParseError as e:
        return False, "", f"HTML parse error: {e}"

    is_complete = all([
        validator.has_doctype,
        validator.has_html,
        validator.has_head,
        validator.has_body
    ])

    title = validator.title_content or validator.h1_content or "Untitled Cheatsheet"

    return is_complete, title, None


def wrap_partial_html(content: str, title: str = "Cheatsheet") -> str:
    """
    Wrap partial HTML content in a complete structure with dark theme.
    """
    # Check if it's already complete HTML
    is_complete, extracted_title, _ = validate_html(content)
    if is_complete:
        return content

    # Use extracted title if available
    if extracted_title and title == "Cheatsheet":
        title = extracted_title

    # Check if content has any HTML tags
    has_body_tag = '<body' in content.lower()
    has_head_tag = '<head' in content.lower()

    if has_body_tag and has_head_tag:
        # Just add DOCTYPE if missing
        if not content.strip().lower().startswith('<!doctype'):
            return f'<!DOCTYPE html>\n{content}'
        return content

    # Create full structure
    wrapped = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --text-primary: #e0e0e0;
            --text-secondary: #b0b0b0;
            --accent: #4a9eff;
            --border: #404040;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }}

        h1 {{ font-size: 2em; color: var(--accent); }}
        h2 {{ font-size: 1.5em; }}
        h3 {{ font-size: 1.25em; }}

        p {{
            margin-bottom: 16px;
        }}

        code {{
            background: var(--bg-secondary);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }}

        pre {{
            background: var(--bg-secondary);
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin-bottom: 16px;
            border: 1px solid var(--border);
        }}

        pre code {{
            background: none;
            padding: 0;
        }}

        a {{
            color: var(--accent);
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid var(--border);
        }}

        th {{
            background: var(--bg-secondary);
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background: rgba(255, 255, 255, 0.02);
        }}

        ul, ol {{
            margin-left: 24px;
            margin-bottom: 16px;
        }}

        li {{
            margin-bottom: 8px;
        }}

        blockquote {{
            border-left: 4px solid var(--accent);
            padding-left: 16px;
            margin: 16px 0;
            color: var(--text-secondary);
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>'''

    return wrapped


def generate_filename(title: str, base_path: Path) -> str:
    """
    Generate a kebab-case filename from title.
    """
    # Remove HTML tags if present
    title = re.sub(r'<[^>]+>', '', title)

    # Convert to lowercase and replace spaces/special chars with hyphens
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    filename = re.sub(r'[-\s]+', '-', filename)
    filename = filename.strip('-')

    # Ensure it has a name
    if not filename:
        filename = 'cheatsheet'

    # Add .html extension
    filename = f"{filename}.html"

    # Check for duplicates and add number if needed
    final_path = base_path / filename
    counter = 1
    while final_path.exists():
        name_part = filename.rsplit('.', 1)[0]
        filename = f"{name_part}-{counter}.html"
        final_path = base_path / filename
        counter += 1

    return filename


def update_index(cheatsheets_dir: Path, new_file: str, title: str):
    """
    Update the index.html file if it exists.
    """
    index_path = cheatsheets_dir / "index.html"
    if not index_path.exists():
        return

    # This would be more complex in reality - you'd parse the HTML
    # and insert the new entry properly. For now, we'll skip this.
    print(f"Note: You may want to manually update {index_path} to include {new_file}")


def main():
    parser = argparse.ArgumentParser(description='Add HTML cheatsheet to the collection')
    parser.add_argument('--input', '-i', help='Input HTML file or "-" for stdin')
    parser.add_argument('--output', '-o', help='Output filename (optional)')
    parser.add_argument('--title', '-t', help='Title for the cheatsheet')
    parser.add_argument('--wrap', action='store_true', help='Wrap partial HTML in complete structure')

    args = parser.parse_args()

    # Determine project root and cheatsheets directory
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[3]  # Go up to DigitalBrain root
    cheatsheets_dir = project_root / "cheatsheets"

    # Ensure cheatsheets directory exists
    cheatsheets_dir.mkdir(exist_ok=True)

    # Read input content
    if args.input == '-' or not args.input:
        content = sys.stdin.read()
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file {input_path} not found")
            sys.exit(1)
        content = input_path.read_text()

    # Validate and possibly wrap HTML
    is_complete, extracted_title, error = validate_html(content)

    if error:
        print(f"Warning: {error}")

    title = args.title or extracted_title or "Cheatsheet"

    if not is_complete or args.wrap:
        print(f"Wrapping partial HTML with complete structure...")
        content = wrap_partial_html(content, title)

    # Determine output filename
    if args.output:
        if args.output.endswith('.html'):
            filename = args.output
        else:
            filename = f"{args.output}.html"
        output_path = cheatsheets_dir / filename
    else:
        filename = generate_filename(title, cheatsheets_dir)
        output_path = cheatsheets_dir / filename

    # Check if file exists
    if output_path.exists():
        response = input(f"File {output_path.name} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)

    # Save the file
    output_path.write_text(content)
    print(f"✓ Saved cheatsheet to: {output_path.relative_to(project_root)}")
    print(f"  Title: {title}")
    print(f"  Size: {len(content):,} bytes")
    print(f"  Open in browser: file://{output_path}")

    # Update index if it exists
    update_index(cheatsheets_dir, filename, title)


if __name__ == '__main__':
    main()