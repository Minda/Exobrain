"""Article extraction from URLs using trafilatura."""

from datetime import datetime

import httpx
import trafilatura
from pydantic import BaseModel


class SourceMetadata(BaseModel):
    """Metadata about the article source."""

    author: str | None = None
    published_at: datetime | None = None
    site_name: str | None = None
    description: str | None = None
    image_url: str | None = None


class ExtractedArticle(BaseModel):
    """An article extracted from a URL."""

    url: str
    title: str
    content: str
    metadata: SourceMetadata


class ArticleExtractor:
    """Extracts clean article content from URLs using trafilatura."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
        )

    async def extract(self, url: str) -> ExtractedArticle:
        """Extract article content from a URL.

        Args:
            url: The URL to extract content from

        Returns:
            ExtractedArticle with title, content, and metadata

        Raises:
            httpx.HTTPError: If the request fails
            ValueError: If content extraction fails
        """
        # Fetch the HTML
        response = await self.client.get(url)
        response.raise_for_status()
        html = response.text

        # Extract content using trafilatura
        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=True,
        )

        if not content:
            raise ValueError(f"Could not extract content from {url}")

        # Extract metadata
        metadata_dict = trafilatura.extract_metadata(html)

        metadata = SourceMetadata()
        if metadata_dict:
            metadata = SourceMetadata(
                author=metadata_dict.author if hasattr(metadata_dict, "author") else None,
                site_name=metadata_dict.sitename if hasattr(metadata_dict, "sitename") else None,
                description=(
                    metadata_dict.description if hasattr(metadata_dict, "description") else None
                ),
                image_url=metadata_dict.image if hasattr(metadata_dict, "image") else None,
            )
            # Try to parse date
            if hasattr(metadata_dict, "date") and metadata_dict.date:
                try:
                    metadata.published_at = datetime.fromisoformat(metadata_dict.date)
                except (ValueError, TypeError):
                    pass

        # Get title - prefer metadata title, fall back to extraction
        title = "Untitled"
        if metadata_dict and hasattr(metadata_dict, "title") and metadata_dict.title:
            title = metadata_dict.title
        else:
            # Try to get title from first line if it looks like a heading
            first_line = content.split("\n")[0].strip()
            if len(first_line) < 200 and not first_line.endswith("."):
                title = first_line

        return ExtractedArticle(
            url=url,
            title=title,
            content=content,
            metadata=metadata,
        )

    async def extract_batch(self, urls: list[str]) -> list[ExtractedArticle | Exception]:
        """Extract multiple articles concurrently.

        Args:
            urls: List of URLs to extract

        Returns:
            List of ExtractedArticle objects or exceptions for failures
        """
        import asyncio

        async def safe_extract(url: str) -> ExtractedArticle | Exception:
            try:
                return await self.extract(url)
            except Exception as e:
                return e

        return await asyncio.gather(*[safe_extract(url) for url in urls])

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "ArticleExtractor":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
