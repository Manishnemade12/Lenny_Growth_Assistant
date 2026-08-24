"""Abstract base class interface for all LLM providers."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseLLMProvider(ABC):
    """Abstract interface for cloud and local LLM provider integrations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Model identifier name."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = True,
    ) -> AsyncGenerator[str, None]:
        """Stream or return generated content chunks from LLM."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector representation of text."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify provider service availability."""
        pass
