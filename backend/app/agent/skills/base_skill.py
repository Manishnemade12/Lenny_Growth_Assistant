"""Abstract base class for all agent skills."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from app.agent.providers.base import BaseLLMProvider


class BaseSkill(ABC):
    """Abstract interface defining an agent skill with intent detection and prompt execution."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill name identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human readable description of skill capabilities."""
        pass

    @property
    @abstractmethod
    def retrieval_top_k(self) -> int:
        """Number of transcript chunks to retrieve for this skill."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt template configured for this skill."""
        pass

    @abstractmethod
    def detect_intent(self, message: str) -> float:
        """Return confidence score (0.0 to 1.0) that message requires this skill."""
        pass

    @abstractmethod
    async def execute(
        self,
        query: str,
        context: list[dict],
        retrieved_chunks: list[dict],
        provider: BaseLLMProvider,
    ) -> AsyncGenerator[str, None]:
        """Execute the skill and stream output chunks."""
        pass
