"""Article summarization with personalized prompting."""

from typing import AsyncIterator

from pydantic import BaseModel

from ..geniuses import Genius, GeniusConfig, Message
from .extractor import ExtractedArticle


# Default prompt for article summarization
DEFAULT_SUMMARY_PROMPT = '''Summarize this article for someone who learns by understanding the "why" first, then concrete examples.

Structure your summary as:
1. **Core Insight** - The fundamental idea or thesis (1-2 sentences)
2. **Why It Matters** - Context and significance 
3. **Key Points** - Bullet points of main arguments/findings
4. **Concrete Examples** - Specific examples or case studies mentioned
5. **Actionable Takeaways** - What can be applied immediately

Keep the tone conversational but precise. Focus on signal over noise.'''


class Summary(BaseModel):
    """A generated summary with metadata."""

    content: str
    model: str
    prompt_used: str
    tokens_used: int | None = None


class SummaryConfig(BaseModel):
    """Configuration for summarization."""

    system_prompt: str = DEFAULT_SUMMARY_PROMPT
    max_tokens: int = 2048
    temperature: float = 0.5


class ArticleSummarizer:
    """Summarizes articles using AI with configurable prompting.

    Supports:
    - Global style preferences (via system_prompt in config)
    - Per-article customization
    - Interactive refinement
    """

    def __init__(self, genius: Genius):
        """Initialize with a Genius instance.

        Args:
            genius: The AI provider to use for summarization
        """
        self.genius = genius

    async def summarize(
        self,
        article: ExtractedArticle,
        config: SummaryConfig | None = None,
    ) -> Summary:
        """Generate a summary for an article.

        Args:
            article: The extracted article to summarize
            config: Optional configuration (uses defaults if not provided)

        Returns:
            Summary with generated content and metadata
        """
        config = config or SummaryConfig()

        # Update genius config with summary-specific settings
        original_prompt = self.genius.config.system_prompt
        self.genius.config.system_prompt = config.system_prompt
        self.genius.config.max_tokens = config.max_tokens
        self.genius.config.temperature = config.temperature

        try:
            # Build the user message with article content
            user_message = self._build_article_message(article)
            messages = [Message(role="user", content=user_message)]

            response = await self.genius.chat(messages)

            tokens = None
            if response.usage:
                tokens = response.usage.get("input_tokens", 0) + response.usage.get(
                    "output_tokens", 0
                )
                # Also check for OpenAI-style token naming
                if tokens == 0:
                    tokens = response.usage.get("prompt_tokens", 0) + response.usage.get(
                        "completion_tokens", 0
                    )

            return Summary(
                content=response.content,
                model=response.model,
                prompt_used=config.system_prompt,
                tokens_used=tokens,
            )
        finally:
            # Restore original prompt
            self.genius.config.system_prompt = original_prompt

    async def summarize_stream(
        self,
        article: ExtractedArticle,
        config: SummaryConfig | None = None,
    ) -> AsyncIterator[str]:
        """Stream a summary token by token.

        Args:
            article: The extracted article to summarize
            config: Optional configuration (uses defaults if not provided)

        Yields:
            String tokens as they are generated
        """
        config = config or SummaryConfig()

        original_prompt = self.genius.config.system_prompt
        self.genius.config.system_prompt = config.system_prompt
        self.genius.config.max_tokens = config.max_tokens
        self.genius.config.temperature = config.temperature

        try:
            user_message = self._build_article_message(article)
            messages = [Message(role="user", content=user_message)]

            async for token in self.genius.stream(messages):
                yield token
        finally:
            self.genius.config.system_prompt = original_prompt

    async def refine(
        self,
        article: ExtractedArticle,
        previous_summary: str,
        feedback: str,
        config: SummaryConfig | None = None,
    ) -> Summary:
        """Refine a summary based on user feedback.

        Args:
            article: The original article
            previous_summary: The summary to refine
            feedback: User's feedback on what to improve
            config: Optional configuration

        Returns:
            Refined summary
        """
        config = config or SummaryConfig()

        # Build a refinement prompt
        refinement_prompt = f"""You previously summarized an article. Here is your summary:

---
{previous_summary}
---

The user would like you to refine this summary based on their feedback:
"{feedback}"

Please provide an improved summary that addresses their feedback while maintaining the same structure."""

        original_prompt = self.genius.config.system_prompt
        self.genius.config.system_prompt = config.system_prompt
        self.genius.config.max_tokens = config.max_tokens
        self.genius.config.temperature = config.temperature

        try:
            messages = [
                Message(role="user", content=self._build_article_message(article)),
                Message(role="assistant", content=previous_summary),
                Message(role="user", content=refinement_prompt),
            ]

            response = await self.genius.chat(messages)

            tokens = None
            if response.usage:
                tokens = response.usage.get("input_tokens", 0) + response.usage.get(
                    "output_tokens", 0
                )
                if tokens == 0:
                    tokens = response.usage.get("prompt_tokens", 0) + response.usage.get(
                        "completion_tokens", 0
                    )

            return Summary(
                content=response.content,
                model=response.model,
                prompt_used=config.system_prompt,
                tokens_used=tokens,
            )
        finally:
            self.genius.config.system_prompt = original_prompt

    def _build_article_message(self, article: ExtractedArticle) -> str:
        """Build the user message containing article content.

        Args:
            article: The article to include

        Returns:
            Formatted message string
        """
        parts = [
            f"# {article.title}",
            f"Source: {article.url}",
        ]

        if article.metadata.author:
            parts.append(f"Author: {article.metadata.author}")

        if article.metadata.published_at:
            parts.append(f"Published: {article.metadata.published_at.strftime('%Y-%m-%d')}")

        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append(article.content)

        return "\n".join(parts)
