"""Base class for Genius implementations."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from pydantic import BaseModel


class Message(BaseModel):
    """A message in a conversation."""

    role: str  # "user", "assistant", or "system"
    content: str


class Response(BaseModel):
    """A response from a Genius."""

    content: str
    model: str
    usage: dict | None = None


class GeniusConfig(BaseModel):
    """Configuration for a Genius."""

    model: str
    system_prompt: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096


class Genius(ABC):
    """Abstract base class for AI provider implementations."""

    def __init__(self, config: GeniusConfig):
        self.config = config

    @abstractmethod
    async def chat(self, messages: list[Message]) -> Response:
        """Send messages and get a response."""
        ...

    @abstractmethod
    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """Stream a response token by token."""
        ...

    def _build_messages(self, messages: list[Message]) -> list[dict]:
        """Build the message list with optional system prompt."""
        result = []
        if self.config.system_prompt:
            result.append({"role": "system", "content": self.config.system_prompt})
        result.extend([{"role": m.role, "content": m.content} for m in messages])
        return result
