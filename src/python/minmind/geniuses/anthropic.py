"""Anthropic Claude implementation of Genius."""

import os
from typing import AsyncIterator

import anthropic

from .base import Genius, GeniusConfig, Message, Response


class AnthropicGenius(Genius):
    """Genius implementation using Anthropic's Claude."""

    def __init__(self, config: GeniusConfig, api_key: str | None = None):
        super().__init__(config)
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

    async def chat(self, messages: list[Message]) -> Response:
        """Send messages and get a response from Claude."""
        # Anthropic uses a different format - system prompt is separate
        system = self.config.system_prompt or ""
        api_messages = [{"role": m.role, "content": m.content} for m in messages]

        response = await self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=system,
            messages=api_messages,
        )

        return Response(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """Stream a response from Claude token by token."""
        system = self.config.system_prompt or ""
        api_messages = [{"role": m.role, "content": m.content} for m in messages]

        async with self.client.messages.stream(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=system,
            messages=api_messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
