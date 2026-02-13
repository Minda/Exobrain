"""OpenAI implementation of Genius."""

import os
from typing import AsyncIterator

import openai

from .base import Genius, GeniusConfig, Message, Response


class OpenAIGenius(Genius):
    """Genius implementation using OpenAI's GPT models."""

    def __init__(self, config: GeniusConfig, api_key: str | None = None):
        super().__init__(config)
        self.client = openai.AsyncOpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY")
        )

    async def chat(self, messages: list[Message]) -> Response:
        """Send messages and get a response from GPT."""
        api_messages = self._build_messages(messages)

        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=api_messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        choice = response.choices[0]
        return Response(
            content=choice.message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            },
        )

    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """Stream a response from GPT token by token."""
        api_messages = self._build_messages(messages)

        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=api_messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
