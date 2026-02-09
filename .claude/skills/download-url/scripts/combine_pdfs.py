# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pypdf",
# ]
# ///
"""
Combine multiple related PDFs into a single document with bookmarks.

Usage: python combine_pdfs.py --pattern "pattern" --output "output.pdf" [--title "Title"]

The pattern is used to identify related PDFs (e.g., all from the same domain).
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from pypdf import PdfWriter, PdfReader


def sanitize_title(filename: str) -> str:
    """Convert filename to readable title for bookmarks."""
    # Remove file extension
    title = Path(filename).stem

    # Remove common suffixes like "-coefficient-giving"
    common_suffixes = [
        "-coefficient-giving", "-anthropic", "-openai",
        "-google", "-microsoft", "-meta", "-amazon"
    ]
    for suffix in common_suffixes:
        if title.endswith(suffix):
            title = title[:-len(suffix)]

    # Convert kebab-case to title case
    title = title.replace("-", " ").title()

    return title


def merge_related_pdfs(pdf_paths: list[Path], output_path: Path, title: str = "Merged Document") -> dict:
    """Merge PDFs with bookmarks and metadata."""
    writer = PdfWriter()
    merged_files = []
    total_pages = 0
    current_page = 0

    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)

            # Get bookmark title from filename
            bookmark_title = sanitize_title(pdf_path.name)

            # Add all pages
            for page in reader.pages:
                writer.add_page(page)

            # Add bookmark for this section
            writer.add_outline_item(bookmark_title, current_page)

            merged_files.append({
                "filename": pdf_path.name,
                "pages": num_pages,
                "bookmark": bookmark_title
            })

            current_page += num_pages
            total_pages += num_pages

        except Exception as e:
            print(f"Warning: Could not process {pdf_path}: {e}", file=sys.stderr)
            continue

    if not merged_files:
        raise ValueError("No valid PDFs could be merged")

    # Add metadata
    writer.add_metadata({
        '/Title': title,
        '/Creator': 'DigitalBrain Multi-Page Download',
        '/Producer': 'pypdf',
        '/CreationDate': datetime.now().isoformat(),
        '/Subject': f'Combined {len(merged_files)} related documents'
    })

    # Write the merged PDF
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

    return {
        "output_path": str(output_path),
        "total_pages": total_pages,
        "files_merged": len(merged_files),
        "files": merged_files
    }


def find_related_pdfs(base_dir: Path, pattern: str) -> list[Path]:
    """Find PDFs matching a pattern (case-insensitive)."""
    pattern_lower = pattern.lower()
    pdf_files = []

    # Search in the base directory and subdirectories
    for pdf_path in base_dir.glob("**/*.pdf"):
        if pattern_lower in pdf_path.name.lower():
            # Exclude already-merged files
            if not any(x in pdf_path.name.lower() for x in ['-complete', '-merged', '-combined', '-collection']):
                pdf_files.append(pdf_path)

    # Sort by name for consistent ordering
    return sorted(pdf_files)


def group_pdfs_by_domain(pdf_files: list[Path]) -> dict[str, list[Path]]:
    """Group PDFs by their apparent domain/source."""
    groups = {}

    for pdf in pdf_files:
        # Try to extract domain from filename
        # Common patterns: domain-name-title.pdf
        parts = pdf.stem.split('-')

        # Look for common domain indicators
        domain_keywords = [
            'coefficient-giving', 'anthropic', 'openai', 'google',
            'microsoft', 'meta', 'amazon', 'arxiv', 'nature', 'science'
        ]

        domain = "misc"
        for keyword in domain_keywords:
            if keyword in pdf.stem.lower():
                domain = keyword
                break

        if domain not in groups:
            groups[domain] = []
        groups[domain].append(pdf)

    return groups


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Combine related PDFs')
    parser.add_argument('--pattern', required=True, help='Pattern to match PDF files')
    parser.add_argument('--output', required=True, help='Output PDF path')
    parser.add_argument('--title', default=None, help='Document title')
    parser.add_argument('--base-dir', default='downloads/articles', help='Base directory to search')

    args = parser.parse_args()

    try:
        base_dir = Path(args.base_dir)
        output_path = Path(args.output)

        # Find related PDFs
        pdf_files = find_related_pdfs(base_dir, args.pattern)

        if not pdf_files:
            print(json.dumps({
                "success": False,
                "error": f"No PDFs found matching pattern: {args.pattern}"
            }))
            return 1

        # Use provided title or generate from pattern
        title = args.title or f"{args.pattern.replace('-', ' ').title()} - Complete Collection"

        # Merge the PDFs
        result = merge_related_pdfs(pdf_files, output_path, title)

        print(json.dumps({
            "success": True,
            "message": f"Successfully merged {result['files_merged']} PDFs",
            **result
        }))
        return 0

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        return 1


if __name__ == "__main__":
    sys.exit(main())