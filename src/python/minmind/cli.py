"""MinMind Python CLI - Called by the Rust CLI for AI operations."""

import argparse
import asyncio
import json
import os
import sys

from .articles import ArticleExtractor, ArticleSummarizer
from .articles.summarizer import SummaryConfig
from .geniuses import AnthropicGenius, GeniusConfig, OpenAIGenius


async def extract_article(url: str) -> dict:
    """Extract article content from a URL."""
    async with ArticleExtractor() as extractor:
        article = await extractor.extract(url)
        return {
            "url": article.url,
            "title": article.title,
            "content": article.content,
            "metadata": {
                "author": article.metadata.author,
                "published_at": (
                    article.metadata.published_at.isoformat()
                    if article.metadata.published_at
                    else None
                ),
                "site_name": article.metadata.site_name,
                "description": article.metadata.description,
                "image_url": article.metadata.image_url,
            },
        }


async def summarize_article(
    article_id: str,
    provider: str,
    prompt: str,
    db_path: str | None = None,
) -> dict:
    """Summarize an article using AI.
    
    This function reads the article from the database, summarizes it,
    and returns the summary.
    """
    # Import sqlite3 to read from the database
    import sqlite3
    
    db_path = db_path or os.environ.get("MINMIND_DB", os.path.expanduser("~/.minmind/minmind.db"))
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get article by ID (support partial ID matching)
    cursor.execute(
        "SELECT id, url, title, raw_content FROM articles WHERE id LIKE ?",
        (f"{article_id}%",)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError(f"Article not found: {article_id}")
    
    article_uuid, url, title, content = row
    
    # Create a fake ExtractedArticle for the summarizer
    from .articles.extractor import ExtractedArticle, SourceMetadata
    
    article = ExtractedArticle(
        url=url,
        title=title,
        content=content,
        metadata=SourceMetadata(),
    )
    
    # Create the Genius based on provider
    genius_config = GeniusConfig(
        model="claude-sonnet-4-20250514" if provider == "anthropic" else "gpt-4o",
        system_prompt=prompt,
        temperature=0.5,
        max_tokens=2048,
    )
    
    if provider == "anthropic":
        genius = AnthropicGenius(genius_config)
    elif provider == "openai":
        genius = OpenAIGenius(genius_config)
    else:
        raise ValueError(f"Unknown provider: {provider}")
    
    # Summarize
    summarizer = ArticleSummarizer(genius)
    summary_config = SummaryConfig(system_prompt=prompt)
    
    summary = await summarizer.summarize(article, summary_config)
    
    return {
        "summary": summary.content,
        "model": summary.model,
        "tokens_used": summary.tokens_used,
    }


def main():
    """Main entry point for the Python CLI."""
    parser = argparse.ArgumentParser(description="MinMind Python CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract article content")
    extract_parser.add_argument("url", help="URL to extract")
    
    # Summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize an article")
    summarize_parser.add_argument("article_id", help="Article ID to summarize")
    summarize_parser.add_argument("--provider", default="anthropic", help="AI provider")
    summarize_parser.add_argument("--prompt", required=True, help="System prompt")
    summarize_parser.add_argument("--db", help="Database path")
    
    args = parser.parse_args()
    
    try:
        if args.command == "extract":
            result = asyncio.run(extract_article(args.url))
            print(json.dumps(result))
        elif args.command == "summarize":
            result = asyncio.run(summarize_article(
                args.article_id,
                args.provider,
                args.prompt,
                args.db,
            ))
            print(json.dumps(result))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
