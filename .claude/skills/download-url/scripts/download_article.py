# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "beautifulsoup4",
#     "readability-lxml",
#     "weasyprint",
#     "markdownify",
# ]
# ///
"""
Download a web article to PDF and Markdown.

Usage: python download_article.py <URL> [--output-dir PATH]

Outputs JSON status to stdout (not the content itself).
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from readability import Document
from weasyprint import HTML


def sanitize_filename(title: str) -> str:
    """Convert title to kebab-case filename."""
    # Remove special characters, keep alphanumeric and spaces
    clean = re.sub(r"[^\w\s-]", "", title.lower())
    # Replace spaces with hyphens
    clean = re.sub(r"[\s_]+", "-", clean)
    # Remove multiple hyphens
    clean = re.sub(r"-+", "-", clean)
    # Trim and limit length
    return clean.strip("-")[:80]


def get_unique_filename(base_path: Path, filename: str, extension: str) -> str:
    """Generate unique filename, appending -1, -2, etc. if exists."""
    full_path = base_path / f"{filename}{extension}"
    if not full_path.exists():
        return filename

    counter = 1
    while True:
        new_filename = f"{filename}-{counter}"
        full_path = base_path / f"{new_filename}{extension}"
        if not full_path.exists():
            return new_filename
        counter += 1


def fetch_article(url: str) -> tuple[str, str]:
    """Fetch URL and return (html_content, final_url)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
    response.raise_for_status()
    return response.text, response.url


def extract_article(html: str, url: str) -> dict:
    """Extract article content using readability."""
    doc = Document(html)

    # Get the cleaned article HTML
    article_html = doc.summary()
    title = doc.title()

    # Parse for additional metadata
    soup = BeautifulSoup(html, "html.parser")

    # Try to find author
    author = None
    author_meta = soup.find("meta", attrs={"name": "author"})
    if author_meta:
        author = author_meta.get("content")

    # Try to find publish date
    publish_date = None
    for attr in ["article:published_time", "datePublished", "date"]:
        date_meta = soup.find("meta", attrs={"property": attr}) or soup.find("meta", attrs={"name": attr})
        if date_meta:
            publish_date = date_meta.get("content")
            break

    return {
        "title": title,
        "author": author,
        "publish_date": publish_date,
        "content_html": article_html,
        "source_url": url,
    }


def create_styled_html(article: dict) -> str:
    """Wrap article content in styled HTML for PDF generation."""
    title = article["title"]
    content = article["content_html"]
    source = article["source_url"]
    author = article.get("author") or "Unknown"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            font-size: 2em;
            margin-bottom: 0.5em;
            line-height: 1.2;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 2em;
            border-bottom: 1px solid #eee;
            padding-bottom: 1em;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        pre, code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        pre {{
            padding: 1em;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 3px solid #ccc;
            margin-left: 0;
            padding-left: 1em;
            color: #555;
        }}
        a {{
            color: #0066cc;
        }}
        .source {{
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid #eee;
            font-size: 0.8em;
            color: #888;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta">
        By {author}
    </div>
    {content}
    <div class="source">
        Source: <a href="{source}">{source}</a>
    </div>
</body>
</html>"""


def html_to_pdf(html: str, output_path: Path) -> None:
    """Convert HTML string to PDF."""
    HTML(string=html).write_pdf(output_path)


def html_to_markdown(html: str, title: str, source_url: str) -> str:
    """Convert article HTML to clean Markdown."""
    # Convert to markdown
    markdown = md(html, heading_style="atx", bullets="-")

    # Clean up extra whitespace
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    # Add header with metadata
    header = f"# {title}\n\nSource: {source_url}\n\n---\n\n"

    return header + markdown.strip()


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python download_article.py <URL> [--output-dir PATH]"
        }))
        return 1

    url = sys.argv[1]

    # Parse output directory
    output_base = Path("downloads/articles")
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_base = Path(sys.argv[idx + 1])

    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL")
    except Exception:
        print(json.dumps({
            "success": False,
            "error": "Please provide a valid URL starting with http:// or https://"
        }))
        return 1

    try:
        # Fetch the article
        html, final_url = fetch_article(url)

        # Extract content
        article = extract_article(html, final_url)

        if not article["content_html"] or len(article["content_html"]) < 100:
            print(json.dumps({
                "success": False,
                "error": "Could not extract article content. The site may require JavaScript or be paywalled."
            }))
            return 1

        # Create output directory with date
        date_dir = datetime.now().strftime("%Y-%m")
        output_dir = output_base / date_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        base_filename = sanitize_filename(article["title"])
        if not base_filename:
            base_filename = "article"

        filename = get_unique_filename(output_dir, base_filename, ".pdf")

        # Create styled HTML and convert to PDF
        styled_html = create_styled_html(article)
        pdf_path = output_dir / f"{filename}.pdf"
        html_to_pdf(styled_html, pdf_path)

        # Create Markdown
        markdown = html_to_markdown(
            article["content_html"],
            article["title"],
            article["source_url"]
        )
        md_path = output_dir / f"{filename}.md"
        md_path.write_text(markdown, encoding="utf-8")

        # Save metadata
        metadata = {
            "title": article["title"],
            "author": article["author"],
            "publish_date": article["publish_date"],
            "source_url": article["source_url"],
            "downloaded_at": datetime.now().isoformat(),
            "pdf_file": f"{filename}.pdf",
            "markdown_file": f"{filename}.md",
        }
        metadata_path = output_dir / f"{filename}_metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        # Output success
        print(json.dumps({
            "success": True,
            "title": article["title"],
            "pdf_path": str(pdf_path),
            "md_path": str(md_path),
            "metadata_path": str(metadata_path),
        }))
        return 0

    except requests.exceptions.Timeout:
        print(json.dumps({
            "success": False,
            "error": "Request timed out. The server may be slow or unavailable."
        }))
        return 1
    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "success": False,
            "error": f"Could not fetch URL: {e}"
        }))
        return 1
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Unexpected error: {e}"
        }))
        return 1


if __name__ == "__main__":
    sys.exit(main())
